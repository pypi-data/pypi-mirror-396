# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Classes and functions to handle receiver topologies (single, round-robin, etc)."""

import asyncio
import logging
import traceback
from dataclasses import dataclass
from typing import AsyncIterator, NewType, cast

import numpy as np
import numpy.typing as npt

from lima2.common.exceptions import Lima2LookupError
from lima2.conductor.utils import expand, naturalsize

logger = logging.getLogger(__name__)


GlobalIdx = NewType("GlobalIdx", np.uint32)
"""Global frame index."""

LocalIdx = NewType("LocalIdx", np.uint32)
"""Local (to a receiver) frame index."""

ReceiverIdx = NewType("ReceiverIdx", np.uint32)
"""Receiver device index."""


@dataclass
class FrameMapping:
    """Maps a frame index to a receiver index."""

    receiver_idx: ReceiverIdx
    local_idx: LocalIdx
    frame_idx: GlobalIdx


class Topology:
    """Receiver topology interface."""


class SingleReceiver(Topology):
    """Single receiver topology."""


class RoundRobin(Topology):
    """Multiple-receiver topology where the receiver ordering is fixed throughout the acquisition.

    This class represents a static, strict round robin where the ordering is fixed at prepare-time.
    """

    def __init__(self, num_receivers: int, ordering: list[int]) -> None:
        self.num_receivers = num_receivers
        """Number of receivers"""

        self.ordering = ordering
        """Ordering of receivers: list of indices specifying who gets a given frame.

        E.g. for two receivers, ordering = [1, 0] means:
        - receiver 1 gets the first frame
        - receiver 0 gets the second frame
        - receiver 1 gets the third frame
        and so on.
        `ordering[i % num_receivers]` yields the index of the receiver which acquired frame i.
        """


class DynamicDispatch(Topology):
    """A multi-receiver topology where the frame dispatching is unpredictable.

    For instance, when the detector has an internal mechanism for load-balancing across receivers,
    there is no simple way to map a frame index to a receiver. In such cases, a lookup table
    generated at runtime is used to determine where any given frame is located.
    """

    def __init__(self, num_receivers: int) -> None:
        self.num_receivers = num_receivers


class LookupTable:
    UNKNOWN = np.iinfo(np.uint32).max

    def __init__(
        self,
        size_hint: int,
        num_receivers: int,
    ) -> None:

        self.lut = np.full(
            fill_value=LookupTable.UNKNOWN,
            shape=(size_hint, 2),
            dtype=np.uint32,
        )
        """Lookup table.

        Maps a global index to a (receiver_idx, local_idx) pair.
        """

        self.rlut = np.full(
            fill_value=LookupTable.UNKNOWN,
            shape=(
                size_hint // num_receivers + size_hint % num_receivers,
                num_receivers,
            ),
            dtype=np.uint32,
        )
        """Reverse lookup table.

        Maps (local_idx, receiver_idx) pair to a global index.
        """

        logger.info(
            f"LUT memory usage: {naturalsize(self.lut.nbytes + self.rlut.nbytes)}"
        )

        self.new_data_cond = asyncio.Condition()
        self.build_done = asyncio.Event()

    async def wait_reverse_lookup(
        self, receiver_idx: ReceiverIdx, from_idx: LocalIdx, num_frames: int
    ) -> npt.NDArray[GlobalIdx]:
        """Block the caller until global index of all required frames is known."""

        ret: npt.NDArray[GlobalIdx] | None = None

        def predicate() -> bool:
            nonlocal ret
            ret = self.reverse_lookup(
                receiver_idx=receiver_idx, from_idx=from_idx, num_frames=num_frames
            )
            if not np.any(ret == LookupTable.UNKNOWN):
                return True
            elif self.build_done.is_set():
                raise RuntimeError(
                    f"Chunk cannot be mapped despite LUT completion "
                    f"({receiver_idx=}, {from_idx=}, {num_frames=})"
                )
            else:
                return False

        async with self.new_data_cond:
            await self.new_data_cond.wait_for(predicate)

        assert ret is not None

        return ret

    def reverse_lookup(
        self, receiver_idx: ReceiverIdx, from_idx: LocalIdx, num_frames: int
    ) -> npt.NDArray[GlobalIdx]:
        """Returns global frame indices for a range of frames on a receiver.

        If the frame index isn't yet known, its value is UNKNOWN.
        """

        global_idx: npt.NDArray[GlobalIdx]

        if from_idx >= self.rlut.shape[0]:
            # Slice entirely overflows the buffer
            global_idx = np.full(
                shape=num_frames,
                fill_value=LookupTable.UNKNOWN,
                dtype=self.rlut.dtype,
            )
        elif from_idx + num_frames >= self.rlut.shape[0]:
            # Slice partially overflows the buffer
            overflow = np.full(
                shape=from_idx + num_frames - self.rlut.shape[0],
                fill_value=LookupTable.UNKNOWN,
                dtype=self.rlut.dtype,
            )
            global_idx = np.concatenate([self.rlut[from_idx:, receiver_idx], overflow])
        else:
            global_idx = cast(
                npt.NDArray[GlobalIdx],
                self.rlut[from_idx : from_idx + num_frames, receiver_idx],
            )

        return global_idx

    def lookup(self, frame_idx: GlobalIdx) -> ReceiverIdx:
        """Determine the location of a frame.

        Raises Lima2LookupError if the frame's location isn't known yet.
        """
        if frame_idx >= self.lut.shape[0]:
            raise Lima2LookupError(f"Frame {frame_idx} not yet acquired.")

        rcv_idx, local_idx = self.lut[frame_idx]
        if rcv_idx == LookupTable.UNKNOWN:
            raise Lima2LookupError(f"Frame {frame_idx} not yet acquired.")

        logger.debug(f"{frame_idx=} -> {rcv_idx=} {local_idx=}")

        return ReceiverIdx(rcv_idx)

    async def iterate(self) -> AsyncIterator[FrameMapping]:
        at_idx = GlobalIdx(np.uint32(0))

        while True:
            # NOTE: the index can grow, so we can't simply
            # use a for loop over its rows.

            rcv_idx, local_idx = self.lut[at_idx]

            if rcv_idx != LookupTable.UNKNOWN:
                yield FrameMapping(
                    receiver_idx=rcv_idx, local_idx=local_idx, frame_idx=at_idx
                )
                at_idx = GlobalIdx(at_idx + 1)
            elif self.build_done.is_set():
                break
            else:
                async with self.new_data_cond:
                    await self.new_data_cond.wait()

            while at_idx >= self.lut.shape[0]:
                if self.build_done.is_set():
                    return
                logger.info(
                    f"lookup.iterate() has hit the index limit at {at_idx}: "
                    "waiting for resize or done event..."
                )
                async with self.new_data_cond:
                    await self.new_data_cond.wait()

        logger.info("Finished iterating over lookup table")

    def _build_iteration(self, mapping: FrameMapping) -> None:
        if mapping.frame_idx >= self.lut.shape[0]:
            self.lut = expand(self.lut, fill_value=LookupTable.UNKNOWN)
            logger.warning(f"Frame lut has grown to {self.lut.shape[0]} entries")
        if mapping.local_idx >= self.rlut.shape[0]:
            self.rlut = expand(self.rlut, fill_value=LookupTable.UNKNOWN)
            logger.warning(f"Frame rlut has grown to {self.rlut.shape[0]} entries")

        self.lut[mapping.frame_idx] = (mapping.receiver_idx, mapping.local_idx)
        self.rlut[mapping.local_idx, mapping.receiver_idx] = mapping.frame_idx

    async def build(self, frame_idx_iterator: AsyncIterator[FrameMapping]) -> None:
        async for mapping in frame_idx_iterator:
            try:
                self._build_iteration(mapping)
            except Exception:
                logger.error(
                    f"Exception in lookup.build() loop at "
                    f"{mapping.frame_idx} -> {mapping.receiver_idx}:\n"
                    f"{traceback.format_exc()}"
                )
                self.build_done.set()
                async with self.new_data_cond:
                    self.new_data_cond.notify_all()
                raise
            finally:
                async with self.new_data_cond:
                    self.new_data_cond.notify_all()

        logger.info(
            "Lookup table done building "
            f"({(self.lut[:, 0] != LookupTable.UNKNOWN).sum()} frames)\n"
        )

        self.build_done.set()
        # Notify consumers that no more frames will be mapped
        async with self.new_data_cond:
            self.new_data_cond.notify_all()

    def num_contiguous(self) -> int:
        """Returns the number of contiguous frames currently in the LUT."""
        unknowns = self.lut[:, 0] == LookupTable.UNKNOWN
        if not np.any(unknowns):
            return self.lut.shape[0]
        else:
            return int(np.where(unknowns)[0][0])
