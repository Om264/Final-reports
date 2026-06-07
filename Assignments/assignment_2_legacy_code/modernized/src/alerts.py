from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable
from .fetcher import WeatherData


@dataclass
class AlertEvent:
    rainfall: float
    threshold: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    acknowledged: bool = False


AlertCallback = Callable[[AlertEvent], None]


class AlertEngine:
    def __init__(self, threshold: float = 20.0) -> None:
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        self.threshold = threshold
        self._callbacks: list[AlertCallback] = []

    def subscribe(self, callback: AlertCallback) -> None:
        self._callbacks.append(callback)

    async def evaluate(self, data: WeatherData) -> AlertEvent | None:
        if data.rainfall_1h > self.threshold:
            event = AlertEvent(rainfall=data.rainfall_1h, threshold=self.threshold)
            for cb in self._callbacks:
                cb(event)
            return event
        return None
