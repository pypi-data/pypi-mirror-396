# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 common exceptions.

Defines exception types that can be thrown by the conductor, serialized in its
webservice layer, and deserialized back into an exception by the client layer.
"""

import traceback
from collections.abc import Callable
from pprint import pformat
from typing import Any, cast


class Lima2Error(Exception):
    """An unspecified exception.

    Used as the default type when unable to deseriale an exception on the client
    side.
    """


class Lima2DeviceError(Exception):
    """Exception coming from a remote device, e.g. tango.DevFailed."""

    def __init__(self, err: str, /, device_name: str):
        super().__init__(err)
        self.device_name = device_name


class Lima2Conflict(Exception):
    """Another command is already in progress."""


class Lima2BadCommand(Exception):
    """Cannot execute the command in the current state."""


class Lima2BackendError(Exception):
    """Command failed because of an error from one of the backend devices."""


class Lima2NotFound(Exception):
    """Request failed because of an invalid key or index."""


class Lima2LookupError(Exception):
    """The requested frame couldn't be looked up."""


class Lima2ParamError(Exception):
    """Error while validating the param dictionary."""

    def __init__(self, err: str, /, where: str, path: str, schema: dict[str, Any]):
        super().__init__(err)
        self.where = where
        self.path = path
        self.schema = schema

    def __str__(self) -> str:
        return (
            f"In {self.where}: "
            f"validation error at {self.path}: {super().__str__()}.\n\n"
            f"The schema for this element is:\n{pformat(self.schema)}\n"
        )


class Lima2ValueError(Exception):
    """Generic value error: something is wrong with a parameter's value."""


by_type: dict[type[Exception], tuple[int, Callable[[Exception], dict[str, Any]]]] = {
    Lima2DeviceError: (
        10,
        lambda exc: {"device_name": cast(Lima2DeviceError, exc).device_name},
    ),
    Lima2Conflict: (20, lambda exc: {}),
    Lima2BadCommand: (30, lambda exc: {}),
    Lima2BackendError: (40, lambda exc: {}),
    Lima2NotFound: (50, lambda exc: {}),
    Lima2LookupError: (60, lambda exc: {}),
    Lima2ParamError: (
        70,
        lambda exc: {
            "where": cast(Lima2ParamError, exc).where,
            "path": cast(Lima2ParamError, exc).path,
            "schema": cast(Lima2ParamError, exc).schema,
        },
    ),
    Lima2ValueError: (80, lambda exc: {}),
}
"""Registry of exception types that can be serialized.

Maps each exception type to a tuple (error code, serialization function).
"""

by_code: dict[int, type[Exception]] = {value[0]: key for key, value in by_type.items()}
"""Inverse mapping of `by_type`. Maps error code to exception type."""

assert len(by_type) == len(by_code), "Duplicate error codes in exception registry"


def serialize(exception: Exception) -> dict[str, Any]:
    """Serialize an exception to send as JSON.

    If the exception type is present in the `by_type` registry, use the
    associated serialization function. Otherwise, set the 'code' to -1 to
    indicate an unexpected error.
    """
    if type(exception) in by_type:
        code, ser_fn = by_type[type(exception)]
    else:
        code, ser_fn = -1, lambda exc: {}

    return {
        "code": code,
        "remote_type": type(exception).__name__,
        "message": Exception.__str__(exception),
        "payload": ser_fn(exception),
        "trace": traceback.format_exception(exception),
    }


def deserialize(ser_exc: dict[str, Any]) -> Exception:
    """Unpack a serialized error into the appropriate exception.

    Returns an exception instance.

    If the error code doesn't map to a registered exception type, return a
    generic Lima2Error containing the remote trace.
    """

    # Raise KeyError if anything is missing
    ser_exc["code"]
    ser_exc["remote_type"]
    ser_exc["message"]
    ser_exc["payload"]
    ser_exc["trace"]

    if ser_exc["code"] in by_code:
        exc_type = by_code[ser_exc["code"]]
        return exc_type(ser_exc["message"], **ser_exc["payload"])
    else:
        # Unknown exception -> show remote trace
        return Lima2Error(f"Unknown conductor exception. {''.join(ser_exc['trace'])}")
