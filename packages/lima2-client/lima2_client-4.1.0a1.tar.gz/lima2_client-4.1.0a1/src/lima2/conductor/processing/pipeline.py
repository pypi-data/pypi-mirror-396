# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 pipeline base class.

An instance of Pipeline represents one processing pipeline, possibly distributed across
multiple Lima2 receivers. The processing is assumed to be the same across all receivers.

It has knowledge of the topology, and therefore can fetch a frame given a global
frame index, and provide aggregated progress counters during/after an acquisition.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, AsyncIterator
from uuid import UUID

import numpy as np
import numpy.typing as npt

from lima2.common import progress_counter
from lima2.common.exceptions import Lima2LookupError, Lima2NotFound
from lima2.common.progress_counter import ProgressCounter, SingleCounter
from lima2.common.types import FrameInfo, FrameSource, ReducedDataSource
from lima2.conductor.processing.master_file import (
    FrameSavingChannel,
    MasterFileGenerator,
    MasterFileMetadata,
    SavingParams,
)
from lima2.conductor.processing.reduced_data import ReducedData, RoiParams
from lima2.conductor.tango.container import TangoProcessingGroup
from lima2.conductor.tango.processing import TangoProcessing
from lima2.conductor.topology import (
    DynamicDispatch,
    FrameMapping,
    GlobalIdx,
    LocalIdx,
    LookupTable,
    ReceiverIdx,
    RoundRobin,
    SingleReceiver,
)

logger = logging.getLogger(__name__)


async def single_receiver_frame_iterator(
    device: TangoProcessing,
    fetch_interval_s: float,
    stop_evt: asyncio.Event,
) -> AsyncIterator[FrameMapping]:
    num_frames = np.uint32(0)

    while True:
        # NOTE(mdu) nb_frames_source is present on all pipelines (cuda,
        # failing, legacy, smx, xpcs).
        nfs = (await device.progress_counters())["nb_frames_source"]

        if stop_evt.is_set() and num_frames >= nfs:
            logger.info(f"Breaking frame_idx_iterator at {num_frames}")
            break

        while num_frames < nfs:
            yield FrameMapping(
                receiver_idx=ReceiverIdx(np.uint32(0)),
                local_idx=LocalIdx(num_frames),
                frame_idx=GlobalIdx(num_frames),
            )
            num_frames += 1

        await asyncio.sleep(fetch_interval_s)


async def round_robin_frame_iterator(
    devices: list[TangoProcessing],
    ordering: list[int],
    fetch_interval_s: float,
    stop_evt: asyncio.Event,
) -> AsyncIterator[FrameMapping]:
    local_idx: npt.NDArray[LocalIdx] = np.array([0 for _ in devices])

    while True:
        # NOTE(mdu) nb_frames_source is present on all pipelines (cuda,
        # failing, legacy, smx, xpcs).
        pcs = await asyncio.gather(*[dev.progress_counters() for dev in devices])
        nfs = [pc["nb_frames_source"] for pc in pcs]

        if stop_evt.is_set() and np.all(local_idx >= nfs):
            logger.info(
                f"Breaking frame_idx_iterator at {local_idx}, {nfs=}, "
                f"total={sum(local_idx)}"
            )
            break

        while np.any(local_idx < nfs):
            frame_idx = local_idx.sum()
            rcv_idx = ordering[frame_idx % len(devices)]

            yield FrameMapping(
                receiver_idx=rcv_idx,
                local_idx=local_idx[rcv_idx],
                frame_idx=frame_idx,
            )

            local_idx[rcv_idx] += 1

        await asyncio.sleep(fetch_interval_s)


@dataclass
class PipelineErrorEvent:
    """Structure passed to the registered callback upon error in the pipeline."""

    uuid: UUID
    device_name: str
    error_msg: str


class Pipeline:
    """A base class for all processing pipelines.

    Implements logic common to all processing pipelines.
    """

    FRAME_SOURCES: dict[str, FrameSource]
    """Map of available frame source names to a corresponding FrameSource descriptor.

    Definition in child classes is enforced by __init_subclass__().
    """

    REDUCED_DATA_SOURCES: dict[str, ReducedDataSource]
    """Map of available reduced data names to a corresponding ReducedDataSource descriptor.

    Definition in child classes is enforced by __init_subclass__().
    """

    TANGO_CLASS: str
    """Class name as defined on server side.

    Definition in child classes is enforced by __init_subclass__().
    """

    PROGRESS_INDICATOR: str
    """Name of the main progress counter.

    Definition in child classes is enforced by __init_subclass__().
    """

    @classmethod
    def __init_subclass__(cls) -> None:
        """Initialize a pipeline subclass."""
        if not hasattr(cls, "TANGO_CLASS"):
            raise ValueError(
                f"Pipeline subclass {cls} must define a TANGO_CLASS class member"
            )

        if not hasattr(cls, "FRAME_SOURCES"):
            raise ValueError(
                f"Pipeline subclass {cls} must define a FRAME_SOURCES class member"
            )

        if not hasattr(cls, "REDUCED_DATA_SOURCES"):
            raise ValueError(
                f"Pipeline subclass {cls} must define a REDUCED_DATA_SOURCES class member"
            )

        if not hasattr(cls, "PROGRESS_INDICATOR"):
            raise ValueError(
                f"Pipeline subclass {cls} must define a PROGRESS_INDICATOR class member"
            )

    def __init__(
        self,
        devices: TangoProcessingGroup,
        num_frames: int,
        frame_infos: dict[str, FrameInfo],
        roi_params: RoiParams,
        saving_channels: dict[str, FrameSavingChannel],
        masterfile_metadata: MasterFileMetadata,
    ):
        self.uuid = devices.uuid
        self.devices = devices
        self.topology = devices.topology

        self.frame_infos = frame_infos
        """Dynamic frame info (shape, pixel type) indexed by source name."""

        self.lut_task: asyncio.Task[None] | None = None
        self.master_file_task: asyncio.Task[None] | None = None

        self.close_event = asyncio.Event()
        """
        Set in close(), used to stop the frame index iteration in single and
        round robin topologies.

        In dynamic dispatch, frame indices are fetched from each receiver to
        build the lookup table instead.
        """

        self.started = False
        """Set to True on start()."""

        self.closed = False
        """Set to True on close()."""

        if num_frames < 0:
            raise ValueError("Need either nb_frames > 0, or nb_frames == 0 (endless)")

        if num_frames == 0:
            # Pick a reasonably large initial buffer size for endless acquisition.
            size_hint = 32_768
        else:
            # Evenized num_frames
            size_hint = num_frames + num_frames % 2

        self.lut = LookupTable(size_hint=size_hint, num_receivers=len(self.devices))

        self.reduced_data = ReducedData(
            devices=self.devices,
            size_hint=size_hint,
            lookup=self.lut,
            roi_params=roi_params,
            static_sources=self.REDUCED_DATA_SOURCES,
            fetch_interval_s=0.05,
        )

        self.master_file_generator = MasterFileGenerator(
            frame_channels=saving_channels, metadata=masterfile_metadata
        )

    def __del__(self) -> None:
        logger.debug(f"Pipeline instance {self.uuid} destroyed")

    @classmethod
    async def get_frame_infos(
        cls, devices: TangoProcessingGroup
    ) -> dict[str, FrameInfo]:
        """Build a map of frame_infos."""
        frame_infos: dict[str, FrameInfo] = {}

        for name in cls.FRAME_SOURCES.keys():
            # TODO(mdu) We should come up with a better mechanism for getting
            # the frame info for a specific frame source.
            if name == "input_frame":
                frame_infos[name] = await devices.input_frame_info()
            else:
                frame_infos[name] = await devices.processed_frame_info()

        return frame_infos

    async def frame_idx_iterator(
        self,
        fetch_interval_s: float,
        stop_evt: asyncio.Event,
    ) -> AsyncIterator[FrameMapping]:
        num_frames = 0

        iterator: AsyncIterator[FrameMapping]

        if type(self.topology) is SingleReceiver:
            iterator = single_receiver_frame_iterator(
                device=self.devices[0],
                fetch_interval_s=fetch_interval_s,
                stop_evt=stop_evt,
            )

        elif type(self.topology) is RoundRobin:
            iterator = round_robin_frame_iterator(
                devices=self.devices,
                ordering=self.topology.ordering,
                fetch_interval_s=fetch_interval_s,
                stop_evt=stop_evt,
            )

        elif type(self.topology) is DynamicDispatch:
            iterator = self.reduced_data.dynamic_index(
                fetch_interval_s=fetch_interval_s
            )

        async for mapping in iterator:
            yield mapping
            num_frames += 1

        logger.info(f"Frame index iterator done after {num_frames} frames")

    def start(self) -> None:
        """Start the reduced data fetching and master file generation tasks."""
        frame_idx_it = self.frame_idx_iterator(
            fetch_interval_s=0.05,
            stop_evt=self.close_event,
        )
        self.lut_task = asyncio.create_task(
            self.lut.build(frame_idx_it), name="lut task"
        )

        self.reduced_data.start()

        self.master_file_task = asyncio.create_task(
            self.master_file_generator.write_master_files(
                num_receivers=len(self.devices), lut=self.lut
            ),
            name="master file task",
        )

        self.started = True

    async def close(self) -> None:
        """Wait for the reduced data subtasks to finish."""

        if self.close_event.is_set():
            logger.warning("Pipeline.close() was already called. Ignoring.")
            return

        # Signal end to frame index iteration (single, round robin)
        self.close_event.set()

        await self.reduced_data.close()
        logger.info("Reduced data system closed")

        if self.lut_task:
            try:
                await self.lut_task
                logger.info("LUT task closed")
            except Exception as e:
                logger.error(
                    f"LUT task failed ({e}): reduced data has likely been truncated"
                )

        if self.master_file_task:
            await self.master_file_task
            logger.info("Master file task closed")

        self.closed = True

    def reduced_data_channels(
        self,
    ) -> dict[str, list[tuple[np.dtype[Any], tuple[int, ...]]]]:
        """Get the description of available reduced data streams."""
        return self.reduced_data.channel_info()

    def master_files(self) -> dict[str, tuple[str, str]]:
        return {
            key: (desc.master_file_path, desc.data_path())
            for key, desc in self.master_file_generator.mfd.items()
        }

    def is_running(self) -> bool:
        return self.started and not self.closed

    async def channel_progress(self, channel: str) -> ProgressCounter:
        """Get progress counter for a specific channel.

        If the channel has no label (no associated counter), default to the main
        progress indicator with a warning.

        Raises:
          Lima2NotFound: the requested frame channel is invalid.
        """

        if channel not in self.FRAME_SOURCES:
            raise Lima2NotFound(
                f"No frame channel named '{channel}'.\n"
                f"Try one of {tuple(self.FRAME_SOURCES.keys())}."
            )

        if self.FRAME_SOURCES[channel].label is None:
            logger.warning(
                f"Trying to get progress for '{channel}', which has no label. "
                f"Defaulting to main indicator '{self.PROGRESS_INDICATOR}'."
            )
            counter_name = self.PROGRESS_INDICATOR
        else:
            counter_name = f"nb_frames_{self.FRAME_SOURCES[channel].label}"

        counters = await self.progress_counters()

        if counter_name not in counters:
            raise NotImplementedError(
                f"Progress counter '{counter_name}' is missing from "
                f"progress counter dict ({list(counters.keys())})"
            )

        return counters[counter_name]

    async def progress_counters(self) -> dict[str, ProgressCounter]:
        """Get the list of aggregated progress counters"""
        pcs_by_rcv = [await dev.progress_counters() for dev in self.devices]

        # Set of unique progress counter names
        pc_keys = set()
        for rcv_pcs in pcs_by_rcv:
            for k in rcv_pcs.keys():
                pc_keys.add(k)

        # Sanity check: all receivers have the same progress counters (assume homogeneous)
        # Perhaps not true in all future topologies
        for rcv in pcs_by_rcv:
            for key in pc_keys:
                assert key in rcv.keys()

        aggregated_pcs: dict[str, ProgressCounter] = {}
        for pc_key in pc_keys:
            single_counters = []
            for dev, pcs in zip(self.devices, pcs_by_rcv, strict=True):
                single_counters.append(
                    SingleCounter(name=pc_key, value=pcs[pc_key], source=dev.name)
                )

            aggregated_pcs[pc_key] = progress_counter.aggregate(
                single_counters=single_counters
            )

        return aggregated_pcs

    async def lookup_last(self) -> str:
        """Returns the url of the processing device who has processed the latest frame.

        Raises: Lima2LookupError if the frame cannot be looked up.
        """
        match self.topology:
            case SingleReceiver():
                return self.devices[0].url
            case RoundRobin() | DynamicDispatch():
                # Last processed frame index
                values = [
                    (await device.last_frames())["processed_idx"]
                    for device in self.devices
                ]

                if all([value < 0 for value in values]):
                    raise Lima2LookupError(
                        "Cannot lookup last frame: no frames processed yet."
                    )
                else:
                    # Take the receiver with most frames processed and ask it for the
                    # latest one
                    # Reverse the list so that rightmost receivers are favored.
                    values.reverse()
                    rcv_idx = len(values) - values.index(max(values)) - 1
                    return self.devices[rcv_idx].url
            case _:
                raise NotImplementedError

    def lookup(self, frame_idx: GlobalIdx) -> str:
        """Returns the url of the processing device that processed a given frame.

        Raises:
          Lima2LookupError (dynamic dispatch only): Frame not found.
        """
        return self.devices[self.lut.lookup(frame_idx=frame_idx)].url

    def reduced_data_stream(
        self, name: str, channel_idx: int
    ) -> AsyncIterator[npt.NDArray[Any]]:
        """Get a reduced data stream as an async iterator of chunks."""
        return self.reduced_data.stream(name=name, channel_idx=channel_idx)

    @classmethod
    def parse_saving_params(
        cls, proc_params: dict[str, Any]
    ) -> dict[str, SavingParams]:
        """
        Build a map of {source name: SavingParams} using this Pipeline class's frame
        sources and a dict of processing param.
        """
        saving_params: dict[str, SavingParams] = {}
        for name, source in cls.FRAME_SOURCES.items():
            if source.saving_channel is None:
                # Non-persistent frame source
                continue

            if source.saving_channel not in proc_params:
                raise KeyError(
                    f"Saving params for source '{name}' missing from processing "
                    f"params (at '{source.saving_channel}')"
                )

            sdict = proc_params[source.saving_channel]

            try:
                saving_params[name] = SavingParams(
                    base_path=sdict["base_path"],
                    filename_prefix=sdict["filename_prefix"],
                    file_exists_policy=sdict["file_exists_policy"],
                    nb_frames_per_file=sdict["nb_frames_per_file"],
                    nx_entry_name=sdict["nx_entry_name"],
                    nx_instrument_name=sdict["nx_instrument_name"],
                    nx_detector_name=sdict["nx_detector_name"],
                    nb_dimensions=sdict["nb_dimensions"],
                    enabled=sdict["enabled"],
                )
            except KeyError as e:
                raise KeyError(
                    f"Missing key {e} in proc_params['{source.saving_channel}'] "
                    "dictionary."
                ) from None
        return saving_params
