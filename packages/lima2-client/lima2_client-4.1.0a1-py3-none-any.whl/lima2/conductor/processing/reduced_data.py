# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Reduced data input/output mechanisms."""

import asyncio
from dataclasses import dataclass
import logging
import time
import traceback
from collections import namedtuple
from typing import Any, AsyncIterator, cast

import numpy as np
import numpy.typing as npt

from lima2.common.devencoded import structured_array
from lima2.common.exceptions import Lima2BackendError, Lima2NotFound
from lima2.common.types import ReducedDataSource, ScalarDataSource, VectorDataSource
from lima2.conductor.tango.processing import TangoProcessing
from lima2.conductor.topology import (
    FrameMapping,
    GlobalIdx,
    LocalIdx,
    LookupTable,
    ReceiverIdx,
)
from lima2.conductor.utils import Ticker, expand, naturalsize, warn_if_hanging

logger = logging.getLogger(__name__)

Roi = namedtuple("Roi", ())
Profile = namedtuple("Profile", ("length"))


FRAME_IDX_DTYPE = np.dtype(
    [
        ("recv_idx", np.int32),
        ("frame_idx", np.int32),
    ]
)


ROI_STATS_DTYPE = np.dtype(
    [
        ("frame_idx", np.int32),
        ("recv_idx", np.int32),
        ("min", np.float32),
        ("max", np.float32),
        ("avg", np.float32),
        ("std", np.float32),
        ("sum", np.float64),
    ]
)

ROI_PROFILES_DTYPE = np.dtype(
    [
        ("frame_idx", np.int32),
        ("recv_idx", np.int32),
        ("min", np.float32),
        ("max", np.float32),
        ("avg", np.float32),
        ("std", np.float32),
        ("sum", np.float64),
    ]
)


@dataclass
class RoiParams:
    rois: list[Roi]
    profiles: list[Profile]

    @staticmethod
    def from_dicts(
        roi_params: dict[str, Any] | None, profile_params: dict[str, Any] | None
    ) -> "RoiParams":
        """Interpret roi stats and roi profile param dicts to build a RoiParams."""
        rois: list[Roi] = []
        profiles: list[Profile] = []

        if roi_params and roi_params["enabled"]:
            for _ in roi_params["rect_rois"] + roi_params["arc_rois"]:
                rois.append(Roi())

        if profile_params and profile_params["enabled"]:
            for roi, direction in zip(
                profile_params["rois"], profile_params["directions"], strict=True
            ):
                if direction == "vertical":
                    profiles.append(Profile(length=roi["dimensions"]["y"]))
                elif direction == "horizontal":
                    profiles.append(Profile(length=roi["dimensions"]["x"]))
                else:
                    raise RuntimeError(
                        f"Invalid profile direction '{direction}'."
                    )  # pragma: no cover

        return RoiParams(rois=rois, profiles=profiles)


class EndLoop:
    """Signifies end of stream to a asyncio.Queue consumer."""


class ReducedDataFetcher:
    """Reduced data fetcher.

    Implements the schunks() iterator, which yields reduced data periodically
    popped from the processing devices.
    """

    def __init__(
        self,
        name: str,
        devices: list[TangoProcessing],
        source: ReducedDataSource,
        close_request: asyncio.Event,
        fetch_interval_s: float,
    ) -> None:
        self.name = name
        self.devices = devices
        self.source = source
        self.close_request = close_request
        self.fetch_interval_s = fetch_interval_s
        self.chunk_queue: asyncio.Queue[
            list[npt.NDArray[Any]] | EndLoop
        ] = asyncio.Queue()

    async def pop_decode_iteration(self, close_request: asyncio.Event) -> bool:
        """Pop and decode reduced data from all devices, return as a list"""
        chunk_shape = (-1, self.source.total_length())

        async def pop_decode_receiver(device: TangoProcessing) -> npt.NDArray[Any]:
            raw = await device.pop_reduced_data(self.source.getter_name)
            decoded = await asyncio.to_thread(
                structured_array.decode, raw_data=raw, dtype=self.source.src_dtype
            )
            return decoded.reshape(chunk_shape)

        raw_chunks = await asyncio.gather(
            *[pop_decode_receiver(device=device) for device in self.devices],
            return_exceptions=True,
        )
        errors = [chunk for chunk in raw_chunks if isinstance(chunk, BaseException)]
        if len(errors) > 0:
            # Error from any device -> signal end of datastream and interrupt the loop
            await self.chunk_queue.put(EndLoop())
            raise Lima2BackendError(
                f"Error fetching chunk for {self.name}:\n- "
                + "\n- ".join([str(error) for error in errors])
            )

        raw_chunks = cast(list[npt.NDArray[Any]], raw_chunks)

        if all([chunk.size == 0 for chunk in raw_chunks]) and close_request.is_set():
            logger.debug(f"Stopping '{self.name}' fetch task")
            await self.chunk_queue.put(EndLoop())
            return True  # Stop signal for Ticker

        await self.chunk_queue.put(raw_chunks)
        return False

    async def schunks(self) -> AsyncIterator[list[npt.NDArray[Any]]]:
        """Fetch and decode data popped from each device periodically.

        Yield chunks popped from each device as a list.
        """

        logger.info(f"Fetching task started for '{self.name}'")

        fetch_task = Ticker(
            interval_s=self.fetch_interval_s,
            callback=self.pop_decode_iteration,
            kwargs={"close_request": self.close_request},
            descr=f"pop_decode_iteration({self.name})",
        )
        fetch_task.start()

        while True:
            chunks = await self.chunk_queue.get()

            if type(chunks) is EndLoop:
                self.chunk_queue.task_done()
                break

            assert type(chunks) is list, f"{type(chunks)=}"

            empty = [chunk.size == 0 for chunk in chunks]

            if not all(empty):
                yield chunks

            self.chunk_queue.task_done()

        logger.info(f"Exited loop '{self.name}'")

        # Guarantee that all items have been processed
        assert (
            fetch_task.done()
        ), f"Exited the '{self.name}' schunks() loop while fetching task is running."

        if self.chunk_queue.qsize() > 0:
            raise RuntimeError(f"Chunk queue for '{self.name}' is not empty")
        await self.chunk_queue.join()

        logger.info(f"Chunk stream done for '{self.name}'")


class ReducedDataPipeline:
    """Pipeline for a reduced data source.

    Runs a ReducedDataFetcher as its data source, and stores the chunks in a
    frame-ordered buffer using the lookup table.

    Allows a consumer to stream chunks in contiguous frame order.
    """

    def __init__(
        self,
        name: str,
        size_hint: int,
        devices: list[TangoProcessing],
        close_request: asyncio.Event,
        source: ReducedDataSource,
        lookup: LookupTable,
        fetch_interval_s: float,
    ) -> None:
        self.name = name
        self.source = source
        self.devices = devices
        self.fetcher = ReducedDataFetcher(
            name=name,
            devices=devices,
            source=source,
            close_request=close_request,
            fetch_interval_s=fetch_interval_s,
        )
        self.lookup = lookup

        self.buffers = [
            np.empty(shape=(size_hint, *shape), dtype=dtype)
            for dtype, shape in source.stream_descriptions()
        ]
        for i, buf in enumerate(self.buffers):
            logger.debug(f"Allocated {naturalsize(buf.nbytes)} for '{name}[{i}]'")

        self.empty = np.full(fill_value=True, shape=size_hint, dtype=np.bool_)
        """Invalid/empty rows in the buffers."""

        self.consume_cond = asyncio.Condition()
        """Used by consumers to wake up when feed() writes to the buffer."""
        self.done_event = asyncio.Event()
        """Event set when the buffer is complete with all fetched chunks."""

    def __del__(self) -> None:
        logger.debug(f"ReducedDataPipeline instance for {self.name} destroyed")

    async def lookup_chunk(
        self, rcv_idx: ReceiverIdx, from_idx: LocalIdx, chunk: npt.NDArray[Any]
    ) -> npt.NDArray[GlobalIdx]:
        """Determine global frame indices for a chunk, given receiver index.

        Blocks the caller until the lookup is successful.
        """
        if chunk.size == 0:
            return np.array([], dtype=np.uint32)
        assert chunk.dtype == self.source.src_dtype
        assert len(chunk.shape) == 2, f"{chunk.shape}"
        assert chunk.shape[1] == self.source.total_length()

        # NOTE: this blocks the feed_loop until we know what indices
        # this chunk corresponds to. The pop() calls are still
        # occurring though, and new chunks just accumulate in the
        # queue.
        frame_indices: npt.NDArray[GlobalIdx] = await warn_if_hanging(
            self.lookup.wait_reverse_lookup(
                receiver_idx=rcv_idx,
                from_idx=LocalIdx(from_idx),
                num_frames=chunk.shape[0],
            ),
            warn_every_s=1.0,
        )

        # NOTE: this is just a sanity check for the reduced data fetching +
        # lookup mechanisms.
        # Will only work as long as the chunks have a "frame_idx" column
        truth, truth_idx = np.unique(chunk["frame_idx"], return_index=True)
        assert np.all(
            frame_indices == truth[truth_idx.argsort()]
        ), f"{frame_indices=} {truth[truth_idx.argsort()]=}"

        return frame_indices

    def store_chunk(
        self, indices: npt.NDArray[np.uint32], chunk: npt.NDArray[Any]
    ) -> None:
        """Split a chunk into its constituent channels and store in self.buffers.

        Automatically expands the buffers and empty list if required.
        """
        for i, subchunk in enumerate(self.source.split(chunk=chunk)):
            while np.any(indices >= self.buffers[i].shape[0]):
                self.buffers[i] = expand(self.buffers[i])
                logger.warning(
                    f"'{self.name}[{i}]' buffer has grown to {self.buffers[i].shape[0]}"
                    f" entries. Total size: {naturalsize(self.buffers[i].nbytes)}."
                )

            self.buffers[i][indices] = subchunk

        while np.any(indices >= self.empty.shape[0]):
            self.empty = expand(self.empty, fill_value=True)

        self.empty[indices] = False

    async def feed_loop(self) -> None:
        """Pull chunks from the reduced data fetcher to fill the buffer.

        Everytime new data comes in, notify all consumers.
        """

        cursors = [np.uint32(0) for _ in self.devices]

        try:
            async for chunks in self.fetcher.schunks():
                # One element per receiver
                assert len(chunks) == len(self.devices), f"{chunks}"

                # NOTE: this blocks the 'async for' loop until we know what
                # indices this chunk corresponds to. The fetcher is still
                # popping chunks though, and new chunks just accumulate in its
                # queue.
                indices: list[npt.NDArray[np.uint32]] = await asyncio.gather(
                    *[
                        self.lookup_chunk(
                            rcv_idx=ReceiverIdx(np.uint32(rcv_idx)),
                            from_idx=LocalIdx(cursors[rcv_idx]),
                            chunk=chunk,
                        )
                        for rcv_idx, chunk in enumerate(chunks)
                    ]
                )

                for i in range(len(self.devices)):
                    cursors[i] += indices[i].size

                self.store_chunk(
                    indices=np.concatenate(indices), chunk=np.concatenate(chunks)
                )

                # Now notify consumers: it is likely that a chunk of contiguous frames
                # can now be consumed.
                async with self.consume_cond:
                    self.consume_cond.notify_all()

            logger.debug(f"'{self.name}' schunks() finished ok")
        except Exception:
            logger.error(
                f"Error in '{self.name}' feed_loop(). {traceback.format_exc()}"
            )
            raise
        finally:
            # Signal end of feed to processing tasks
            logger.debug(f"Closing '{self.name}' feed")

            self.done_event.set()
            async with self.consume_cond:
                self.consume_cond.notify_all()

    async def consume(self, channel_idx: int) -> AsyncIterator[npt.NDArray[Any]]:
        """Consume a reduced data channel in global frame ordering.

        Yields chunks of contiguous reduced data.
        """
        at_idx = 0

        while True:
            if not np.any(self.empty):
                first_empty = self.empty.size
            else:
                first_empty = np.where(self.empty)[0][0]

            if first_empty > at_idx:
                yield self.buffers[channel_idx][at_idx:first_empty]
                at_idx = first_empty
            elif self.done_event.is_set():
                break
            else:
                # Done consuming but feed loop isn't done yet -> wait
                async with self.consume_cond:
                    await self.consume_cond.wait()

        logger.info(f"Consume '{self.name}[{channel_idx}]' done")


class ReducedData:
    """Reduced data handler.

    One ReducedData instance is created by the Pipeline instance at
    prepare-time, at which point all reduced data sources are identified.

    On prepare, ReducedDataPipeline instances are created for each source. These
    objects each manage the fetching and caching of one data source, and the
    resulting data streams are available via stream().

    On start, the ReducedDataPipeline tasks are created and the
    fetch-decode-cache loop runs for all data sources. When stream() is called,
    an async iterator is returned, which yields contiguous chunks of reduced
    data as the acquisition progresses.
    """

    def __init__(
        self,
        devices: list[TangoProcessing],
        size_hint: int,
        lookup: LookupTable,
        roi_params: RoiParams,
        static_sources: dict[str, ReducedDataSource],
        fetch_interval_s: float,
    ) -> None:
        self.devices = devices

        self.feed_tasks: set[asyncio.Task[None]] = set()

        self.pipelines: dict[str, ReducedDataPipeline] = {}

        self.close_request = asyncio.Event()
        """Set by the AcquisitionSystem when processing is done."""

        # Combine static reduced data sources (e.g. xpcs fill_factor) with dynamically
        # created rois to allocate all reduced data arrays.
        self.sources = static_sources.copy()

        # Roi stats and profiles are a special case: they correspond to a single
        # server-side source (popRoiStatistics) but can provide multiple reduced data
        # streams (roi_stats_0, roi_stats_1, ..., roi_profile_0, roi_profile_1, ...)

        # TODO|NOTE(mdu) we could avoid having to parse roi/profile params by adding a
        # server-side mechanism for querying the active reduced data streams
        if len(roi_params.rois) > 0:
            self.sources["roi_stats"] = ScalarDataSource(
                getter_name="popRoiStatistics",
                src_dtype=ROI_STATS_DTYPE,
                num_elements=len(roi_params.rois),
                channel_keys=["avg", "std", "min", "max", "sum"],
            )

        if len(roi_params.profiles) > 0:
            self.sources["roi_profile"] = VectorDataSource(
                getter_name="popRoiProfiles",
                src_dtype=ROI_STATS_DTYPE,
                lengths=[profile.length for profile in roi_params.profiles],
                channel_keys=["avg", "std", "min", "max", "sum"],
            )

        start = time.perf_counter()

        for name, source in self.sources.items():
            self.pipelines[name] = ReducedDataPipeline(
                name=name,
                size_hint=size_hint,
                devices=self.devices,
                close_request=self.close_request,
                source=source,
                lookup=lookup,
                fetch_interval_s=fetch_interval_s,
            )

        logger.debug(
            "Allocated reduced data buffers in "
            f"{(time.perf_counter() - start) * 1e3:.1f}ms."
        )
        logger.info(f"Ready to fetch reduced data for {list(self.pipelines.keys())}")

    def dynamic_index(self, fetch_interval_s: float) -> AsyncIterator[FrameMapping]:
        """Fetch the 'frame_idx' data to build a lookup table in dynamic dispatch."""
        fetcher = ReducedDataFetcher(
            name="frame_idx",
            devices=self.devices,
            source=ScalarDataSource(
                getter_name="popFrameIdx",
                src_dtype=FRAME_IDX_DTYPE,
                num_elements=1,
                channel_keys=["frame_idx"],
            ),
            close_request=self.close_request,
            fetch_interval_s=fetch_interval_s,
        )

        async def frame_idx_iterator() -> AsyncIterator[FrameMapping]:
            """Yields receiver index of the latest contiguous frame acquired."""
            try:
                cursors = [np.uint32(0) for _ in self.devices]
                async for chunks in fetcher.schunks():
                    for rcv_idx, chunk in enumerate(chunks):
                        for row in chunk:
                            yield FrameMapping(
                                receiver_idx=ReceiverIdx(np.uint32(rcv_idx)),
                                local_idx=LocalIdx(cursors[rcv_idx]),
                                frame_idx=row["frame_idx"],
                            )
                            cursors[rcv_idx] += 1
            except Exception:
                logger.error(f"{traceback.format_exc()}")

            logger.info("frame_idx_iterator() done")

        return frame_idx_iterator()

    def start(self) -> None:
        """Start the reduced data pipeline for each data source."""
        if len(self.feed_tasks) > 0:
            raise RuntimeError("Reduced data feed tasks already started")

        for name, pipeline in self.pipelines.items():
            logger.debug(f"Starting feed task for {name}")

            task = asyncio.create_task(pipeline.feed_loop(), name=f"{name} feed")

            self.feed_tasks.add(task)

    async def close(self) -> None:
        """Notify end of processing to feed tasks and join."""
        # NOTE: this event is picked up by all ReducedDataFetchers to
        # stop their fetching loop.
        self.close_request.set()

        results = await asyncio.gather(*self.feed_tasks, return_exceptions=True)
        failed_tasks = [
            task.get_name()
            for task, res in zip(self.feed_tasks, results, strict=True)
            if isinstance(res, BaseException)
        ]
        if len(failed_tasks) > 0:
            logger.warning(
                "Some reduced data feeding tasks didn't complete (errors above):\n- "
                + "\n- ".join([name for name in failed_tasks])
            )

        self.feed_tasks.clear()

        logger.info("Joined all reduced data feed tasks 👌👌")

    def channel_info(self) -> dict[str, list[tuple[np.dtype[Any], tuple[int, ...]]]]:
        return {
            key: pipeline.source.stream_descriptions()
            for key, pipeline in self.pipelines.items()
        }

    def stream(self, name: str, channel_idx: int) -> AsyncIterator[npt.NDArray[Any]]:
        """Get a reduced data stream by name and index.

        Multiple clients may request the same reduced data stream, therefore
        this returns a new, independent generator every time it is called.

        Raises:
          Lima2NotFound: no reduced data stream of that name or index.
        """
        if name not in self.pipelines:
            raise Lima2NotFound(
                f"No reduced data channel named '{name}'. "
                f"Have {list(self.pipelines.keys())}."
            )

        if channel_idx >= len(self.pipelines[name].buffers):
            raise Lima2NotFound(
                f"Reduced data channel '{name}' has no channel with index {channel_idx} "
                f"(number of channels is {len(self.pipelines[name].buffers)})."
            )

        logger.debug(f"Consumer registered for {name}[{channel_idx}]")
        return self.pipelines[name].consume(channel_idx=channel_idx)
