import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from app.config import ALERT_LOG_FILE, HISTORY_COLUMNS, HISTORY_FILE, NOTIFICATION_LOG_FILE

logger = logging.getLogger(__name__)


class DataStorage:
    def __init__(self):
        self.history_file: Path = HISTORY_FILE
        self.alert_log_file: Path = ALERT_LOG_FILE
        self.notification_log_file: Path = NOTIFICATION_LOG_FILE

    def save_reading(self, reading: Dict[str, Any]) -> bool:
        record: Dict[str, Any] = {
            "timestamp": reading.get("timestamp", ""),
            "city": reading.get("city", ""),
            "temperature": reading.get("temperature", 0.0),
            "humidity": reading.get("humidity", 0.0),
            "pressure": reading.get("pressure", 0.0),
            "rainfall": reading.get("rainfall", 0.0),
            "alert_level": reading.get("alert_level", "GREEN"),
        }
        try:
            df: pd.DataFrame = pd.DataFrame([record])
            if self.history_file.exists():
                df.to_csv(self.history_file, mode="a", header=False, index=False)
            else:
                self.history_file.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(self.history_file, mode="w", header=True, index=False)
            return True
        except OSError as e:
            logger.error(f"Failed to save reading: {e}")
            return False

    def load_history(self, max_records: Optional[int] = None) -> pd.DataFrame:
        if not self.history_file.exists():
            return pd.DataFrame(columns=HISTORY_COLUMNS)
        try:
            df: pd.DataFrame = pd.read_csv(self.history_file)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            for col in ["temperature", "humidity", "pressure", "rainfall"]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
            if max_records is not None and len(df) > max_records:
                df = df.tail(max_records)
            return df
        except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as e:
            logger.error(f"Failed to load history: {e}")
            return pd.DataFrame(columns=HISTORY_COLUMNS)

    def load_alerts(self, max_lines: int = 100) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        if not self.alert_log_file.exists():
            return records
        try:
            with open(self.alert_log_file, "r", encoding="utf-8") as f:
                lines: List[str] = f.readlines()
            for line in lines[-max_lines:]:
                parts: List[str] = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    records.append({
                        "timestamp": parts[0],
                        "city": parts[1],
                        "rainfall": parts[2],
                        "level": parts[3],
                    })
        except OSError as e:
            logger.error(f"Failed to load alerts: {e}")
        return records

    def load_notifications(self, max_lines: int = 100) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        if not self.notification_log_file.exists():
            return records
        try:
            with open(self.notification_log_file, "r", encoding="utf-8") as f:
                lines: List[str] = f.readlines()
            for line in lines[-max_lines:]:
                parts: List[str] = [p.strip() for p in line.split("|")]
                if len(parts) >= 5:
                    records.append({
                        "timestamp": parts[0],
                        "city": parts[1],
                        "rainfall": parts[2],
                        "level": parts[3],
                        "type": parts[4],
                    })
        except OSError as e:
            logger.error(f"Failed to load notifications: {e}")
        return records

    def get_history_dataframe(self) -> pd.DataFrame:
        return self.load_history()

    def export_to_csv(self) -> bytes:
        df: pd.DataFrame = self.load_history()
        return df.to_csv(index=False).encode("utf-8")

    def export_to_excel(self) -> Optional[bytes]:
        df: pd.DataFrame = self.load_history()
        try:
            output: Path = HISTORY_FILE.parent / "export_temp.xlsx"
            df.to_excel(output, index=False, engine="openpyxl")
            data: bytes = output.read_bytes()
            output.unlink(missing_ok=True)
            return data
        except Exception as e:
            logger.error(f"Excel export failed: {e}")
            return None

    def clear_history(self) -> bool:
        try:
            if self.history_file.exists():
                self.history_file.unlink()
            logger.info("History data cleared.")
            return True
        except OSError as e:
            logger.error(f"Failed to clear history: {e}")
            return False
