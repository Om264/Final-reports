import json
import logging
from pathlib import Path
from .alerts import AlertEvent


class AlertLogger:
    def __init__(self, log_path: str | Path = "alerts.log") -> None:
        self.log_path = Path(log_path)
        self.logger = logging.getLogger("rainfall_alerts")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(self.log_path)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        ))
        self.logger.addHandler(handler)

    def log_alert(self, event: AlertEvent) -> None:
        record = {
            "event": "threshold_exceeded",
            "rainfall_mm": event.rainfall,
            "threshold_mm": event.threshold,
            "timestamp": event.timestamp.isoformat(),
        }
        self.logger.info(json.dumps(record))
