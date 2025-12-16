# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor server /benchmark endpoints"""

import logging
from starlette.routing import Route
from starlette.requests import Request
from starlette.responses import StreamingResponse

from .benchmark_generators.rois import roi_stats_generator


logger = logging.getLogger(__name__)


def roi_stats(request: Request) -> StreamingResponse:
    """
    responses:
      200:
        description: OK
    parameters:
      - in: query
        name: num_frames
        type: integer
      - in: query
        name: num_rois
        type: integer
      - in: query
        name: seed
        type: integer
    """

    # NOTE: roi_stats is not async since we want to benchmark the max
    # framerate that the app can handle. See https://www.starlette.io/threadpool/.

    num_frames = int(request.query_params.get("num_frames", 16000))
    num_rois = int(request.query_params.get("num_rois", 1))
    seed = int(request.query_params.get("seed", 1))

    logger.debug(
        f"Streaming roi stats from with " f"{num_frames=}, {num_rois=}, {seed=}"
    )

    return StreamingResponse(
        content=roi_stats_generator(
            num_frames=num_frames, num_rois=num_rois, seed=seed
        ),
        media_type="application/octet-stream",
    )


routes = [Route("/roi_stats", roi_stats)]
