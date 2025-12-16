# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor server /acquisition endpoints"""

import logging

import jsonschema_default
import orjson
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from lima2.common.exceptions import Lima2Conflict, Lima2ValueError
from lima2.common.state import RunState
from lima2.conductor.acquisition_system import AcquisitionSystem

logger = logging.getLogger(__name__)


async def prepare(request: Request) -> JSONResponse:
    """
    summary: Prepare for acquisition.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              uuid:
                type: string
              control:
                type: object
              receiver:
                type: object
              processing:
                type: object
    responses:
      202:
        description: Prepare OK.
      400:
        description: Prepare failed. Check response.
    """

    # Prepare for acquisition: send params over and instantiate the pipeline
    # This handler is transactional: it sends a response only once the server is done
    # preparing.

    logger.debug("Handling prepare() request")

    if request.state.user_lock.locked():
        raise Lima2Conflict("Another command is in progress.")

    async with request.state.user_lock:
        params = await request.json()

        for key in ["control", "receiver", "processing"]:
            if key not in params:
                raise Lima2ValueError(f"Params JSON is missing key '{key}'.")

        ctl_params = params["control"]
        rcv_params = params["receiver"]
        proc_params = params["processing"]

        lima2: AcquisitionSystem = request.state.lima2

        uuid = await lima2.prepare(
            ctl_params=ctl_params, acq_params=rcv_params, proc_params=proc_params
        )

        return JSONResponse(
            str(uuid),
            status_code=202,
        )


async def start(request: Request) -> JSONResponse:
    """
    summary: Start the prepared acquisition.
    responses:
      202:
        description: Acquisition started.
    """
    if request.state.user_lock.locked():
        raise Lima2Conflict("Another command is in progress.")

    async with request.state.user_lock:
        lima2: AcquisitionSystem = request.state.lima2
        await lima2.start()

        return JSONResponse({}, status_code=202)


async def trigger(request: Request) -> JSONResponse:
    """
    summary: Send a trigger signal to control.
    responses:
      202:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    await lima2.trigger()

    return JSONResponse({}, status_code=202)


async def stop(request: Request) -> JSONResponse:
    """
    summary: Stop the current acquisition.
    responses:
      202:
        description: Acquisition stopped.
    """
    if request.state.user_lock.locked():
        raise Lima2Conflict("Another command is in progress.")

    async with request.state.user_lock:
        lima2: AcquisitionSystem = request.state.lima2
        await lima2.stop()

        return JSONResponse({}, status_code=202)


async def reset(request: Request) -> JSONResponse:
    """
    summary: Reset (recover from FAULT).
    responses:
      202:
        description: Recovered.
    """
    if request.state.user_lock.locked():
        raise Lima2Conflict("Another command is in progress.")

    async with request.state.user_lock:
        lima2: AcquisitionSystem = request.state.lima2
        await lima2.reset()

        return JSONResponse({}, status_code=202)


async def state(request: Request) -> JSONResponse:
    """
    summary: Get the current state of the acquisition as a RunState's name and IntFlag
             value.
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2

    if lima2.acquisition is None:
        return JSONResponse({"name": RunState.IDLE.name, "value": RunState.IDLE.value})

    if lima2.acquisition.state.failed():
        return JSONResponse(
            {"name": RunState.FAULT.name, "value": RunState.FAULT.value}
        )
    elif lima2.acquisition.state.running():
        return JSONResponse(
            {"name": RunState.RUNNING.name, "value": RunState.RUNNING.value}
        )
    else:
        return JSONResponse({"name": RunState.IDLE.name, "value": RunState.IDLE.value})


async def running(request: Request) -> JSONResponse:
    """
    summary: Determine if an acquisition is currently running.
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2

    if lima2.acquisition is None:
        return JSONResponse(False)

    return JSONResponse(lima2.acquisition.state.running())


async def failed(request: Request) -> JSONResponse:
    """
    summary: Determine if the current acquisition has failed.
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2

    if lima2.acquisition is None:
        return JSONResponse(False)

    return JSONResponse(lima2.acquisition.state.failed())


async def default_params(request: Request) -> JSONResponse:
    """
    summary: Default control and receiver parameters.
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2

    ctl_schema = lima2.control.fetch_params_schema()
    rcv_schema = lima2.receivers[0].fetch_params_schema()

    return JSONResponse(
        {
            "control": jsonschema_default.create_from(ctl_schema),
            "receiver": jsonschema_default.create_from(rcv_schema),
        }
    )


async def params_schema(request: Request) -> JSONResponse:
    """
    summary: JSON schema for control and receiver parameters.
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2

    ctl_schema = lima2.control.fetch_params_schema()
    rcv_schema = lima2.receivers[0].fetch_params_schema()

    return JSONResponse(
        {
            "control": orjson.loads(ctl_schema),
            "receiver": orjson.loads(rcv_schema),
        }
    )


async def nb_frames_acquired(request: Request) -> JSONResponse:
    """
    summary: Number of frames acquired (according to control device).
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    nb_frames_acquired = await lima2.nb_frames_acquired()

    return JSONResponse(nb_frames_acquired.asdict())


async def nb_frames_xferred(request: Request) -> JSONResponse:
    """
    summary: Number of frames transferred (by receiver devices).
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    nb_frames_xferred = await lima2.nb_frames_xferred()

    return JSONResponse(nb_frames_xferred.asdict())


async def errors(request: Request) -> JSONResponse:
    """
    summary: Get the last error thrown by each receiver, if any.
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    errors = await lima2.errors()

    return JSONResponse(errors)


routes = [
    Route("/prepare", prepare, methods=["POST"]),
    Route("/start", start, methods=["POST"]),
    Route("/trigger", trigger, methods=["POST"]),
    Route("/stop", stop, methods=["POST"]),
    Route("/reset", reset, methods=["POST"]),
    Route("/state", state, methods=["GET"]),
    Route("/running", running, methods=["GET"]),
    Route("/failed", failed, methods=["GET"]),
    Route("/default_params", default_params, methods=["GET"]),
    Route("/params_schema", params_schema, methods=["GET"]),
    Route("/nb_frames_acquired", nb_frames_acquired, methods=["GET"]),
    Route("/nb_frames_xferred", nb_frames_xferred, methods=["GET"]),
    Route("/errors", errors, methods=["GET"]),
]
