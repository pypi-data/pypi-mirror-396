# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Detector-specific attributes and logic."""

from dataclasses import dataclass


@dataclass
class DetectorAttributes:
    plugin_saves_raws: bool
    """True if the acquisition plugin saves raw frames.
    
    If the detector has this flag enabled, we assume that we'll will find a set of
    saving params in the 'acq_params' dictionary, under the key 'saving'.

    In addition, 
    """


_attributes = {
    "Simulator": DetectorAttributes(plugin_saves_raws=False),
    "Reader": DetectorAttributes(plugin_saves_raws=False),
    "Dectris": DetectorAttributes(plugin_saves_raws=True),
    "Smartpix": DetectorAttributes(plugin_saves_raws=False),
    "Rigaku": DetectorAttributes(plugin_saves_raws=False),
}
"""Static attributes for each supported detector."""


def attributes(name: str) -> DetectorAttributes:
    """Get detector attributes by plugin name."""
    try:
        return _attributes[name]
    except KeyError:
        raise NotImplementedError(f"Unknown detector plugin '{name}'") from None
