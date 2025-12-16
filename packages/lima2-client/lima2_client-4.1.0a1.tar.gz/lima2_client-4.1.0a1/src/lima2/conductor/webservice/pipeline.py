# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor server /pipeline endpoints"""

import logging
from typing import Any, AsyncIterator

import jsonschema_default
import numpy as np
import numpy.typing as npt
import orjson
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route

from lima2.common.exceptions import Lima2NotFound
from lima2.conductor import processing
from lima2.conductor.acquisition_system import AcquisitionSystem
from lima2.conductor.topology import GlobalIdx

logger = logging.getLogger(__name__)


async def home(request: Request) -> JSONResponse:
    """
    summary: List of pipeline UUIDs.
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    pipelines = await lima2.list_pipelines()

    return JSONResponse([str(uuid) for uuid in pipelines])


async def pipeline_classes(request: Request) -> JSONResponse:
    """
    summary: Lists all pipeline class names.
    responses:
      200:
        description: OK.
    """
    return JSONResponse(list(processing.pipeline_classes.keys()))


async def pipeline_version(request: Request) -> JSONResponse:
    """
    summary: Get the version of a pipeline class.
    parameters:
      - in: path
        name: name
        schema:
          type: string
        required: true
        description: name of a processing class
    responses:
      200:
        description: OK.
      400:
        description: Invalid class name.
    """
    class_name = str(request.path_params["name"])
    if class_name not in processing.pipeline_classes:
        raise Lima2NotFound(
            f"No such pipeline class: '{class_name}'.\n"
            f"Try one of {tuple(processing.pipeline_classes.keys())}."
        )

    lima2: AcquisitionSystem = request.state.lima2
    version = lima2.receivers[0].proc_version(proc_class=class_name)

    return JSONResponse(version)


async def pipeline_class(request: Request) -> JSONResponse:
    """
    summary: Get the description for a specific pipeline class.
    parameters:
      - in: path
        name: name
        schema:
          type: string
        required: true
        description: name of a processing class
    responses:
      200:
        description: OK.
      400:
        description: Invalid class name.
    """
    class_name = str(request.path_params["name"])

    if class_name not in processing.pipeline_classes:
        raise Lima2NotFound(
            f"No such pipeline class: '{class_name}'.\n"
            f"Try one of {tuple(processing.pipeline_classes.keys())}."
        )

    pipeline_class = processing.pipeline_classes[class_name]

    lima2: AcquisitionSystem = request.state.lima2
    schema = lima2.receivers[0].fetch_proc_schema(proc_class=class_name)
    defaults = jsonschema_default.create_from(schema)

    return JSONResponse(
        {
            "tango_class": pipeline_class.TANGO_CLASS,
            "frame_sources": list(pipeline_class.FRAME_SOURCES.keys()),
            "reduced_data_sources": list(pipeline_class.REDUCED_DATA_SOURCES.keys()),
            "params_schema": orjson.loads(schema),
            "default_params": defaults,
        }
    )


async def pipeline_params_schema(request: Request) -> JSONResponse:
    """
    summary: Get the params schema for a specific pipeline class.
    parameters:
      - in: path
        name: name
        schema:
          type: string
        required: true
        description: name of a processing class
    responses:
      200:
        description: OK.
      400:
        description: Invalid class name.
    """
    class_name = str(request.path_params["name"])

    if class_name not in processing.pipeline_classes:
        raise Lima2NotFound(
            f"No such pipeline class: '{class_name}'.\n"
            f"Try one of {tuple(processing.pipeline_classes.keys())}."
        )

    lima2: AcquisitionSystem = request.state.lima2
    schema = lima2.receivers[0].fetch_proc_schema(proc_class=class_name)

    return JSONResponse(orjson.loads(schema))


async def clear_previous_pipelines(request: Request) -> JSONResponse:
    """
    summary: Erase all pipelines except the current one.
    responses:
      202:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    cleared = await lima2.clear_previous_pipelines()

    return JSONResponse({"cleared": cleared}, status_code=202)


async def pipeline_by_uuid(request: Request) -> JSONResponse:
    """
    summary: Pipeline attributes given its uuid.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid=request.path_params["uuid"])

    return JSONResponse(
        {
            "uuid": str(pipeline.uuid),
            "type": pipeline.TANGO_CLASS,
            "running": pipeline.is_running(),
            "progress_counters": {
                name: counter.asdict()
                for name, counter in (await pipeline.progress_counters()).items()
            },
            "reduced_data": {
                key: [
                    {"dtype": dtype.descr, "shape": shape}
                    for dtype, shape in channel_list
                ]
                for key, channel_list in pipeline.reduced_data_channels().items()
            },
        }
    )


async def pipeline_progress_indicator(request: Request) -> JSONResponse:
    """
    summary: Get the main progress indicator.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid=request.path_params["uuid"])

    counters = await pipeline.progress_counters()

    if pipeline.PROGRESS_INDICATOR not in counters:
        raise NotImplementedError(
            f"Progress indicator '{pipeline.PROGRESS_INDICATOR}' is missing from "
            f"progress counter dict ({list(counters.keys())})"
        )

    return JSONResponse(counters[pipeline.PROGRESS_INDICATOR].sum)


async def pipeline_progress_by_channel(request: Request) -> JSONResponse:
    """
    summary: Get progress for a specific frame source.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
      - in: path
        name: channel
        schema:
          type: string
        required: true
        description: frame channel
    responses:
      200:
        description: OK.
    """
    uuid = request.path_params["uuid"]
    channel = str(request.path_params["channel"])

    lima2: AcquisitionSystem = request.state.lima2

    return JSONResponse(await lima2.progress(channel=channel, uuid=uuid))


async def pipeline_progress_counters(request: Request) -> JSONResponse:
    """
    summary: Lists all progress counters of a pipeline.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid=request.path_params["uuid"])
    counters = await pipeline.progress_counters()

    return JSONResponse({name: counter.asdict() for name, counter in counters.items()})


async def pipeline_reduced_data_channels(request: Request) -> JSONResponse:
    """
    summary: Lists all available reduced data streams (e.g. roi stats).
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid=request.path_params["uuid"])

    return JSONResponse(
        {
            key: [
                {"dtype": dtype.descr, "shape": shape} for dtype, shape in channel_list
            ]
            for key, channel_list in pipeline.reduced_data_channels().items()
        }
    )


async def pipeline_master_files(request: Request) -> JSONResponse:
    """
    summary: Lists the locations of generated master files for each saved frame channel.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid=request.path_params["uuid"])
    master_files = pipeline.master_files()

    return JSONResponse(master_files)


async def pipeline_reduced_data_stream(request: Request) -> StreamingResponse:
    """
    summary: Get a specific reduced data stream (e.g. roi stats).
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
      - in: path
        name: name
        schema:
          type: string
        required: true
        description: name of the data stream
      - in: path
        name: index
        schema:
          type: integer
        required: true
        description: channel index (e.g. if 3 rois are
                     defined, can be 0, 1 or 2)
    responses:
      200:
        description: OK.
    """
    uuid = request.path_params["uuid"]
    name = str(request.path_params["name"])
    index = int(request.path_params["index"])

    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid=uuid)

    chunk_stream = pipeline.reduced_data_stream(name=name, channel_idx=index)

    async def bytes_stream(
        chunks: AsyncIterator[npt.NDArray[Any]],
    ) -> AsyncIterator[bytes]:
        try:
            async for chunk in chunks:
                yield chunk.tobytes()
        except Exception as e:
            raise e

    return StreamingResponse(
        content=bytes_stream(chunk_stream), media_type="application/octet-stream"
    )


async def pipeline_frame_channels(request: Request) -> JSONResponse:
    """
    summary: List available frame channels.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
    responses:
      200:
        description: OK.
    """
    uuid = request.path_params["uuid"]

    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid=uuid)

    return JSONResponse(
        {
            key: {
                "num_channels": value.num_channels,
                "width": value.width,
                "height": value.height,
                "pixel_type": np.dtype(value.pixel_type).name,
            }
            for key, value in pipeline.frame_infos.items()
        }
    )


async def pipeline_frame_lookup(request: Request) -> JSONResponse:
    """
    summary: Find the receiver to ask for a specific frame.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
      - in: path
        name: frame_idx
        schema:
          type: integer
        required: true
        description: frame index
    responses:
      200:
        description: OK.
      400:
        description: Frame not found.
    """
    uuid = request.path_params["uuid"]
    frame_idx = int(request.path_params["frame_idx"])

    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid)

    if frame_idx == -1:
        rcv_url = await pipeline.lookup_last()
    elif frame_idx < 0:
        raise ValueError(f"Cannot lookup frame {frame_idx}: must be >= -1")
    else:
        rcv_url = pipeline.lookup(frame_idx=GlobalIdx(np.uint32(frame_idx)))

    return JSONResponse(
        {
            "frame_idx": int(frame_idx),
            "receiver_url": rcv_url,
        }
    )


async def pipeline_is_running(request: Request) -> JSONResponse:
    """
    summary: Get the running state of the pipeline.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
    responses:
      200:
        description: OK.
    """
    uuid = request.path_params["uuid"]

    lima2: AcquisitionSystem = request.state.lima2
    pipeline = await lima2.get_pipeline(uuid)

    return JSONResponse(pipeline.is_running())


async def pipeline_get_errors(request: Request) -> JSONResponse:
    """
    summary: Get processing error message, if any.
    parameters:
      - in: path
        name: uuid
        schema:
          type: string
        required: true
        description: UUID of a pipeline, or "current"
    responses:
      200:
        description: OK.
    """
    # TODO(mdu) uuid is ignored here, because processing_errors lives in the
    # Acquisition instance. This endpoint will always return the errors from the
    # latest acquisition, even if uuid refers to a previous run.
    _ = request.path_params["uuid"]

    lima2: AcquisitionSystem = request.state.lima2

    if lima2.acquisition is not None:
        return JSONResponse(lima2.acquisition.processing_errors)
    else:
        return JSONResponse([])


routes = [
    Route("/", home, methods=["GET"]),
    Route("/class", pipeline_classes, methods=["GET"]),
    Route("/class/{name:str}", pipeline_class, methods=["GET"]),
    Route("/class/{name:str}/schema", pipeline_params_schema, methods=["GET"]),
    Route("/class/{name:str}/version", pipeline_version, methods=["GET"]),
    Route("/clear", clear_previous_pipelines, methods=["POST"]),
    Route("/{uuid}", pipeline_by_uuid, methods=["GET"]),
    Route("/{uuid}/running", pipeline_is_running, methods=["GET"]),
    Route("/{uuid}/errors", pipeline_get_errors, methods=["GET"]),
    Route("/{uuid}/progress", pipeline_progress_indicator, methods=["GET"]),
    Route(
        "/{uuid}/progress/{channel:str}", pipeline_progress_by_channel, methods=["GET"]
    ),
    Route("/{uuid}/progress_counters", pipeline_progress_counters, methods=["GET"]),
    Route("/{uuid}/reduced_data", pipeline_reduced_data_channels, methods=["GET"]),
    Route("/{uuid}/master_files", pipeline_master_files, methods=["GET"]),
    Route(
        "/{uuid}/reduced_data/{name:str}/{index:int}",
        pipeline_reduced_data_stream,
        methods=["GET"],
    ),
    Route("/{uuid}/frames", pipeline_frame_channels, methods=["GET"]),
    Route("/{uuid}/lookup/{frame_idx}", pipeline_frame_lookup, methods=["GET"]),
]
