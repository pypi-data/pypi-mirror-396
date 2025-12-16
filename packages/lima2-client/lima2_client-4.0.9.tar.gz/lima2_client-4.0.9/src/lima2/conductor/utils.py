# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Utility functions"""

import asyncio
import contextlib
import functools
import logging
import time
import traceback
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, Iterator, TypeVar

import jsonschema_rs
import numpy as np

from lima2.common.types import pixel_type_to_np_dtype

logger = logging.getLogger(__name__)

DecoratedFunc = TypeVar("DecoratedFunc", bound=Callable[..., Any])

Validator = (
    jsonschema_rs.Draft4Validator
    | jsonschema_rs.Draft6Validator
    | jsonschema_rs.Draft7Validator
    | jsonschema_rs.Draft201909Validator
    | jsonschema_rs.Draft202012Validator
)


@functools.cache
def _get_validator(schema: str) -> Validator:
    """Get a Validator instance from a serialized schema string."""
    return jsonschema_rs.validator_for(schema)  # type: ignore


def validate(instance: dict[str, Any], schema: str) -> None:
    """Lima2 param validation.

    Raises a ValidationError if `instance` fails the schema validation.

    To validate quickly and allow parallel validations, use jsonschema_rs.

    Since JSON schema draft 6, a value is considered an "integer" if its
    fractional part is zero [1]. This means for example that 2.0 is considered
    an integer.

    The jsonschema_rs validator doesn't allow us to provide custom validation
    criteria, so we allow such values through, but should be careful to cast all
    "integer" params to python int before using them.

    [1] https://json-schema.org/draft-06/json-schema-release-notes
    """
    validator = _get_validator(schema)
    validator.validate(instance=instance)


def list_to_jsonpath(path: list[str | int]) -> str:
    """Convert a path as list into a json path string.

    Assumes no special characters (dot, space, quote) in the path elements.
    """
    if len(path) == 0:
        return "$"
    ret = "$"
    for item in path:
        if isinstance(item, int):
            ret += f"[{item}]"
        elif isinstance(item, str):
            ret += f".{item}"
        else:
            raise TypeError(type(item))
    return ret


def get_subschema(schema: dict[str, Any], path: list[str | int]) -> dict[str, Any]:
    """In a nested schema dictionary, get the subschema at `path`.

    Assumes path is the path to an actual subschema, not a leaf of the schema.

    For a jsonschema_rs.ValidationError, this should be used as
    ```
    get_subschema(schema, error.schema_path[:-1])
    ```
    """
    if len(path) == 0:
        return schema
    else:
        return get_subschema(schema[str(path[0])], path[1:])


def frame_info_to_shape_dtype(frame_info: dict[str, Any]) -> dict[str, Any]:
    return dict(
        shape=(
            frame_info["nb_channels"],
            frame_info["dimensions"]["y"],
            frame_info["dimensions"]["x"],
        ),
        dtype=pixel_type_to_np_dtype[frame_info["pixel_type"]],
    )


def naturalsize(size: int, decimal_places: int = 2) -> str:
    """Format a size."""
    size = float(size)
    for unit in ["B", "kiB", "MiB", "GiB", "TiB", "PiB"]:
        if size < 1024 or unit == "PiB":
            break
        size /= 1024
    return f"{size:.{decimal_places}f} {unit}"


def naturaltime(time_s: float, decimal_places: int = 1) -> str:
    """Format a duration in seconds to a human-readable string."""
    thresholds = [
        (60 * 60, "hrs"),
        (60, "min"),
        (1, "s"),
        (1e-3, "ms"),
        (1e-6, "µs"),
        (1e-9, "ns"),
    ]
    for threshold, unit in thresholds:
        if time_s >= threshold:
            value = time_s / threshold
            unit = unit
            break
    else:
        # value doesn't exceed the ns threshold
        # -> express in scientific notation.
        return f"{time_s * 1e9:.{decimal_places}e} ns"

    return f"{value:.{decimal_places}f} {unit}"


class Ticker:
    """Execute an async callback at regular intervals."""

    def __init__(
        self,
        interval_s: float,
        callback: Callable[..., Awaitable[bool | None]],
        kwargs: dict[str, Any] | None = None,
        descr: str = "",
        skip_one: bool = False,
    ) -> None:
        self.task: asyncio.Task[None] | None = None
        self.interval_s = interval_s
        self.callback = callback

        if kwargs is None:
            kwargs = {}
        self.kwargs = kwargs

        self.skip_one = skip_one
        if descr == "":
            self.descr = self.callback.__name__
        else:
            self.descr = descr

    async def _loop(self) -> None:
        if self.skip_one:
            await asyncio.sleep(self.interval_s)
        while True:
            start = time.perf_counter()
            try:
                stop = await self.callback(**self.kwargs)
                if stop:
                    break
            except Exception:
                logger.error(
                    f"Exception in ticker callback '{self.descr}'. "
                    f"{traceback.format_exc()}"
                )
                break
            delta = time.perf_counter() - start
            if delta >= self.interval_s:
                logger.warning(
                    f"Ticker callback '{self.descr}' took "
                    f"{(delta - self.interval_s) * 1e3:.1f}ms "
                    f"longer than interval ({self.interval_s}s)"
                )
            await asyncio.sleep(max(0, self.interval_s - delta))

    @contextlib.contextmanager
    def context(self) -> Iterator[None]:
        self.start()
        try:
            yield
        except Exception:
            raise
        finally:
            self.cancel()

    def start(self) -> None:
        self.task = asyncio.create_task(
            self._loop(), name=f"ticker({self.descr}, {self.interval_s})"
        )

    def cancel(self) -> None:
        if self.task:
            self.task.cancel()

    def done(self) -> bool:
        if self.task:
            return self.task.done()
        else:
            return False


NpAny = TypeVar("NpAny", bound=np.generic)
"""Generic numpy type."""

NpShape = TypeVar("NpShape", bound=tuple[int, ...])
"""Generic numpy shape."""


def expand(
    array: np.ndarray[NpShape, np.dtype[NpAny]],
    fill_value: Any | None = None,
) -> np.ndarray[NpShape, np.dtype[NpAny]]:
    """Expands an array by a factor 2 along its first dimension."""

    if fill_value:
        ret = np.full(
            fill_value=fill_value,
            shape=(array.shape[0] * 2, *array.shape[1:]),
            dtype=array.dtype,
        )
    else:
        ret = np.empty(
            shape=(array.shape[0] * 2, *array.shape[1:]),
            dtype=array.dtype,
        )
    ret[: array.shape[0]] = array
    return ret


T = TypeVar("T")


async def warn_if_hanging(coroutine: Coroutine[Any, Any, T], warn_every_s: float) -> T:
    """Await a coroutine forever, but log a warning periodically if it takes too long."""

    async def notify() -> None:
        logger.warning(
            f"{coroutine.__qualname__} has been working for {warn_every_s}s..."
        )

    with Ticker(interval_s=warn_every_s, callback=notify, skip_one=True).context():
        return await coroutine


def to_async(func: Callable[..., T]) -> Callable[..., Awaitable[T]]:
    """Wrap a standard function (can be a lambda) into an async one."""

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):  # type: ignore
        return func(*args, **kwargs)

    return wrapper
