from __future__ import annotations
from dataclasses import dataclass
from .types import DisruptionKind


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


@dataclass(frozen=True)
class Disruption:
    kind: DisruptionKind
    severity: float          # 0..1
    duration_days: int       # >0
    start_day: int = 0       # >=0

    def __post_init__(self) -> None:
        if self.duration_days <= 0:
            raise ValueError("duration_days must be > 0")
        if self.start_day < 0:
            raise ValueError("start_day must be >= 0")
        object.__setattr__(self, "severity", _clip01(self.severity))
