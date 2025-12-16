from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np


@dataclass(frozen=True)
class RecoverySeries:
    """
    Canonical resilience object: time-indexed performance (and optional dimensions).

    - performance: (T,) or (N,T) ndarray
    - baseline: scalar baseline (default 1.0)
    - meta: free-form metadata (scenario, policy, disruption, etc.)

    This is the object that metrics consume, like ndarray is consumed by NumPy ops.
    """
    performance: np.ndarray
    baseline: float = 1.0
    meta: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        perf = np.asarray(self.performance, dtype=float)
        if perf.ndim not in (1, 2):
            raise ValueError("performance must be 1D (T,) or 2D (N,T)")
        object.__setattr__(self, "performance", perf)

    @property
    def is_batch(self) -> bool:
        return self.performance.ndim == 2

    @property
    def T(self) -> int:
        return int(self.performance.shape[-1])

    @property
    def N(self) -> int:
        return int(self.performance.shape[0]) if self.is_batch else 1

    def loss(self) -> np.ndarray:
        """Loss relative to baseline (clipped at 0). Shape matches performance."""
        b = float(self.baseline)
        return np.maximum(0.0, b - self.performance)

    def min_performance(self) -> np.ndarray:
        """Min perf per scenario (scalar if 1D, else (N,))."""
        return np.min(self.performance, axis=-1)

    def argmin(self) -> np.ndarray:
        """Index of minimum perf per scenario."""
        return np.argmin(self.performance, axis=-1)

    def with_meta(self, **updates: Any) -> "RecoverySeries":
        meta = dict(self.meta or {})
        meta.update(updates)
        return RecoverySeries(self.performance, baseline=self.baseline, meta=meta)
