# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor main script.

This file is meant to be executed by an ASGI server for the webapp to be served, e.g.
```
uvicorn lima2.conductor.main:app
```
"""

import asyncio
import logging
from pathlib import Path

from lima2.conductor.acquisition_system import AcquisitionSystem
from lima2.conductor.tango.control import TangoControl
from lima2.conductor.tango.receiver import TangoReceiver
from lima2.conductor.topology import (
    DynamicDispatch,
    RoundRobin,
    SingleReceiver,
    Topology,
)
from lima2.conductor.webservice import utils, webapp

logger = logging.getLogger(__name__)

log_level = utils.env_or("LIMA2_LOG_LEVEL", default="info").upper()
log_path = Path(utils.env_or("LIMA2_LOG_PATH", default="/tmp/lima2_conductor.log"))

utils.configure_logger(
    file_path=log_path,
    stdout_log_level=log_level,
)

logger.info("Launching lima2-conductor.")

# Ensure this module is executed with a running event loop
try:
    asyncio.get_running_loop()
except RuntimeError as e:
    raise RuntimeError(
        f"{__file__} must be executed with a running event loop.\n"
        "Try `uvicorn lima2.conductor.main:app`."
    ) from e


ctl_url = utils.env_or_die("LIMA2_CONTROL_URL")
rcv_urls = [url.strip() for url in utils.env_or_die("LIMA2_RECEIVER_URLS").split(",")]
topology_str = utils.env_or_die("LIMA2_TOPOLOGY")
tango_timeout_s = int(utils.env_or_die("LIMA2_TANGO_TIMEOUT"))

# Parse topology string
topology: Topology
match topology_str:
    case "single":
        if len(rcv_urls) != 1:
            raise ValueError(
                f"Single receiver topology is invalid for {len(rcv_urls)} receivers"
            )
        topology = SingleReceiver()
    case "round_robin":
        if len(rcv_urls) == 1:
            raise ValueError(
                "Round robin topology is invalid for 1 receiver. Use 'single' instead."
            )
        ordering = list(range(len(rcv_urls)))
        logger.warning(f"Assuming round robin ordering: {ordering}")
        topology = RoundRobin(num_receivers=len(rcv_urls), ordering=ordering)
    case "dynamic":
        if len(rcv_urls) == 1:
            raise ValueError(
                "Dynamic topology is wasteful for 1 receiver. Use 'single' instead."
            )
        topology = DynamicDispatch(num_receivers=len(rcv_urls))
    case _:
        raise ValueError(f"Invalid topology string '{topology_str}'")


logger.info(f"Connecting to devices {[ctl_url] + rcv_urls}")


control = TangoControl(ctl_url, timeout_ms=tango_timeout_s * 1000)
receivers = [
    TangoReceiver(rcv_url, timeout_ms=tango_timeout_s * 1000) for rcv_url in rcv_urls
]

lima2 = AcquisitionSystem(
    control=control,
    receivers=receivers,
    topology=topology,
    tango_timeout_s=tango_timeout_s,
)

# Instantiate the Starlette app (picked up by web server, see cli.py)
app = webapp.create_app(lima2=lima2)
