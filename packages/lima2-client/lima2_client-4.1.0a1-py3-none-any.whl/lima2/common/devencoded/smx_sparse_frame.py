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

DATA_HEADER_FORMAT = "<HHIII"
DATA_HEADER_SIZE = struct.calcsize(DATA_HEADER_FORMAT)


@dataclass
class SmxSparseFrame:
    """
    Provide sparse data frame from Lima including few metadata
    """

    index: npt.NDArray[Any]
    intensity: npt.NDArray[Any]
    background_avg: npt.NDArray[Any]
    background_std: npt.NDArray[Any]

    idx: int
    """Index of the frame where 0 is the first frame"""

    shape: tuple[int, ...]
    """Shape of the frame"""

    def __bool__(self) -> bool:
        return not self.isEmpty()

    def isEmpty(self) -> bool:
        return self.index is None

    def densify(
        self,
        mask: npt.NDArray[Any],
        radius: npt.NDArray[Any],
        dummy: npt.NDArray[Any],
        normalization: npt.NDArray[Any] | None = None,
    ) -> Frame:
        """Generate a dense image of its sparse representation with background

        :param mask: 2D array with NaNs for mask and pixel radius for the valid pixels
        :param radius: 1D array with the radial distance
        :param dummy: numerical value for masked-out pixels in dense image
        :param normalization: flat*solidangle*polarization*... array
        :return dense array
        """
        dense = np.interp(mask, radius, self.background_avg)
        if self.background_std is not None:
            std = np.interp(mask, radius, self.background_std)
            np.maximum(0.0, np.random.normal(dense, std), out=dense)
        if normalization is not None:
            dense *= normalization

        flat = dense.ravel()
        flat[self.index] = self.intensity
        dtype = self.intensity.dtype
        if np.issubdtype(dtype, np.integer):
            dense = np.round(dense)
        dense = np.ascontiguousarray(dense, dtype=dtype)
        dense[np.logical_not(np.isfinite(mask))] = dummy

        return Frame(data=dense, idx=self.idx)

    def densify_peaks(self) -> npt.NDArray[Any]:
        """Generate a dense image of its sparse representation with peaks only

        :param mask: 2D array with NaNs for mask and pixel radius for the valid pixels
        :return dense array
        """
        dense = np.zeros(self.shape, self.intensity.dtype)
        flat = dense.ravel()
        flat[self.index] = self.intensity
        return dense

    @property
    def data(self) -> npt.NDArray[Any]:
        return self.densify_peaks()


def decode(raw_data: EncodedFrame) -> SmxSparseFrame:
    """Decode data provided by Lima2

    Argument:
        raw_data: DevEncoded data

    Returns:
        A SmxSparseFrame.
    """

    if isinstance(raw_data, tuple):
        # Support the direct output from proxy.readImage
        if raw_data[0] != "SMX_SPARSE_FRAME":
            raise DevEncodedFormatNotSupported(
                "Data type SMX_SPARSE_FRAME expected (found %s)." % raw_data[0]
            )
        raw_data = raw_data[1]

    (
        width,
        height,
        nb_bins,
        nb_peaks,
        frame_idx,
    ) = struct.unpack_from(DATA_HEADER_FORMAT, raw_data)

    offset = DATA_HEADER_SIZE
    index = np.frombuffer(raw_data, count=nb_peaks, offset=offset, dtype=np.int32)
    offset += index.nbytes
    intensity = np.frombuffer(raw_data, count=nb_peaks, offset=offset, dtype=np.float32)
    offset += intensity.nbytes
    background_avg = np.frombuffer(
        raw_data, count=nb_bins, offset=offset, dtype=np.float32
    )
    offset += background_avg.nbytes
    background_std = np.frombuffer(
        raw_data, count=nb_bins, offset=offset, dtype=np.float32
    )

    shape = (1, height, width)
    return SmxSparseFrame(
        index, intensity, background_avg, background_std, frame_idx, shape
    )
