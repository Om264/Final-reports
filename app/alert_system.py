import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.config import ALERT_LOG_FILE, ALERT_THRESHOLDS, HISTORY_FILE
from app.utils import current_timestamp, rainfall_to_alert_level

logger = logging.getLogger(__name__)


class AlertSystem:
    def __init__(self, log_file: Path = ALERT_LOG_FILE):
        self.log_file: Path = log_file
        self._current_alerts: Dict[str, str] = {}

    def evaluate(self, rainfall: float, city: str) -> Tuple[str, str]:
        level: str = rainfall_to_alert_level(rainfall, ALERT_THRESHOLDS)
        status_messages: Dict[str, str] = {
            "GREEN": "Normal",
            "YELLOW": "Warning",
            "RED": "Danger - ALERT",
        }
        status: str = status_messages.get(level, "Unknown")

        previous: Optional[str] = self._current_alerts.get(city)
        self._current_alerts[city] = level

        if level == "RED":
            self._log_alert(city, rainfall, level)
            logger.warning(f"RED ALERT triggered for {city}: {rainfall} mm/h")

        if previous and previous != level and level == "RED":
            logger.info(f"Alert escalation for {city}: {previous} -> RED")

        return level, status

    def _log_alert(self, city: str, rainfall: float, level: str) -> None:
        entry: str = f"{current_timestamp()} | {city} | {rainfall:.2f} mm/h | {level}\n"
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(entry)
        except OSError as e:
            logger.error(f"Failed to write alert log: {e}")

    def load_alert_history(self, max_lines: int = 100) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        if not self.log_file.exists():
            return records
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines[-max_lines:]:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    records.append({
                        "timestamp": parts[0],
                        "city": parts[1],
                        "rainfall": parts[2],
                        "level": parts[3],
                    })
        except OSError as e:
            logger.error(f"Failed to read alert log: {e}")
        return records

    def get_current_alert_level(self, city: str) -> str:
        return self._current_alerts.get(city, "GREEN")

    def alert_summary(self) -> Dict[str, int]:
        summary: Dict[str, int] = {"GREEN": 0, "YELLOW": 0, "RED": 0}
        for level in self._current_alerts.values():
            if level in summary:
                summary[level] += 1
        return summary

    def clear_alerts(self) -> None:
        self._current_alerts.clear()
        logger.info("All alerts cleared.")
