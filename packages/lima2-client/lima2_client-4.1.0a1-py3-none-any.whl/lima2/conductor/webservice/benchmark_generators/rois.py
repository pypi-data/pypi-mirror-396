# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Roi stats/profiles generators for benchmarking of the webapp endpoints."""

import logging
import time
from typing import Iterator

import numpy as np

logger = logging.getLogger(__name__)


roi_stats_dtype = np.dtype(
    [
        ("min", np.float32),
        ("max", np.float32),
        ("avg", np.float32),
        ("std", np.float32),
        ("sum", np.float64),
    ]
)


def roi_stats_generator(num_frames: int, num_rois: int, seed: int) -> Iterator[bytes]:
    total_bytes = 0

    np.random.seed(seed)

    roi_min_data = np.random.randn(num_frames, num_rois).astype(np.float32)
    roi_max_data = np.random.randn(num_frames, num_rois).astype(np.float32)
    roi_avg_data = np.random.randn(num_frames, num_rois).astype(np.float32)
    roi_std_data = np.random.randn(num_frames, num_rois).astype(np.float32)
    roi_sum_data = np.random.randn(num_frames, num_rois).astype(np.float64)

    start = time.perf_counter()
    for i in range(num_frames):
        payload = np.empty(len(roi_min_data[i]), dtype=roi_stats_dtype)

        payload["min"] = roi_min_data[i]
        payload["max"] = roi_max_data[i]
        payload["avg"] = roi_avg_data[i]
        payload["std"] = roi_std_data[i]
        payload["sum"] = roi_sum_data[i]

        total_bytes += payload.nbytes
        yield payload.tobytes()

    delta = time.perf_counter() - start

    logger.info(
        f"Transferred {num_frames * num_rois} roi stats ({total_bytes / 1024 / 1024} MiB) "
        f"in {time.perf_counter() - start:.2f}s "
        f"({total_bytes / 1024 / 1024 / delta:.2f} MiB/s)"
    )
