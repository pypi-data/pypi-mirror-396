# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 tango device containers."""


import asyncio
import contextlib
from collections.abc import Callable
from typing import Awaitable, Iterator
from uuid import UUID

import tango as tg

from lima2.common.exceptions import Lima2DeviceError
from lima2.common.state import DeviceState
from lima2.common.types import FrameInfo
from lima2.conductor.tango.processing import ProcessingErrorEvent, TangoProcessing
from lima2.conductor.tango.receiver import TangoReceiver
from lima2.conductor.tango.utils import TangoDevice
from lima2.conductor.topology import Topology


class TangoReceiverGroup(list[TangoReceiver]):
    def __init__(self, receivers: list[TangoReceiver], topology: Topology) -> None:
        super().__init__(receivers)
        self.topology = topology

    async def list_pipelines(self) -> list[tuple[TangoReceiver, list[UUID]]]:
        """Get the list of active pipeline UUIDs for each receiver.

        Raise the first encountered exception.
        """
        futs = [receiver.list_pipelines() for receiver in self]
        uuid_lists = [
            [UUID(value) for value in uuid_list]
            for uuid_list in await asyncio.gather(*futs)
        ]
        return list(zip(self, uuid_lists, strict=True))

    async def errors(self) -> list[tuple[TangoReceiver, str]]:
        """Get the last_error attribute of each receiver.

        Raise the first encountered exception.
        """
        futs = [receiver.last_error() for receiver in self]
        return list(zip(self, await asyncio.gather(*futs), strict=True))


class TangoDeviceGroup(list[TangoDevice]):
    async def acq_states(self) -> list[tuple[TangoDevice, DeviceState]]:
        """Request each device's acq_state attribute.

        Raise the first encountered exception.
        """
        futs = [device.acq_state() for device in self]
        results = await asyncio.gather(*futs)
        return list(zip(self, results, strict=True))

    async def ping(self) -> list[tuple[TangoDevice, int | BaseException]]:
        """Ping all devices, return the result of each call."""
        futs = [device.ping() for device in self]
        results = await asyncio.gather(*futs, return_exceptions=True)
        return list(zip(self, results, strict=True))

    async def start(self) -> list[tuple[TangoDevice, None | BaseException]]:
        """Call start() on each device, return the result of each call."""
        futs = [device.start() for device in self]
        results = await asyncio.gather(*futs, return_exceptions=True)
        return list(zip(self, results, strict=True))

    async def stop(self) -> list[tuple[TangoDevice, None | BaseException]]:
        """Call stop() on each device, return the result of each call."""
        futs = [device.stop() for device in self]
        results = await asyncio.gather(*futs, return_exceptions=True)
        return list(zip(self, results, strict=True))

    async def reset(self) -> list[tuple[TangoDevice, None | BaseException]]:
        """Call reset() on each device, return the result of each call."""
        futs = [device.reset() for device in self]
        results = await asyncio.gather(*futs, return_exceptions=True)
        return list(zip(self, results, strict=True))

    @contextlib.contextmanager
    def attach(self) -> Iterator[None]:
        """A context where all devices are attached (polling/listening to events)."""
        with contextlib.ExitStack() as stack:
            for device in self:
                stack.enter_context(device.attach())
            yield


class TangoProcessingGroup(list[TangoProcessing]):
    """A group of homogeneous processing devices."""

    def __init__(
        self,
        devices: list[TangoProcessing],
        topology: Topology,
        uuid: UUID,
        class_name: str,
    ) -> None:
        super().__init__(devices)
        self.class_name = class_name
        """Pipeline class name."""
        self.uuid = uuid
        """Acquisition/pipeline uuid."""
        self.topology = topology
        """Receiver topology."""

    @staticmethod
    def from_uuid(
        uuid: UUID, topology: Topology, timeout_s: float
    ) -> "TangoProcessingGroup":
        """Create a list of TangoProcessing instances from a single pipeline uuid."""
        db = tg.Database()
        urls = db.get_device_exported(f"*/limaprocessing/{str(uuid)}*")

        if not urls:
            raise ValueError(f"Processing devices not found in tango database: {uuid=}")

        class_names = [db.get_device_info(url).class_name for url in urls]
        if not all(class_name == class_names[0] for class_name in class_names):
            raise NotImplementedError("Heterogeneous processing is not supported")

        class_name = class_names[0]

        def rcv_idx(name: str) -> int:
            """
            Find the receiver index from a processing device name, by splitting
            on the '@' character.
            """
            return int(name.split("@")[-1])

        # Sort the processing devices by receiver index
        sorted_urls = sorted(urls, key=rcv_idx)

        return TangoProcessingGroup(
            devices=[
                TangoProcessing(url=url, class_name=class_name, timeout_s=timeout_s)
                for url in sorted_urls
            ],
            uuid=uuid,
            topology=topology,
            class_name=class_name,
        )

    async def raw_frame_info(self) -> FrameInfo:
        return await self[0].raw_frame_info()

    async def input_frame_info(self) -> FrameInfo:
        return await self[0].input_frame_info()

    async def processed_frame_info(self) -> FrameInfo:
        return await self[0].processed_frame_info()

    async def listen(
        self,
        on_finished: Callable[[TangoProcessing], Awaitable[None]],
        on_error: Callable[[ProcessingErrorEvent], Awaitable[None]],
    ) -> list[None | BaseException]:
        """Subscribe to error/finished events.

        Handlers passed to this method are registered on all devices.
        """

        async def register(device: TangoProcessing) -> None:
            await device.ping()
            try:
                await device.on_finished(on_finished)
                await device.on_error(on_error)
            except BaseException as e:
                raise Lima2DeviceError(
                    f"On {device.name}: {e}", device_name=device.name
                ) from e

        results = await asyncio.gather(
            *[register(dev) for dev in self], return_exceptions=True
        )

        return results
