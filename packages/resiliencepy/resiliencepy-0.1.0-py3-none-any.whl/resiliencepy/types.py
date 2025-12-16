from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

CurveShape = Literal["linear", "exponential", "logistic", "delayed_rebound"]
DisruptionKind = Literal[
    "supplier_shutdown",
    "port_closure",
    "transport_delay",
    "cyberattack",
    "demand_spike",
]
