from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional
import numpy as np

from .series import RecoverySeries
from .registry import REGISTRY


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


@REGISTRY.register_metric("ttr")
def time_to_recovery(series: RecoverySeries, eps: float = 0.02) -> np.ndarray:
    """
    TTR: first time index where performance >= baseline*(1-eps) after min point.
    Returns scalar for 1D, else (N,) for batch.
    """
    perf = series.performance
    b = float(series.baseline)
    thr = b * (1.0 - eps)

    if perf.ndim == 1:
        min_idx = int(np.argmin(perf))
        idxs = np.where(perf[min_idx:] >= thr)[0]
        return np.array(min_idx + idxs[0]) if idxs.size else np.array(-1)

    # batch
    min_idx = np.argmin(perf, axis=1)
    out = np.full((perf.shape[0],), -1, dtype=int)
    for i in range(perf.shape[0]):
        j0 = int(min_idx[i])
        idxs = np.where(perf[i, j0:] >= thr)[0]
        out[i] = (j0 + int(idxs[0])) if idxs.size else -1
    return out


@REGISTRY.register_metric("area_of_loss")
def area_of_loss(series: RecoverySeries) -> np.ndarray:
    loss = series.loss()
    return np.sum(loss, axis=-1)


@REGISTRY.register_metric("min_perf")
def min_perf(series: RecoverySeries) -> np.ndarray:
    return series.min_performance()


@REGISTRY.register_metric("resilience_index")
def resilience_index(series: RecoverySeries) -> np.ndarray:
    """
    RI = 1 - (area_of_loss / worst_case_loss), clipped 0..1
    worst_case_loss assumes staying at min_perf for full horizon.
    """
    b = float(series.baseline)
    perf = series.performance
    aol = np.sum(np.maximum(0.0, b - perf), axis=-1)
    m = np.min(perf, axis=-1)
    worst = (b - m) * perf.shape[-1]
    ri = np.where(worst > 1e-9, 1.0 - (aol / worst), 1.0)
    return np.clip(ri, 0.0, 1.0)


@dataclass(frozen=True)
class Metrics:
    """
    Convenience facade, like numpy.linalg / numpy.random style access.
    """
    @staticmethod
    def compute(series: RecoverySeries, names: Optional[list[str]] = None, **kwargs: Any) -> Dict[str, Any]:
        if names is None:
            names = ["ttr", "area_of_loss", "min_perf", "resilience_index"]
        out: Dict[str, Any] = {}
        for n in names:
            fn = REGISTRY.metric(n)
            out[n] = fn(series, **kwargs) if n == "ttr" else fn(series)
        return out
