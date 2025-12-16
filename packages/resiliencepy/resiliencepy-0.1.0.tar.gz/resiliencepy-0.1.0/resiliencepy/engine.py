from __future__ import annotations
from dataclasses import asdict
from typing import Optional
import numpy as np

from .types import CurveShape
from .disruptions import Disruption
from .policies import Policy
from .series import RecoverySeries


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def _policy_effects(p: Policy) -> tuple[float, float, float]:
    """
    Returns (depth_mult, ttr_mult, cost_proxy).
    Interpretable, stable defaults (v0.1).
    """
    depth_mult = 1.0
    ttr_mult = 1.0
    cost_proxy = 0.0

    if p.safety_stock > 0:
        depth_mult *= (1.0 - 0.6 * p.safety_stock)
        cost_proxy += 0.4 * p.safety_stock

    if p.dual_sourcing:
        depth_mult *= 0.75
        ttr_mult *= 0.80
        cost_proxy += 0.15

    if p.rerouting:
        ttr_mult *= 0.90
        cost_proxy += 0.10

    if p.expediting:
        ttr_mult *= 0.75
        cost_proxy += 0.35

    if p.overtime:
        ttr_mult *= 0.85
        cost_proxy += 0.25

    return float(depth_mult), float(ttr_mult), float(cost_proxy)


def _curve_1d(shape: CurveShape, impact_level: float, ttr: int, T: int, start: int, delay_days: int, overshoot: float) -> np.ndarray:
    """
    Returns (T,) unit performance curve (baseline=1.0).
    """
    perf = np.ones(T, dtype=float)
    if start >= T:
        return perf

    perf[start:] = impact_level

    end = min(T - 1, start + ttr)
    n = end - start + 1
    if n <= 1:
        return perf

    x = np.linspace(0.0, 1.0, n)

    if shape == "linear":
        rec = impact_level + (1.0 - impact_level) * x

    elif shape == "exponential":
        k = 4.0
        rec = impact_level + (1.0 - impact_level) * (1.0 - np.exp(-k * x)) / (1.0 - np.exp(-k))

    elif shape == "logistic":
        k = 10.0
        sig = 1.0 / (1.0 + np.exp(-k * (x - 0.5)))
        sig0 = 1.0 / (1.0 + np.exp(-k * (0.0 - 0.5)))
        sig1 = 1.0 / (1.0 + np.exp(-k * (1.0 - 0.5)))
        sig = (sig - sig0) / (sig1 - sig0)
        rec = impact_level + (1.0 - impact_level) * sig

    elif shape == "delayed_rebound":
        delay_frac = min(0.9, delay_days / max(1, ttr))
        rec = np.full_like(x, impact_level)
        m = x >= delay_frac
        xr = (x[m] - delay_frac) / max(1e-9, (1.0 - delay_frac))
        k = 12.0
        sig = 1.0 / (1.0 + np.exp(-k * (xr - 0.5)))
        sig0 = 1.0 / (1.0 + np.exp(-k * (0.0 - 0.5)))
        sig1 = 1.0 / (1.0 + np.exp(-k * (1.0 - 0.5)))
        sig = (sig - sig0) / (sig1 - sig0)
        rec[m] = impact_level + (1.0 - impact_level) * sig

    else:
        raise ValueError(f"Unknown curve shape: {shape}")

    if overshoot > 0:
        rec = rec + overshoot * (x ** 2)

    perf[start:end + 1] = rec
    perf[end + 1:] = perf[end]
    return perf


def simulate(
    disruption: Disruption,
    policy: Policy,
    *,
    horizon_days: int = 60,
    baseline: float = 1.0,
    curve_shape: CurveShape = "logistic",
) -> RecoverySeries:
    """
    Single scenario simulation.
    """
    if horizon_days <= 0:
        raise ValueError("horizon_days must be > 0")

    depth_mult, ttr_mult, cost_proxy = _policy_effects(policy)

    base_depth = _clip01(disruption.severity)
    depth = _clip01(base_depth * depth_mult)

    base_ttr = int(max(3, round(disruption.duration_days * (1.2 + 1.6 * disruption.severity))))
    ttr = int(max(2, round(base_ttr * ttr_mult)))

    overshoot = 0.05 if policy.overtime else 0.0
    delay_days = int(0.3 * disruption.duration_days) if curve_shape == "delayed_rebound" else 0

    unit = _curve_1d(
        curve_shape,
        impact_level=(1.0 - depth),
        ttr=ttr,
        T=horizon_days,
        start=disruption.start_day,
        delay_days=delay_days,
        overshoot=overshoot,
    )
    perf = unit * float(baseline)

    meta = {
        "disruption": asdict(disruption),
        "policy": asdict(policy),
        "curve_shape": curve_shape,
        "cost_proxy": cost_proxy,
        "depth": depth,
        "ttr_model": ttr,
    }
    return RecoverySeries(perf, baseline=float(baseline), meta=meta)


def simulate_batch(
    disruptions: list[Disruption],
    policies: list[Policy],
    *,
    horizon_days: int = 60,
    baseline: float = 1.0,
    curve_shape: CurveShape = "logistic",
) -> RecoverySeries:
    """
    Batch simulation: returns performance shape (N,T)
    - Pairwise if len(disruptions)==len(policies)
    - Broadcast if one side is length 1
    """
    if horizon_days <= 0:
        raise ValueError("horizon_days must be > 0")
    if len(disruptions) == 0 or len(policies) == 0:
        raise ValueError("disruptions and policies must be non-empty")

    if len(disruptions) != len(policies):
        if len(disruptions) == 1:
            disruptions = disruptions * len(policies)
        elif len(policies) == 1:
            policies = policies * len(disruptions)
        else:
            raise ValueError("Provide equal lengths or one side length=1 for broadcasting")

    N = len(disruptions)
    perf = np.empty((N, horizon_days), dtype=float)
    meta = {"N": N, "baseline": float(baseline), "curve_shape": curve_shape}

    # still loop over scenarios, but each curve is vectorized across time
    for i, (d, p) in enumerate(zip(disruptions, policies)):
        perf[i, :] = simulate(d, p, horizon_days=horizon_days, baseline=baseline, curve_shape=curve_shape).performance

    return RecoverySeries(perf, baseline=float(baseline), meta=meta)
