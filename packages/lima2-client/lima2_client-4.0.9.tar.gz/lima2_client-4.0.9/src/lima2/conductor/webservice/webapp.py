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
from typing import AsyncIterator, TypedDict

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.schemas import SchemaGenerator

from lima2.common.exceptions import serialize
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
    {"openapi": "3.0.0", "info": {"title": "Conductor API", "version": "0.1"}}
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
        | {"conductor": f"{lima2.state}"}
        | {"devices": {dev.name: state.name for dev, state in dev_states}}
    )


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
        ],
        debug=False,
        lifespan=lifespan,
        exception_handlers={Exception: error_handler},
    )

    # Pass the AcquisitionSystem instance to the shared app state
    # This is necessary for handlers to be able to use the object.
    app.state.lima2 = lima2

    return app
