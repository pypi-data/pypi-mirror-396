# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor client exceptions."""


class MalformedConductorResponse(RuntimeError):
    """Raised when the conductor's response cannot be interpreted.

    Raised when the conductor returns a 400 response but it has a
    non-json payload, or the payload doesn't have an 'error' key.

    Indicates a flaw in error handling code on the server side.
    """


class ConductorConnectionError(RuntimeError):
    """Raised by all client functions when the conductor can't be reached."""


class ConductorEndpointNotFound(RuntimeError):
    """Raised when a request is made to the conductor on an invalid endpoint."""
