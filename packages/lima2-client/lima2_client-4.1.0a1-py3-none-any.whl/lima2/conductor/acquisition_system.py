# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Lima2 acquisition system encapsulation.

Abstraction over the Lima2 system as a whole (control + receivers). Exposes
the state and commands.
"""

import asyncio
import contextlib
import copy
import functools
import logging
import textwrap
import time
import traceback
import weakref
from enum import Enum
from typing import Any, Iterator, Literal
from uuid import UUID, uuid1

import orjson
from jsonschema_rs import ValidationError

from lima2.common.exceptions import (
    Lima2BackendError,
    Lima2BadCommand,
    Lima2DeviceError,
    Lima2NotFound,
    Lima2ParamError,
)
from lima2.common.progress_counter import ProgressCounter, SingleCounter
from lima2.common.state import DeviceState, State
from lima2.common.types import FrameType
from lima2.conductor import detector
from lima2.conductor.acquisition import Acquisition, AcquisitionEvent, SuccessFlag
from lima2.conductor.processing import (
    failing,
    legacy,
    master_file,
    pipeline_classes,
    smx,
    xpcs,
)
from lima2.conductor.processing.master_file import MasterFileMetadata
from lima2.conductor.processing.pipeline import Pipeline
from lima2.conductor.processing.reduced_data import RoiParams
from lima2.conductor.tango.container import (
    TangoDeviceGroup,
    TangoProcessingGroup,
    TangoReceiverGroup,
)
from lima2.conductor.tango.control import TangoControl
from lima2.conductor.tango.receiver import TangoReceiver
from lima2.conductor.tango.utils import TangoDevice, format_exception, unpack_exception
from lima2.conductor.topology import DynamicDispatch, Topology
from lima2.conductor.utils import (
    get_subschema,
    list_to_jsonpath,
    naturaltime,
    validate,
)

logger = logging.getLogger(__name__)


ValidatedControlParams = dict[str, Any]
"""A set of control parameters that passed validation."""
ValidatedReceiverParams = dict[str, Any]
"""A set of receiver parameters that passed validation."""
ValidatedProcessingParams = dict[str, Any]
"""A set of processing parameters that passed validation."""


class DisconnectedError(RuntimeError):
    """Returned by ping_all() when some devices are offline."""


class LocalState(Enum):
    """Simple state tag used to reject untimely user commands."""

    IDLE = "idle"
    READY = "ready"
    RUNNING = "running"


def parse_num_frames(acq_params: dict[str, Any]) -> int:
    """Get the number of frames expected to be acquired from the param dict."""
    return int(acq_params["acq"]["nb_frames"])


class AcquisitionSystem:
    def __init__(
        self,
        control: TangoControl,
        receivers: list[TangoReceiver],
        topology: Topology,
        tango_timeout_s: float,
    ):
        self.control = control
        self.receivers = TangoReceiverGroup(receivers=receivers, topology=topology)
        self.devices = TangoDeviceGroup((control, *receivers))

        self.connected_devices: set[TangoDevice] = set()
        """Set of devices whose state isn't OFFLINE."""

        self.topology = topology
        """Static topology (frame dispatch).

        Passed to Pipeline constructor on prepare().
        """

        self.state = LocalState.IDLE
        """Conductor state.

        Local state flag used ONLY to determine whether a user command is valid in the
        current context.
        """

        self.tango_timeout_s = tango_timeout_s

        self.acquisition: Acquisition | None = None
        """Current acquisition."""

        self.cached_pipelines: dict[UUID, Pipeline] = {}

    ###########################################################################
    # Connection
    ###########################################################################

    @contextlib.contextmanager
    def attach(self) -> Iterator[None]:
        """Register event callbacks and start the polling tasks."""
        self.register_control_callbacks()
        self.register_receiver_callbacks()

        with self.devices.attach():
            yield

    async def ping_all(self) -> list[int]:
        """Ping all devices, raise a DisconnectedError if any are offline."""
        results = await self.devices.ping()

        offline_devices: list[str] = []
        pings_us: list[int] = []
        for _dev, ret in results:
            if isinstance(ret, int):
                pings_us.append(ret)
            elif isinstance(ret, Lima2DeviceError):
                offline_devices.append(ret.device_name)
            else:
                raise RuntimeError(
                    f"Unexpected exception in ping(): " f"{traceback.format_exc()}"
                )

        if len(offline_devices) > 0:
            raise DisconnectedError(
                "The following devices are offline:\n- "
                + "\n- ".join([name for name in offline_devices])
            )

        return pings_us

    ###########################################################################
    # State
    ###########################################################################

    async def device_states(self) -> list[tuple[TangoDevice, DeviceState]]:
        """Return a list of (device, state) tuples."""
        return await self.devices.acq_states()

    async def global_state(self) -> State:
        """Compute the unified system state from the individual device states."""
        try:
            await self.ping_all()
        except DisconnectedError:
            return State.DISCONNECTED

        dev_states = await self.device_states()

        for dev, state in dev_states:
            logger.info(f"{dev.name}: {state.name}")

        return State.from_device_states(states=[state for _, state in dev_states])

    ###########################################################################
    # User commands
    ###########################################################################

    async def prepare(
        self,
        ctl_params: dict[str, Any],
        acq_params: dict[str, Any],
        proc_params: dict[str, Any],
    ) -> UUID:
        """Prepare for an acquisition.

        Validate parameters, send them to each device, and call prepare
        to instantiate the processing pipeline.

        Raises:
          Lima2BadCommand: cannot prepare in current state.
          Lima2ParamError: a set of params does not fit its schema.
          Lima2BackendError: an error occurred on a device during the tango command.
        """
        if self.state not in (LocalState.IDLE, LocalState.READY):
            raise Lima2BadCommand(
                f"Cannot prepare for acquisition in {self.state.name.lower()} state."
            )

        if self.acquisition is not None and self.acquisition.running():
            logger.warning(
                f"Previous acquisition seems unfinished: "
                f"{self.acquisition.state.describe()}"
            )
            self.acquisition.detach()

        # If prepare is called while devices are offline, this shows a helpful error.
        try:
            await self.ping_all()
        except DisconnectedError as e:
            raise Lima2BackendError(e) from None

        det_info = await self.control.det_info()
        det_attributes = detector.attributes(name=det_info["plugin"])

        # Homogeneous processing
        ctl = copy.deepcopy(ctl_params)
        rcv_plist = [copy.deepcopy(acq_params) for _ in self.receivers]
        proc_plist = [copy.deepcopy(proc_params) for _ in self.receivers]

        for i in range(len(self.receivers)):
            if det_attributes.plugin_saves_raws:
                if "saving" not in rcv_plist[i]:
                    raise KeyError(
                        f"Detector plugin saves raw frames but the 'saving' subdict "
                        f"is missing from {rcv_plist[i]=}."
                    )
                rcv_plist[i]["saving"]["filename_rank"] = i
                if type(self.topology) is DynamicDispatch:
                    rcv_plist[i]["saving"]["include_frame_idx"] = True

            match proc_params["class_name"]:
                case "LimaProcessingLegacy":
                    legacy.finalize_params(
                        proc_params=proc_plist[i],
                        receiver_idx=i,
                        topology=self.topology,
                    )
                case "LimaProcessingSmx":
                    smx.finalize_params(
                        proc_params=proc_plist[i],
                        receiver_idx=i,
                        num_receivers=len(self.receivers),
                        topology=self.topology,
                    )
                case "LimaProcessingXpcs":
                    xpcs.finalize_params(
                        proc_params=proc_plist[i],
                        receiver_idx=i,
                        topology=self.topology,
                    )
                case "LimaProcessingFailing":
                    failing.finalize_params(
                        proc_params=proc_plist[i],
                        topology=self.topology,
                    )
                case _:
                    raise NotImplementedError

        validate_t0 = time.perf_counter()

        ctl, rcv_plist, proc_plist = await self.validate_params(
            ctl_params=ctl, rcv_params=rcv_plist, proc_params=proc_plist
        )

        logger.debug(
            f"All params validated in {naturaltime(time.perf_counter() - validate_t0)}"
        )

        acq_id = uuid1()

        # Prepare concurrently
        futs = [self.control.prepare(uuid=acq_id, params=ctl)] + [
            rcv.prepare(uuid=acq_id, acq_params=rcv_plist[i], proc_params=proc_plist[i])
            for i, rcv in enumerate(self.receivers)
        ]

        t0 = time.perf_counter()
        results = await asyncio.gather(
            *futs,
            return_exceptions=True,  # Collect exceptions in results
        )
        logger.info(f"Device prepare() took {time.perf_counter() - t0}s")

        errors = [result for result in results if result is not None]
        if any(errors):
            details = textwrap.indent(
                "\n".join([f"{str(error)}" for error in errors]),
                prefix="  ",
            )
            raise Lima2BackendError(
                f"Prepare command failed on {len(errors)} device(s):\n{details}"
            )

        pipeline_list = await self.list_pipelines()
        if acq_id not in pipeline_list:
            raise Lima2NotFound(
                f"Pipeline {acq_id} not found in existing pipelines: {pipeline_list}."
            )

        proc_devs = TangoProcessingGroup.from_uuid(
            uuid=acq_id, topology=self.topology, timeout_s=self.tango_timeout_s
        )
        pipeline_class = pipeline_classes[proc_devs.class_name]

        num_frames = parse_num_frames(acq_params=acq_params)

        # TODO|NOTE(mdu) we could avoid having to parse roi/profile params by adding a
        # server-side mechanism for querying the active reduced data streams
        roi_params = RoiParams.from_dicts(
            roi_params=proc_params.get("statistics"),
            profile_params=proc_params.get("profiles"),
        )

        masterfile_metadata = MasterFileMetadata(
            acq_params=acq_params,
            proc_params=proc_params,
            det_info=det_info,
        )

        # Build master file generation channels
        saving_params = pipeline_class.parse_saving_params(proc_params=proc_params)
        frame_infos = await pipeline_class.get_frame_infos(devices=proc_devs)
        frame_types = {
            name: source.frame_type
            for name, source in pipeline_class.FRAME_SOURCES.items()
        }

        if det_attributes.plugin_saves_raws:
            if "saving" not in acq_params:
                raise KeyError(
                    f"Detector plugin saves raw frames but the 'saving' subdict "
                    f"is missing from {acq_params=}."
                )

            saving_params |= {"raw_frame": acq_params["saving"]}
            frame_infos |= {"raw_frame": await proc_devs.raw_frame_info()}
            frame_types |= {"raw_frame": FrameType.DENSE}

        # Extract saving channels from frame infos, saving params
        saving_channels = master_file.build_channels(
            saving_params=saving_params,
            frame_infos=frame_infos,
            frame_types=frame_types,
        )

        self.acquisition = await Acquisition.attach(
            processing_devices=proc_devs,
            on_end=self.on_acquisition_end,
            on_failure=self.on_acquisition_failure,
            num_frames=num_frames,
            frame_infos=frame_infos,
            roi_params=roi_params,
            saving_channels=saving_channels,
            masterfile_metadata=masterfile_metadata,
        )

        await self.clear_previous_pipelines()

        self.state = LocalState.READY
        logger.info(f"Ready for acquisition {acq_id}")

        return acq_id

    async def start(self) -> None:
        """Call start on all devices.

        Raises:
          Lima2BadCommand: acquisition cannot start.
          Lima2BackendError: an error occurred on a device during the tango command.
        """

        if self.state == LocalState.RUNNING:
            raise Lima2BadCommand("An acquisition is already running.")
        elif self.state != LocalState.READY:
            raise Lima2BadCommand("No acquisition is prepared.")

        if self.acquisition is None:
            raise Lima2BadCommand("Not synced to lima2 backend. Call prepare() again.")

        results = await self.devices.start()

        errors = [ret for _, ret in results if isinstance(ret, BaseException)]
        if any(errors):
            details = textwrap.indent(
                "\n".join([f"{str(error)}" for error in errors]),
                prefix="  ",
            )
            raise Lima2BackendError(
                f"Start command failed failed on {len(errors)} device(s):\n{details}"
            )

        self.state = LocalState.RUNNING
        self.acquisition.start()

        logger.info("🚄 Acquisition running 🚄")

    async def trigger(self) -> None:
        """Call trigger on the Control device."""
        if self.state == LocalState.RUNNING:
            await self.control.trigger()
        else:
            logger.warning(f"Got trigger() while {self.state.name} -> ignoring")

    async def reset(self) -> None:
        """Try to resync with the devices and then recover.

        Raises:
          Lima2BadCommand: acquisition is running.
        """

        # NOTE: here we prioritise looking at the global_state() instead of the
        # local self.state, so that if the conductor and devices desynced, the
        # user can try to recover. At the end of the reset() operation, we force
        # self.state to IDLE and hope that it's enough to get back to a
        # workable situation.
        gstate = await self.global_state()
        if gstate == State.RUNNING:
            # NOTE: forcing self.state to RUNNING allows the user to stop() the
            # acquisition after this failed call.
            self.state = LocalState.RUNNING
            raise Lima2BadCommand("Cannot reset while acquisition is running.")

        logger.info("Calling reset on every device")

        results = await self.devices.reset()

        for device, result in results:
            if isinstance(result, BaseException):
                logger.warning(f"Exception from {device.name} in  to reset(): {result}")

        self.state = LocalState.IDLE
        self.acquisition = None

    async def stop(self) -> None:
        """Stop the running acquisition.

        Raises:
          Lima2BadCommand: not running.
        """
        if self.state != LocalState.RUNNING:
            raise Lima2BadCommand(f"Cannot stop acquisition in {self.state} state.")

        results = await self.devices.stop()

        for dev, res in results:
            if isinstance(res, BaseException):
                logger.warning(f"Exception from {dev.name} in call to stop(): {res}")

        nb_frames_xferred = await self.nb_frames_xferred()
        logger.warning(
            f"Stop requested after {nb_frames_xferred.sum} "
            + " + ".join([str(count.value) for count in nb_frames_xferred.counters])
            + "frames."
        )

    ####################################################################################
    # Event handlers
    ####################################################################################

    async def on_acquisition_end(self, result: SuccessFlag) -> None:
        """Registered as the current Acquisition's on_end() callback."""
        if result.success:
            logger.info("🎉 Run finished successfully 🎉")
        else:
            logger.info("☠️ Run finished with errors ☠️")

        logger.info("Calling control.close()")
        try:
            await self.control.close()
        except BaseException:
            logger.warning(
                f"Exception while calling control.close(): {traceback.format_exc()}"
            )

        self.state = LocalState.IDLE

    async def on_acquisition_failure(self) -> None:
        """Registered as the current Acquisition's on_failure() callback."""
        logger.warning("Aborting acquisition")
        results = await self.devices.stop()

        for dev, res in results:
            if isinstance(res, BaseException):
                logger.warning(f"Exception from {dev.name} in call to stop(): {res}")

    ###########################################################################
    # Pipelines
    ###########################################################################

    @property
    def current_pipeline(self) -> Pipeline | None:
        if self.acquisition is None:
            return None
        else:
            return self.acquisition.pipeline

    async def list_pipelines(self) -> list[UUID]:
        """Fetch the list of pipeline UUIDs (flattened across receivers)."""
        uuids = set(
            uuid
            for _, uuid_list in await self.receivers.list_pipelines()
            for uuid in uuid_list
        )
        return list(uuids)

    async def get_pipeline(self, uuid: Literal["current"] | str | UUID) -> Pipeline:
        """Get a specific pipeline by uuid.

        Automatically connects to the processing devices if the pipeline
        instance doesn't exist yet (hence the async).

        Raises:
          Lima2NotFound: pipeline uuid not found in list of pipelines
        """

        if uuid == "current":
            if self.current_pipeline is not None:
                return self.current_pipeline
            else:
                raise Lima2NotFound("No current pipeline: call prepare first.")
        elif type(uuid) is str:
            uuid = UUID(uuid)

        assert type(uuid) is UUID

        if uuid in self.cached_pipelines:
            return self.cached_pipelines[uuid]

        pipeline_list = await self.list_pipelines()
        if uuid not in pipeline_list:
            raise Lima2NotFound(
                f"Pipeline {uuid} not found in existing pipelines: {pipeline_list}."
            )

        proc_devices = TangoProcessingGroup.from_uuid(
            uuid=uuid, topology=self.topology, timeout_s=self.tango_timeout_s
        )
        pipeline_class = pipeline_classes[proc_devices[0].class_name]

        frame_infos = await pipeline_class.get_frame_infos(devices=proc_devices)

        # NOTE: this creates a "degraded" Pipeline instance that has no lookup table or
        # reduced data.
        pipeline = pipeline_class(
            devices=proc_devices,
            frame_infos=frame_infos,
            num_frames=0,
            roi_params=RoiParams(rois=[], profiles=[]),
            saving_channels={},
            masterfile_metadata=MasterFileMetadata(
                acq_params={}, proc_params={}, det_info={}
            ),
        )

        self.cached_pipelines[uuid] = pipeline

        return pipeline

    async def clear_previous_pipelines(self) -> list[str]:
        """Erase all pipelines except the current one."""
        if self.current_pipeline is not None:
            current = self.current_pipeline.uuid
        else:
            current = None

        async def clear(receiver: TangoReceiver) -> list[str]:
            """Clear previous pipelines from a single receiver device."""
            pipelines = await receiver.list_pipelines()

            cleared: list[str] = []
            for uuid_str in pipelines:
                if uuid_str != str(current):
                    logger.debug(
                        f"Erasing pipeline {uuid_str} from recv {receiver.name}"
                    )
                    await receiver.erase_pipeline(uuid_str)
                    cleared.append(uuid_str)
            return cleared

        futures = [clear(receiver=rcv) for rcv in self.receivers]
        results = await asyncio.gather(*futures, return_exceptions=True)

        cleared: set[str] = set()
        for rcv, res in zip(self.receivers, results, strict=True):
            if isinstance(res, BaseException):
                logger.warning(
                    f"Exception while clearing pipelines from {rcv.name}: "
                    + "".join(traceback.format_exception(res))
                )
            else:
                cleared = cleared.union(res)

        logger.info(f"Cleared pipelines {[uuid for uuid in set(cleared)]}")

        # Reset local cache
        if self.current_pipeline is not None:
            self.cached_pipelines = {self.current_pipeline.uuid: self.current_pipeline}
        else:
            self.cached_pipelines = {}

        return list(cleared)

    ###########################################################################
    # Info
    ###########################################################################

    async def progress(
        self, channel: str, uuid: Literal["current"] | str | UUID
    ) -> int:
        """Get a progress indicator for a given acquisition and frame channel."""

        if channel == "raw_frame":
            if self.acquisition is None:
                raise Lima2NotFound("No acquisition is prepared or running.")
            # NOTE: permissive, "raw_frame" is a valid channel even if the detector
            # plugin has no raw saving mechanism.
            return (await self.nb_frames_xferred()).sum

        pipeline = await self.get_pipeline(uuid=uuid)
        if channel in pipeline.FRAME_SOURCES:
            return (await pipeline.channel_progress(channel=channel)).sum
        else:
            raise Lima2NotFound(
                f"No frame channel named '{channel}'.\n"
                f"Try one of {('raw_frame', *pipeline.FRAME_SOURCES.keys())}."
            )

    async def nb_frames_acquired(self) -> SingleCounter:
        return await self.control.nb_frames_acquired()

    async def nb_frames_xferred(self) -> ProgressCounter:
        return ProgressCounter(
            name="nb_frames_xferred",
            counters=[await rcv.nb_frames_xferred() for rcv in self.receivers],
        )

    async def det_info(self) -> dict[str, Any]:
        return await self.control.det_info()

    async def det_status(self) -> dict[str, Any]:
        return await self.control.det_status()

    async def det_capabilities(self) -> dict[str, Any]:
        return await self.control.det_capabilities()

    async def errors(self) -> list[str]:
        errors: list[str] = []
        for dev, err in await self.receivers.errors():
            if err == "No error":
                continue

            what, info = unpack_exception(err)

            errors.append(
                format_exception(
                    where=dev.name, when="during acquisition", what=what, info=info
                )
            )

        return errors

    ###########################################################################
    # Event handler registration
    ###########################################################################

    def on_device_online(self, device: TangoDevice) -> None:
        logger.info(f"Device {device.name} online.")
        self.connected_devices.add(device)
        if self.connected_devices == set(self.devices):
            logger.info("🟢 All devices connected. Lima2 system operational. 🚀")

    def on_device_down(self, device: TangoDevice) -> None:
        logger.error(f"🔴 {device.name} went offline. ⛓️‍💥")
        self.connected_devices.remove(device)

    def register_control_callbacks(self) -> None:
        """Register on_state_change callback on the control device."""

        # NOTE: Using weakref in event handlers is necessary to allow the
        # garbage collector to destroy the Acquisition object.
        wself = weakref.ref(self)

        async def on_connect(new_state: DeviceState) -> None:
            self_ref = wself()
            if self_ref is None:
                return

            self_ref.on_device_online(device=self_ref.control)

        async def on_state_change(new_state: DeviceState) -> None:
            logger.info(f"Control in new state: {new_state}")

            self_ref = wself()
            if self_ref is None:
                return

            if new_state == DeviceState.OFFLINE:
                self_ref.on_device_down(device=self_ref.control)

                if self_ref.acquisition is not None:
                    await self_ref.acquisition.notify(event=AcquisitionEvent.FAILURE)

        self.control.on_connect(on_connect)
        self.control.on_state_change(on_state_change)

    def register_receiver_callbacks(self) -> None:
        """Register on_connect and on_state_change callback on the receiver devices."""

        # NOTE: Using weakref in event handlers is necessary to allow the
        # garbage collector to destroy the Acquisition object.
        wself = weakref.ref(self)

        async def on_connect(rcv: TangoReceiver, new_state: DeviceState) -> None:
            self_ref = wself()
            if self_ref is None:
                return

            self_ref.on_device_online(device=rcv)

        async def on_state_change(rcv: TangoReceiver, new_state: DeviceState) -> None:
            """Handler for receiver device state changes."""
            logger.info(f"Receiver {rcv.name} in new state: {new_state}")

            self_ref = wself()
            if self_ref is None:
                return

            if new_state == DeviceState.FAULT:
                payload = await rcv.last_error()

                what, info = unpack_exception(payload)

                logger.error(f"⁉️ FAULT state on {rcv.name}. Reason: {what} ({info})")
                if self_ref.acquisition is not None:
                    await self_ref.acquisition.notify(
                        event=AcquisitionEvent.ACQ_DEVICE_FAILED
                    )

            elif new_state == DeviceState.IDLE:
                if self_ref.acquisition is not None:
                    await self_ref.acquisition.notify(
                        event=AcquisitionEvent.ACQ_DEVICE_DONE
                    )

            elif new_state == DeviceState.OFFLINE:
                self_ref.on_device_down(device=rcv)

                if self_ref.acquisition is not None:
                    await self_ref.acquisition.notify(
                        event=AcquisitionEvent.ACQ_DEVICE_DISCONNECTED
                    )

        for receiver in self.receivers:
            receiver.on_connect(functools.partial(on_connect, receiver))
            receiver.on_state_change(functools.partial(on_state_change, receiver))

    ###########################################################################
    # Misc
    ###########################################################################

    async def validate_params(
        self,
        ctl_params: dict[str, Any],
        rcv_params: list[dict[str, Any]],
        proc_params: list[dict[str, Any]],
    ) -> tuple[
        ValidatedControlParams,
        list[ValidatedReceiverParams],
        list[ValidatedProcessingParams],
    ]:
        """Validate parameters.

        NOTE: Param validation can strongly impact the total time spent in the prepare()
        call. To alleviate this, we try to cache as much as possible: - the schemas, in
        control and receiver devices -> avoids fetching them from tango db every time, -
        the validator, created from the parsed schema (cached by validate()).
        """

        def validate_control(control: TangoControl, params: dict[str, Any]) -> None:
            schema = control.fetch_params_schema()
            try:
                validate(instance=params, schema=schema)
            except ValidationError as e:
                raise Lima2ParamError(
                    e.message,
                    where="control params",
                    path=list_to_jsonpath(e.instance_path),
                    schema=get_subschema(orjson.loads(schema), e.schema_path[:-1]),
                ) from e

        def validate_receiver_params(
            receiver: TangoReceiver,
            rcv_params: dict[str, Any],
        ) -> None:
            rcv_schema = receiver.fetch_params_schema()
            try:
                validate(instance=rcv_params, schema=rcv_schema)
            except ValidationError as e:
                raise Lima2ParamError(
                    e.message,
                    where=f"acquisition params for {receiver.name}",
                    path=list_to_jsonpath(e.instance_path),
                    schema=get_subschema(orjson.loads(rcv_schema), e.schema_path[:-1]),
                ) from e

        def validate_proc_params(
            receiver: TangoReceiver,
            proc_params: dict[str, Any],
        ) -> None:
            proc_class: str = proc_params["class_name"]
            proc_schema = receiver.fetch_proc_schema(proc_class=proc_class)
            try:
                validate(instance=proc_params, schema=proc_schema)
            except ValidationError as e:
                raise Lima2ParamError(
                    e.message,
                    where=f"processing params for {receiver.name}",
                    path=list_to_jsonpath(e.instance_path),
                    schema=get_subschema(orjson.loads(proc_schema), e.schema_path[:-1]),
                ) from e

        validate_fut = [
            asyncio.to_thread(validate_control, control=self.control, params=ctl_params)
        ]
        for rcv, rcv_p, proc_p in zip(
            self.receivers, rcv_params, proc_params, strict=True
        ):
            validate_fut.append(
                asyncio.to_thread(
                    validate_receiver_params, receiver=rcv, rcv_params=rcv_p
                )
            )
            validate_fut.append(
                asyncio.to_thread(
                    validate_proc_params, receiver=rcv, proc_params=proc_p
                )
            )

        # Raise the first exception to occur in one of the validations
        await asyncio.gather(*validate_fut)

        return ctl_params, rcv_params, proc_params
