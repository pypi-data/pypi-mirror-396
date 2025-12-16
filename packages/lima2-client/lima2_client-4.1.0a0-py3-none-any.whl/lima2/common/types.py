# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 common types."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Iterator

import numpy as np
import numpy.typing as npt

from lima2.common.devencoded import dense_frame, smx_sparse_frame, sparse_frame
from lima2.common.devencoded.dense_frame import EncodedFrame, Frame
from lima2.common.devencoded.smx_sparse_frame import SmxSparseFrame
from lima2.common.devencoded.sparse_frame import SparseFrame

pixel_type_to_np_dtype: dict[str, np.dtype[Any]] = {
    "gray8s": np.dtype(np.int8),
    "gray8": np.dtype(np.uint8),
    "gray16s": np.dtype(np.int16),
    "gray16": np.dtype(np.uint16),
    "gray32s": np.dtype(np.int32),
    "gray32": np.dtype(np.uint32),
    "gray32f": np.dtype(np.float32),
    "gray64f": np.dtype(np.float64),
}
"""Mapping from pixel_enum to numpy type."""


@dataclass
class FrameInfo:
    """Dynamic attributes of a frame source."""

    num_channels: int
    width: int
    height: int
    pixel_type: np.dtype[Any]

    @staticmethod
    def from_dict(value: dict[str, Any]) -> "FrameInfo":
        return FrameInfo(
            num_channels=value["nb_channels"],
            width=value["dimensions"]["x"],
            height=value["dimensions"]["y"],
            pixel_type=pixel_type_to_np_dtype[value["pixel_type"]],
        )


class FrameType(Enum):
    DENSE = auto()
    SPARSE = auto()
    SMX_SPARSE = auto()


decoder_by_type: dict[
    FrameType,
    Callable[
        [EncodedFrame],
        Frame | SparseFrame | SmxSparseFrame,
    ],
] = {
    FrameType.DENSE: dense_frame.decode,
    FrameType.SPARSE: sparse_frame.decode,
    FrameType.SMX_SPARSE: smx_sparse_frame.decode,
}
"""Mapping from frame type to associated decode function"""


@dataclass
class FrameSource:
    """Specifies the name of a getter and a frame type for a given frame source.

    From these two attributes, it is possible to fetch a frame from a processing tango
    device and then decode it.
    """

    getter_name: str
    """Name of the getter method to call on the tango device to fetch the data"""

    frame_type: FrameType
    """Frame type"""

    saving_channel: str | None
    """Name of the associated saving_params object in the proc_params struct.

    Can be None for sources without persistency.
    """

    label: str | None
    """Name of corresponding frame stream in the processing device: progress_counters, etc."""


PEAK_COUNTER_DTYPE = np.dtype(
    [
        ("frame_idx", "i4"),
        ("recv_idx", "i4"),
        ("nb_peaks", "i4"),
    ]
)
"""Smx peak_counter dtype.

NOTE: This describes the dtype as retrieved from the processing device, NOT what
a consumer will receive from the conductor via a reduced data channel. The
frame_idx and recv_idx columns will be stripped by the conductor and the
consumer will not see them.
"""

FILL_FACTOR_DTYPE = np.dtype(
    [
        ("frame_idx", "i4"),
        ("recv_idx", "i4"),
        ("fill_factor", "i4"),
    ]
)
"""Xpcs fill_factor dtype.

NOTE: This describes the dtype as retrieved from the processing device, NOT what
a consumer will receive from the conductor via a reduced data channel. The
frame_idx and recv_idx columns will be stripped by the conductor and the
consumer will not see them.
"""


@dataclass
class ScalarDataSource:
    """A data source with zero-dimensional values.

    E.g. fill factor (count = 1), roi statistics (count = number of rois).
    """

    getter_name: str
    src_dtype: np.dtype[Any]
    """Numpy dtype of the source stream (decoded after pop)."""
    channel_keys: list[str]
    """Fields of src_dtype exposed in outgoing ReducedDataChannels."""
    num_elements: int

    def total_length(self) -> int:
        return self.num_elements

    def shapes(self) -> list[tuple[int, ...]]:
        return [()] * self.num_elements

    def stream_descriptions(self) -> list[tuple[np.dtype[Any], tuple[int, ...]]]:
        elem_dtype = np.dtype([(key, self.src_dtype[key]) for key in self.channel_keys])
        return [(elem_dtype, ())] * self.num_elements

    def split(self, chunk: npt.NDArray[Any]) -> Iterator[npt.NDArray[Any]]:
        for i in range(self.num_elements):
            yield chunk[:, i][self.channel_keys]


@dataclass
class VectorDataSource:
    """A data source whose values are 1D vectors with a fixed length.

    E.g. roi profiles.
    """

    getter_name: str
    src_dtype: np.dtype[Any]
    """Numpy dtype of the source stream (decoded after pop)."""
    channel_keys: list[str]
    """Fields of src_dtype exposed in outgoing ReducedDataChannels."""
    lengths: list[int]
    """Length of each vector indexed by channel index."""

    def total_length(self) -> int:
        return sum(self.lengths)

    def shapes(self) -> list[tuple[int, ...]]:
        return [(length,) for length in self.lengths]

    def stream_descriptions(self) -> list[tuple[np.dtype[Any], tuple[int, ...]]]:
        elem_dtype = np.dtype([(key, self.src_dtype[key]) for key in self.channel_keys])
        return [(elem_dtype, shape) for shape in self.shapes()]

    def split(self, chunk: npt.NDArray[Any]) -> Iterator[npt.NDArray[Any]]:
        offset = 0
        for length in self.lengths:
            yield chunk[:, offset : offset + length][self.channel_keys]
            offset += length


ReducedDataSource = ScalarDataSource | VectorDataSource
