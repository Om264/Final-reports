import logging
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from app.config import HISTORY_FILE

logger = logging.getLogger(__name__)


class AnomalyDetector:
    def __init__(self, z_threshold: float = 2.0):
        self.z_threshold: float = z_threshold
        self._historical_mean: float = 5.0
        self._historical_std: float = 5.0
        self._update_statistics()

    def _update_statistics(self) -> None:
        if not HISTORY_FILE.exists():
            return
        try:
            df: pd.DataFrame = pd.read_csv(HISTORY_FILE)
            rainfall: pd.Series = pd.to_numeric(df["rainfall"], errors="coerce").dropna()
            if len(rainfall) >= 5:
                self._historical_mean = float(rainfall.mean())
                self._historical_std = float(rainfall.std())
                if self._historical_std < 0.1:
                    self._historical_std = 0.5
        except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as e:
            logger.warning(f"Cannot update anomaly statistics: {e}")

    def detect(self, rainfall: float, city: str) -> Dict[str, Any]:
        z_score: float = (
            (rainfall - self._historical_mean) / self._historical_std
            if self._historical_std > 0
            else 0.0
        )
        is_anomaly: bool = abs(z_score) >= self.z_threshold
        severity: str = (
            "extreme"
            if abs(z_score) > 3
            else "high"
            if abs(z_score) > self.z_threshold
            else "normal"
        )

        description: str = self._describe_anomaly(rainfall, z_score, is_anomaly)

        return {
            "city": city,
            "rainfall": rainfall,
            "z_score": round(z_score, 3),
            "is_anomaly": is_anomaly,
            "severity": severity,
            "description": description,
            "historical_mean": round(self._historical_mean, 2),
            "historical_std": round(self._historical_std, 2),
        }

    def detect_batch(
        self, readings: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        results: Dict[str, List[Dict[str, Any]]] = {
            "anomalies": [],
            "all": [],
        }
        for reading in readings:
            rainfall: float = reading.get("rainfall", 0.0)
            city: str = reading.get("city", "Unknown")
            result: Dict[str, Any] = self.detect(rainfall, city)
            results["all"].append(result)
            if result["is_anomaly"]:
                results["anomalies"].append(result)
        return results

    def batch_detect_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or "rainfall" not in df.columns:
            return df
        result: pd.DataFrame = df.copy()
        rainfall_vals: pd.Series = pd.to_numeric(result["rainfall"], errors="coerce")
        mean_val: float = rainfall_vals.mean() if len(rainfall_vals) > 0 else 0
        std_val: float = rainfall_vals.std() if len(rainfall_vals) > 0 else 1
        if std_val < 0.1:
            std_val = 0.5
        result["z_score"] = (rainfall_vals - mean_val) / std_val
        result["is_anomaly"] = abs(result["z_score"]) >= self.z_threshold
        return result

    def summary(self) -> Dict[str, Any]:
        return {
            "z_threshold": self.z_threshold,
            "historical_mean": round(self._historical_mean, 2),
            "historical_std": round(self._historical_std, 2),
        }

    @staticmethod
    def _describe_anomaly(rainfall: float, z_score: float, is_anomaly: bool) -> str:
        if not is_anomaly:
            return "Normal rainfall pattern."
        if rainfall < 0.5 and z_score < -2:
            return f"Unusually dry conditions (z={z_score:.2f})."
        if z_score > 3:
            return (
                f"EXTREME rainfall event! Rainfall {rainfall:.1f} mm/h "
                f"is highly unusual (z={z_score:.2f})."
            )
        if z_score > 2:
            return (
                f"High rainfall anomaly detected: {rainfall:.1f} mm/h "
                f"(z={z_score:.2f}). Potential flood risk."
            )
        return f"Anomalous pattern detected (z={z_score:.2f})."
