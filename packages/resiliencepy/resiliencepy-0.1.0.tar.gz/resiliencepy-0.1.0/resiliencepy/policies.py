from __future__ import annotations
from dataclasses import dataclass


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


@dataclass(frozen=True)
class Policy:
    """
    Recovery levers. Keep minimal and interpretable in v0.1.
    """
    safety_stock: float = 0.0     # 0..1
    expediting: bool = False
    overtime: bool = False
    dual_sourcing: bool = False
    rerouting: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "safety_stock", _clip01(self.safety_stock))
