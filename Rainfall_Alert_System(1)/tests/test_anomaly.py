import tempfile
import unittest
from pathlib import Path

import pandas as pd

from app.anomaly_detector import AnomalyDetector


class TestAnomalyDetector(unittest.TestCase):
    def setUp(self) -> None:
        self.detector = AnomalyDetector(z_threshold=2.0)

    def test_normal_rainfall_no_anomaly(self) -> None:
        result = self.detector.detect(5.0, "Beijing")
        self.assertFalse(result["is_anomaly"])
        self.assertEqual(result["severity"], "normal")

    def test_high_rainfall_anomaly(self) -> None:
        result = self.detector.detect(50.0, "Beijing")
        self.assertTrue(result["is_anomaly"])
        self.assertIn(result["severity"], ("high", "extreme"))

    def test_extreme_rainfall_z_score(self) -> None:
        result = self.detector.detect(100.0, "Beijing")
        self.assertTrue(result["is_anomaly"])
        self.assertGreater(abs(result["z_score"]), 2)

    def test_anomaly_result_structure(self) -> None:
        result = self.detector.detect(10.0, "Shanghai")
        required_keys = [
            "city", "rainfall", "z_score", "is_anomaly",
            "severity", "description", "historical_mean", "historical_std",
        ]
        for key in required_keys:
            self.assertIn(key, result)

    def test_batch_detect_finds_anomalies(self) -> None:
        readings = [
            {"city": "Beijing", "rainfall": 5.0},
            {"city": "Shanghai", "rainfall": 3.0},
            {"city": "Guangzhou", "rainfall": 60.0},
            {"city": "Shenzhen", "rainfall": 2.0},
        ]
        results = self.detector.detect_batch(readings)
        self.assertIn("anomalies", results)
        self.assertIn("all", results)
        self.assertGreaterEqual(len(results["anomalies"]), 1)

    def test_batch_detect_all_normal(self) -> None:
        readings = [
            {"city": "Beijing", "rainfall": 5.0},
            {"city": "Shanghai", "rainfall": 3.0},
            {"city": "Guangzhou", "rainfall": 4.0},
        ]
        results = self.detector.detect_batch(readings)
        self.assertEqual(len(results["all"]), 3)

    def test_detect_dataframe(self) -> None:
        df = pd.DataFrame({
            "city": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11"],
            "rainfall": [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 200.0],
            "temperature": [20.0] * 11,
        })
        result = self.detector.batch_detect_dataframe(df)
        self.assertIn("z_score", result.columns)
        self.assertIn("is_anomaly", result.columns)
        self.assertTrue(result["is_anomaly"].iloc[10])

    def test_summary(self) -> None:
        summary = self.detector.summary()
        self.assertIn("z_threshold", summary)
        self.assertIn("historical_mean", summary)
        self.assertIn("historical_std", summary)

    def test_description_normal(self) -> None:
        desc = self.detector._describe_anomaly(5.0, 0.5, False)
        self.assertEqual(desc, "Normal rainfall pattern.")

    def test_description_extreme(self) -> None:
        desc = self.detector._describe_anomaly(80.0, 4.5, True)
        self.assertIn("EXTREME", desc)

    def test_custom_threshold(self) -> None:
        detector = AnomalyDetector(z_threshold=1.0)
        result = detector.detect(10.0, "Beijing")
        self.assertTrue(result["is_anomaly"])

    def test_zero_std_fallback(self) -> None:
        detector = AnomalyDetector(z_threshold=2.0)
        detector._historical_std = 0.0
        result = detector.detect(5.0, "Beijing")
        self.assertFalse(result["is_anomaly"])


if __name__ == "__main__":
    unittest.main()
