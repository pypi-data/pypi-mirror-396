from __future__ import annotations
from typing import Callable, Dict, Any

MetricFn = Callable[..., Any]


class Registry:
    def __init__(self) -> None:
        self._metrics: Dict[str, MetricFn] = {}

    def register_metric(self, name: str) -> Callable[[MetricFn], MetricFn]:
        def deco(fn: MetricFn) -> MetricFn:
            if name in self._metrics:
                raise KeyError(f"Metric '{name}' already registered")
            self._metrics[name] = fn
            return fn
        return deco

    def metric(self, name: str) -> MetricFn:
        if name not in self._metrics:
            raise KeyError(f"Metric '{name}' not registered")
        return self._metrics[name]

    @property
    def metrics(self) -> Dict[str, MetricFn]:
        return dict(self._metrics)


REGISTRY = Registry()
