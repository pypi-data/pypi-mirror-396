# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Utility functions to decode Lima data from device server."""

import struct
from dataclasses import dataclass
from typing import Any

import numpy as np
import numpy.typing as npt

from lima2.common.devencoded.dense_frame import EncodedFrame, Frame

from .exception import DevEncodedFormatNotSupported

DATA_HEADER_FORMAT = "<HHII"
DATA_HEADER_SIZE = struct.calcsize(DATA_HEADER_FORMAT)


@dataclass
class SparseFrame:
    """
    Provide sparse data frame from Lima including few metadata
    """

    index: npt.NDArray[Any]
    intensity: npt.NDArray[Any]

    idx: int
    """Index of the frame where 0 is the first frame"""

    shape: tuple[int, ...]
    """Shape of the frame"""

    def __bool__(self) -> bool:
        return not self.isEmpty()

    def isEmpty(self) -> bool:
        return self.index is None

    def densify(self) -> Frame:
        """Generate a dense image of its sparse representation

        :param mask: 2D array with NaNs for mask and pixel radius for the valid pixels
        :return dense array
        """
        dense = np.zeros(self.shape, self.intensity.dtype)
        flat = dense.ravel()
        flat[self.index] = self.intensity
        return Frame(dense, self.idx)


def decode(raw_data: EncodedFrame) -> SparseFrame:
    """Decode data provided by Lima2

    Argument:
        raw_data: DevEncoded data

    Returns:
        A SparseFrame.
    """

    if isinstance(raw_data, tuple):
        if raw_data[0] != "SPARSE_FRAME":
            raise DevEncodedFormatNotSupported(
                "Data type SPARSE_FRAME expected (found %s)." % raw_data[0]
            )
        raw_data = raw_data[1]

    (
        width,
        height,
        nb_pixels,
        frame_idx,
    ) = struct.unpack_from(DATA_HEADER_FORMAT, raw_data)

    offset = DATA_HEADER_SIZE
    index = np.frombuffer(raw_data, count=nb_pixels, offset=offset, dtype=np.int32)
    offset += index.nbytes
    intensity = np.frombuffer(raw_data, count=nb_pixels, offset=offset, dtype=np.uint16)
    offset += intensity.nbytes

    return SparseFrame(index, intensity, frame_idx, (1, height, width))
