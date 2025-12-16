# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor server /control endpoints"""

import logging

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from lima2.conductor.acquisition_system import AcquisitionSystem

logger = logging.getLogger(__name__)


async def info(request: Request) -> JSONResponse:
    """
    summary: Show detector info.
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    info = await lima2.det_info()

    return JSONResponse(info)


async def status(request: Request) -> JSONResponse:
    """
    summary: Show detector status.
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    status = await lima2.det_status()

    return JSONResponse(status)


async def capabilities(request: Request) -> JSONResponse:
    """
    summary: Describe detector capabilities.
    responses:
      200:
        description: OK.
    """
    lima2: AcquisitionSystem = request.state.lima2
    capabilities = await lima2.det_capabilities()

    return JSONResponse(capabilities)


async def command(request: Request) -> JSONResponse:
    """
    summary: Execute a detector-specific command.
    responses:
      202:
        description: OK.
    """
    params = await request.json()

    for key in ("name", "arg"):
        if key not in params:
            raise RuntimeError(f"Key '{key}' missing from request parameters")

    lima2: AcquisitionSystem = request.state.lima2
    ret = await lima2.control.command(name=params["name"], arg=params["arg"])

    # NOTE(mdu) assume ret is json serializable
    return JSONResponse(ret, status_code=202)


async def attribute(request: Request) -> JSONResponse:
    """
    summary: Read or write an attribute.
    parameters:
      - in: path
        name: name
        schema:
          type: string
        required: true
        description: name of the attribute to set/get
    responses:
      200:
        description: read successful.
      202:
        description: write successful.
    """
    name = str(request.path_params["name"])
    lima2: AcquisitionSystem = request.state.lima2

    if request.method == "GET":
        ret = await lima2.control.read_attribute(name=name)
        # NOTE(mdu) assume ret is json serializable
        return JSONResponse(ret, status_code=200)
    elif request.method == "POST":
        value = await request.json()
        await lima2.control.write_attribute(name=name, value=value)
        return JSONResponse({}, status_code=202)
    else:
        raise NotImplementedError


routes = [
    Route("/info", info, methods=["GET"]),
    Route("/status", status, methods=["GET"]),
    Route("/capabilities", capabilities, methods=["GET"]),
    Route("/command", command, methods=["POST"]),
    Route("/attribute/{name:str}", attribute, methods=["GET", "POST"]),
]
