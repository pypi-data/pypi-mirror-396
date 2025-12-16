# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor HTTP services wrapped into functions."""

import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Iterator, cast
from uuid import UUID

import numpy as np
import numpy.typing as npt
import tango as tg

from lima2.client.exceptions import ConductorConnectionError
from lima2.client.session import ConductorSession
from lima2.common import pipelines, types
from lima2.common.devencoded.dense_frame import Frame
from lima2.common.devencoded.smx_sparse_frame import SmxSparseFrame
from lima2.common.devencoded.sparse_frame import SparseFrame
from lima2.common.exceptions import Lima2NotFound
from lima2.common.progress_counter import ProgressCounter, SingleCounter
from lima2.common.state import RunState, State
from lima2.common.types import FrameInfo

logger = logging.getLogger(__name__)


class Acquisition:
    """Conductor /acquisition service requests."""

    def __init__(self, session: ConductorSession) -> None:
        self.session = session
        """The conductor session."""

    def prepare(
        self,
        control: dict[str, Any],
        receiver: dict[str, Any],
        processing: dict[str, Any],
    ) -> UUID:
        """Prepare for a new acquisition given control, receiver and processing params."""
        uuid_str = self.session.post(
            "/acquisition/prepare",
            json={
                "control": control,
                "receiver": receiver,
                "processing": processing,
            },
        ).json()
        return UUID(uuid_str)

    def start(self) -> None:
        """Start the currently prepared acquisition."""
        self.session.post("/acquisition/start")

    def stop(self) -> None:
        """Stop the currently running acquisition."""
        self.session.post("/acquisition/stop")

    def trigger(self) -> None:
        """Trigger the detector in the currently running acquisition.

        Only useful in software-triggered acquisitions.
        """
        self.session.post("/acquisition/trigger")

    def reset(self) -> None:
        """Call reset() on the Lima2 devices to attempt recovery from a FAULT state."""
        self.session.post("/acquisition/reset")

    def state(self) -> str:
        """Get the current state of the acquisition."""
        return str(self.session.get("/acquisition/state").json()["name"])

    def running(self) -> bool:
        """Returns True if an acquisition is running.

        Returns False if the latest acquisition is finished, or failed.
        """
        runstate = RunState(self.session.get("/acquisition/state").json()["value"])
        if (
            runstate == RunState.IDLE
            or runstate & RunState.ACQ_DONE
            or runstate & RunState.FAULT
        ):
            return False
        else:
            return True

    def failed(self) -> bool:
        """Returns True if the latest acquisition failed."""
        runstate = RunState(self.session.get("/acquisition/state").json()["value"])
        return bool(runstate & RunState.FAULT)

    def default_params(self) -> tuple[dict[str, Any], dict[str, Any]]:
        """Get default acquisition parameters.

        Returns a tuple (control params, receiver params).
        """
        params = self.session.get("/acquisition/default_params").json()
        return (
            cast(dict[str, Any], params["control"]),
            cast(dict[str, Any], params["receiver"]),
        )

    def params_schema(self) -> dict[str, Any]:
        """Get the schema for acquisition parameters."""
        return cast(
            dict[str, Any], self.session.get("/acquisition/params_schema").json()
        )

    def nb_frames_acquired(self) -> int:
        """Get the number of frames acquired in the current acquisition."""
        json_dict = self.session.get("/acquisition/nb_frames_acquired").json()
        return SingleCounter.fromdict(json_dict).value

    def nb_frames_xferred(self) -> int:
        """Get the number of frames transferred in the current acquisition."""
        json_dict = self.session.get("/acquisition/nb_frames_xferred").json()
        return ProgressCounter.fromdict(json_dict).sum

    def errors(self) -> list[str]:
        """Get all error messages for the current acquisition.

        Can be used in case of failure during the acquisition to report
        the causes.
        """
        return cast(list[str], self.session.get("/acquisition/errors").json())


class Detector:
    """Conductor /detector service requests."""

    def __init__(self, session: ConductorSession) -> None:
        self.session = session
        """The conductor session."""

    def info(self) -> dict[str, Any]:
        """Retrieve the detector info dictionary."""
        return cast(dict[str, Any], self.session.get("/detector/info").json())

    def status(self) -> dict[str, Any]:
        """Retrieve the detector status dictionary."""
        return cast(dict[str, Any], self.session.get("/detector/status").json())

    def capabilities(self) -> dict[str, Any]:
        """Retrieve the detector capabilities dictionary."""
        return cast(dict[str, Any], self.session.get("/detector/capabilities").json())

    def command(self, name: str, arg: Any = None) -> Any:
        """Execute a command on the Lima2 control device."""
        return self.session.post(
            "/detector/command", json={"name": name, "arg": arg}
        ).json()

    def write_attribute(self, name: str, value: Any) -> None:
        """Set the value of an attribute on the Lima2 control device."""
        self.session.post(f"/detector/attribute/{name}", json=value)

    def read_attribute(self, name: str) -> Any:
        """Get the value of an attribute from the Lima2 control device."""
        return self.session.get(f"/detector/attribute/{name}").json()


class Pipeline:
    """Conductor /pipeline service requests."""

    def __init__(self, session: ConductorSession) -> None:
        self.session = session
        """The conductor session."""

    def classes(self) -> list[str]:
        """Enumerate pipeline classes."""
        return cast(list[str], self.session.get("/pipeline/class").json())

    def default_params(self, processing_name: str) -> dict[str, Any]:
        """Fetch default processing params for a pipeline type."""
        json = self.session.get(f"/pipeline/class/{processing_name}").json()
        return cast(dict[str, Any], json["default_params"])

    def params_schema(self, processing_name: str) -> dict[str, Any]:
        """Fetch the JSON schema for a pipeline type."""
        json = self.session.get(f"/pipeline/class/{processing_name}/schema").json()
        return cast(dict[str, Any], json)

    def uuids(self) -> list[UUID]:
        """Get UUIDs for each alive pipeline."""
        return [UUID(uuid_str) for uuid_str in self.session.get("/pipeline/").json()]

    def current_pipeline(self) -> UUID:
        """Get the UUID of the current pipeline."""
        res = self.session.get("/pipeline/current")
        return UUID(res.json()["uuid"])

    def pipeline(self, uuid: str | UUID) -> dict[str, Any]:
        """Get a generic info dictionary for a given pipeline."""
        return cast(dict[str, Any], self.session.get(f"/pipeline/{str(uuid)}").json())

    def running(self, uuid: str | UUID = "current") -> bool:
        """Returns True if the pipeline is currently running.

        If the uuid isn't valid, returns False.
        """
        try:
            res = self.session.get(f"/pipeline/{str(uuid)}/running")
        except Lima2NotFound:
            return False
        return bool(res.json())

    def errors(self, uuid: str | UUID = "current") -> list[str]:
        """Get processing error messages, if any."""
        return cast(list[str], self.session.get(f"/pipeline/{str(uuid)}/errors").json())

    def progress(self, channel: str | None = None, uuid: str | UUID = "current") -> int:
        """Get current number of frames processed.

        If channel isn't specified, return the default progress indicator.
        """
        if channel is None:
            return int(self.session.get(f"/pipeline/{str(uuid)}/progress").json())
        else:
            return int(
                self.session.get(f"/pipeline/{str(uuid)}/progress/{channel}").json()
            )

    def clear_previous_pipelines(
        self,
    ) -> list[str]:
        """Clear and free memory for all pipelines except the latest one."""
        res = self.session.post("/pipeline/clear")
        return cast(list[str], res.json()["cleared"])

    def reduced_data_channels(
        self, uuid: str | UUID = "current"
    ) -> dict[str, list[tuple[np.dtype[Any], tuple[int, ...]]]]:
        """Enumerate reduced data channels for a given pipeline as a dictionary."""
        json = self.session.get(f"/pipeline/{str(uuid)}/reduced_data").json()

        def deser_dtype(
            descr: list[tuple[str, str] | tuple[str, str, tuple[int, ...]]] | str,
        ) -> np.dtype[Any]:
            """Deserialize a np.dtype.descr received in json format."""
            if type(descr) is str:
                return np.dtype(descr)
            elif type(descr) is list:
                ret: list[
                    tuple[str, np.dtype[Any]]
                    | tuple[str, np.dtype[Any], tuple[int, ...]]
                ] = []

                for x in descr:
                    if len(x) == 2:
                        name, dtype = x
                        ret.append((name, deser_dtype(dtype)))
                    elif len(x) == 3:
                        name, dtype, shape = x
                        ret.append((name, deser_dtype(dtype), shape))

                    else:
                        raise NotImplementedError

                return np.dtype(ret)
            else:
                raise TypeError(f"{type(descr)}")

        return {
            key: [
                (deser_dtype(descr["dtype"]), tuple(descr["shape"]))
                for descr in channel_descrs
            ]
            for key, channel_descrs in json.items()
        }

    def frame_channels(self, uuid: str | UUID = "current") -> dict[str, FrameInfo]:
        """Enumerate frame channels for a given pipeline as a dictionary."""
        json = self.session.get(f"/pipeline/{str(uuid)}/frames").json()
        return {
            key: FrameInfo(
                num_channels=value["num_channels"],
                width=value["width"],
                height=value["height"],
                pixel_type=np.dtype(value["pixel_type"]),
            )
            for key, value in json.items()
        }

    def master_files(self, uuid: str | UUID = "current") -> dict[str, tuple[str, str]]:
        """Get a {source: (file path, dataset path)} mapping of generated master files."""
        res = self.session.get(f"/pipeline/{str(uuid)}/master_files")
        return {
            src_name: (file_path, data_path)
            for src_name, [file_path, data_path] in res.json().items()
        }

    def reduced_data(
        self, name: str, channel_idx: int, uuid: str | UUID = "current"
    ) -> Iterator[npt.NDArray[Any]]:
        """Get an iterator over a reduced data channel."""

        # NOTE raises if name or channel_idx is invalid
        res = self.session.get(
            f"/pipeline/{str(uuid)}/reduced_data/{name}/{channel_idx}", stream=True
        )

        channel_descrs = self.reduced_data_channels(uuid=uuid)

        dtype, shape = channel_descrs[name][channel_idx]

        for i, chunk in enumerate(res.iter_content(chunk_size=None)):
            if i % 100 == 0:
                logger.debug(f"Decoding {name} for frame {i}")
            yield np.frombuffer(chunk, dtype=dtype).reshape((-1, *shape))

    def lookup(self, frame_idx: int, uuid: str | UUID = "current") -> tuple[int, str]:
        """Look up a frame by index.

        Returns a tuple (frame index, receiver url).
        """
        json = self.session.get(f"/pipeline/{str(uuid)}/lookup/{frame_idx}").json()

        return (json["frame_idx"], json["receiver_url"])

    def get_frame(
        self, frame_idx: int, source: str, uuid: str | UUID = "current"
    ) -> Frame | SparseFrame | SmxSparseFrame:
        """Fetch a frame directly from a receiver device."""
        fidx, rcv_url = self.lookup(frame_idx=frame_idx, uuid=uuid)
        class_name = self.pipeline(uuid=uuid)["type"]
        try:
            pipeline_info = pipelines.by_name[class_name]
        except KeyError as e:
            raise NotImplementedError(class_name) from e

        try:
            frame_source = pipeline_info.frame_sources[source]
        except KeyError as e:
            raise ValueError(
                f"Invalid frame source '{source}' for pipeline {class_name}."
            ) from e

        device = tg.DeviceProxy(rcv_url)

        getter = getattr(device, frame_source.getter_name)

        try:
            raw_data: tuple[str, bytes] = getter(frame_idx)
        except tg.DevFailed as e:
            logger.error(
                f"Failed to get {source} {frame_idx} (resolved to {fidx} on {device.dev_name()})"
            )
            raise RuntimeError(
                f"Unable to get frame {fidx} from {device.dev_name()}:\n{e}"
            ) from e

        decoder = types.decoder_by_type[frame_source.frame_type]

        frm = decoder(raw_data)

        return frm


class ConnectionState(Enum):
    ONLINE = auto()
    CONDUCTOR_OFFLINE = auto()
    DEVICES_OFFLINE = auto()


@dataclass
class ConductorServices:
    acquisition: Acquisition
    detector: Detector
    pipeline: Pipeline
    session: ConductorSession

    @staticmethod
    def from_session(session: ConductorSession) -> "ConductorServices":
        """Populate a ConductorServices instance from a ConductorSession."""
        return ConductorServices(
            acquisition=Acquisition(session=session),
            detector=Detector(session=session),
            pipeline=Pipeline(session=session),
            session=session,
        )

    def system_state(self) -> dict[str, Any]:
        """Get the state of every Lima2 component."""
        return cast(dict[str, Any], self.session.get("/state").json())

    def connection_state(self) -> ConnectionState:
        """Get the connection state."""
        try:
            system_state = self.system_state()
        except ConductorConnectionError:
            return ConnectionState.CONDUCTOR_OFFLINE

        if State[system_state["state"]] == State.DISCONNECTED:
            return ConnectionState.DEVICES_OFFLINE

        return ConnectionState.ONLINE


def init(hostname: str, port: int = 58712) -> ConductorServices:
    """Initialize a conductor session.

    Returns a namespace of conductor services (`acquisition`, `detector`,
    `pipeline`), and the ConductorSession instance (`session`).
    """

    return ConductorServices.from_session(
        session=ConductorSession(hostname=hostname, port=port)
    )
