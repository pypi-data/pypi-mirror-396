# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor server entrypoint.

This module defines the create_app function, used by uvicorn to instantiate
our Starlette app.

Here we also define endpoints located at the root (/).
"""

import asyncio
import contextlib
import logging
from importlib import metadata
from json import JSONDecodeError
from typing import AsyncIterator, TypedDict

from packaging.version import Version
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.schemas import SchemaGenerator

from lima2.common.exceptions import Lima2ValueError, serialize
from lima2.conductor.acquisition_system import AcquisitionSystem
from lima2.conductor.webservice import acquisition, detector, pipeline

logger = logging.getLogger(__name__)

DEFAULT_PORT = 58712
"""Webservice default port"""


ConductorState = TypedDict(
    "ConductorState",
    {
        "lima2": AcquisitionSystem,
        "user_lock": asyncio.Lock,
    },
)

pkg_version = Version(metadata.version("lima2-client"))


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[ConductorState]:
    """Lifespan generator.

    Makes contextual objects (state, ...) accessible in handlers as `request.state.*`.
    """

    # Can run concurrent tasks here
    # async def side_task():
    #     while True:
    #         logger.info("side_task!")
    #         await asyncio.sleep(0.5)
    #
    # asyncio.create_task(side_task())

    lima2: AcquisitionSystem = app.state.lima2

    with lima2.attach():
        yield {
            "lima2": lima2,
            "user_lock": asyncio.Lock(),
        }

    logger.info("Bye bye")


async def homepage(request: Request) -> JSONResponse:
    """
    summary: Says hi :)
    responses:
      200:
        description: OK
    """

    lima2: AcquisitionSystem = request.state.lima2
    gstate = await lima2.global_state()

    dev_states = await lima2.device_states()

    return JSONResponse(
        {"hello": "lima2 :)", "state": gstate.name}
        | {"devices": {dev.name: state.name for dev, state in dev_states}}
    )


async def conductor_version(request: Request) -> JSONResponse:
    """
    summary: Query running version of the conductor.
    responses:
      200:
        description: OK
    """
    return JSONResponse(str(pkg_version))


async def plugin_version(request: Request) -> JSONResponse:
    """
    summary: Query running version of the detector plugin.
    responses:
      200:
        description: OK
    """
    lima2: AcquisitionSystem = request.state.lima2

    return JSONResponse(await lima2.control.version())


async def ping(request: Request) -> JSONResponse:
    """
    summary: Ping all devices and return the latency in us.
    responses:
      202:
        description: OK
    """

    lima2: AcquisitionSystem = request.state.lima2
    ping_us = {dev.name: await dev.ping() for dev in [lima2.control, *lima2.receivers]}

    return JSONResponse(ping_us, status_code=202)


schemas = SchemaGenerator(
    {
        "openapi": "3.0.0",
        "info": {
            "title": "Conductor API",
            "version": f"{pkg_version.major}.{pkg_version.minor}",
        },
    }
)


async def openapi_schema(request: Request) -> Response:
    return schemas.OpenAPIResponse(request=request)


async def system_state(request: Request) -> JSONResponse:
    """
    summary: Returns the system state.
    responses:
      200:
        description: OK
    """
    lima2: AcquisitionSystem = request.state.lima2
    gstate = await lima2.global_state()
    dev_states = await lima2.device_states()
    return JSONResponse(
        {"state": gstate.name}
        | {"conductor": f"{lima2.state.name}"}
        | {"devices": {dev.name: state.name for dev, state in dev_states}}
    )


async def get_log_level(request: Request) -> JSONResponse:
    """
    summary: Returns the current log level.
    responses:
      200:
        description: OK
    """
    lima2: AcquisitionSystem = request.state.lima2
    level = logging.getLevelName(logging.getLogger("lima2").level).lower()

    dev_levels = {"conductor": level} | {
        dev.name: await dev.log_level() for dev in [lima2.control, *lima2.receivers]
    }

    return JSONResponse(dev_levels)


async def set_conductor_log_level(request: Request) -> JSONResponse:
    """
    summary: Set the conductor's global log level.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: string
    responses:
      200:
        description: OK
    """
    try:
        level = str(await request.json()).upper()
    except JSONDecodeError:
        raise Lima2ValueError("Invalid JSON payload") from None

    logger = logging.getLogger("lima2")

    try:
        logger.setLevel(level=level)
    except ValueError as e:
        raise Lima2ValueError(e) from None

    if level.lower() == "debug":
        logger.debug("Debug logs enabled 👋")

    return JSONResponse(level)


async def set_control_log_level(request: Request) -> JSONResponse:
    """
    summary: Set the control device's log level.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: string
    responses:
      200:
        description: OK
    """
    try:
        level = str(await request.json()).lower()
    except JSONDecodeError:
        raise Lima2ValueError("Invalid JSON payload") from None

    lima2: AcquisitionSystem = request.state.lima2

    await lima2.control.set_log_level(level)

    return JSONResponse(level)


async def set_receiver_log_level(request: Request) -> JSONResponse:
    """
    summary: Set a receiver device's log level.
    parameters:
      - in: path
        name: index
        schema:
          type: integer
        required: true
        description: index of the receiver
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: string
    responses:
      200:
        description: OK
    """
    index = int(request.path_params["index"])
    try:
        level = str(await request.json()).lower()
    except JSONDecodeError:
        raise Lima2ValueError("Invalid JSON payload") from None

    lima2: AcquisitionSystem = request.state.lima2

    if not 0 <= index < len(lima2.receivers):
        raise Lima2ValueError(
            f"Invalid receiver index. "
            f"Valid ones are {list(range(len(lima2.receivers)))}."
        )
    await lima2.receivers[index].set_log_level(level)

    return JSONResponse(level)


async def batch_set_receiver_log_level(request: Request) -> JSONResponse:
    """
    summary: Set the log level of all receiver devices.
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: string
    responses:
      200:
        description: OK
    """
    try:
        level = str(await request.json()).lower()
    except JSONDecodeError:
        raise Lima2ValueError("Invalid JSON payload") from None

    lima2: AcquisitionSystem = request.state.lima2

    futs = [rcv.set_log_level(level) for rcv in lima2.receivers]
    await asyncio.gather(*futs)

    return JSONResponse(level)


async def error_handler(request: Request, exception: Exception) -> JSONResponse:
    """Generic exception handler.

    All internal exceptions will be seen by clients as an error 400 response.

    The content of the exception is serialized to allow reconstruction on the
    client side, when possible. See lima2.common.exceptions.
    """

    return JSONResponse(serialize(exception=exception), status_code=400)


def create_app(lima2: AcquisitionSystem) -> Starlette:
    """Build the web app.

    Returns the webapp instance, with Lima2 context assigned to app's state.
    """

    app = Starlette(
        routes=[
            Route("/", homepage, methods=["GET"]),
            Route("/ping", ping, methods=["POST"]),
            Route("/version/conductor", conductor_version, methods=["GET"]),
            Route("/version/detector_plugin", plugin_version, methods=["GET"]),
            Route(
                "/schema",
                endpoint=openapi_schema,
                include_in_schema=False,
                methods=["GET"],
            ),
            # Mount("/benchmark", routes=benchmark.routes),
            Mount("/acquisition", routes=acquisition.routes),
            Route("/state", system_state, methods=["GET"]),
            Mount("/detector", routes=detector.routes),
            Mount("/pipeline", routes=pipeline.routes),
            Route("/log_level/conductor", set_conductor_log_level, methods=["PUT"]),
            Route("/log_level/control", set_control_log_level, methods=["PUT"]),
            Route(
                "/log_level/receivers/{index:int}",
                set_receiver_log_level,
                methods=["PUT"],
            ),
            Route(
                "/log_level/receivers", batch_set_receiver_log_level, methods=["PUT"]
            ),
            Route("/log_level", get_log_level, methods=["GET"]),
        ],
        debug=False,
        lifespan=lifespan,
        exception_handlers={Exception: error_handler},
    )

    # Pass the AcquisitionSystem instance to the shared app state
    # This is necessary for handlers to be able to use the object.
    app.state.lima2 = lima2

    return app
