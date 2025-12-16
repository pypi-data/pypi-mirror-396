# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Utility functions to decode Lima data from device server."""

import struct
from typing import Any

import numpy
import numpy.typing as npt

from .exception import DevEncodedFormatNotSupported

DATA_HEADER_FORMAT = "<IHHIIHHHHHHHHIIIIIIQ"
DATA_MAGIC = struct.unpack(">I", b"DTAY")[0]
DATA_HEADER_SIZE = struct.calcsize(DATA_HEADER_FORMAT)


def decode(raw_data: tuple[str, bytes], dtype: npt.DTypeLike) -> npt.NDArray[Any]:
    """Decode data provided by Lima2

    See https://lima1.readthedocs.io/en/latest/applications/tango/python/doc/#devencoded-data-array

    Argument:
        raw_data: DevEncoded data
        dtype:
    """

    if raw_data[0] != "STRUCTURED_ARRAY":
        raise DevEncodedFormatNotSupported(
            "Data type STRUCTURED_ARRAY expected (found %s)." % raw_data[0]
        )
    raw_data = raw_data[1]

    (
        magic,
        version,
        header_size,
        _category,
        data_type,
        endianness,
        nb_dim,
        dim1,
        dim2,
        _dim3,
        _dim4,
        _dim5,
        _dim6,
        _dim_step1,
        _dim_step2,
        _dim_step3,
        _dim_step4,
        _dim_step5,
        _dim_step6,
        frame_idx,
    ) = struct.unpack_from(DATA_HEADER_FORMAT, raw_data)

    if magic != DATA_MAGIC:
        raise DevEncodedFormatNotSupported(
            "Magic header not supported (found 0x%x)." % magic
        )

    # Assume backward-compatible incremental versioning
    if version < 1:
        raise DevEncodedFormatNotSupported(
            "Image header version not supported (found %s)." % version
        )

    data = numpy.frombuffer(raw_data, offset=header_size, dtype=dtype)

    # Create a memory copy only if it is needed
    if not data.flags.writeable:
        data = numpy.array(data)

    return data
