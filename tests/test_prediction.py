import tempfile
import unittest
from pathlib import Path

import pandas as pd

from app.predictor import RainfallPredictor


class TestRainfallPredictor(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.model_path = Path(self.temp_dir) / "test_model.pkl"
        self.history_path = Path(self.temp_dir) / "test_history.csv"
        self.predictor = RainfallPredictor(model_path=self.model_path, history_file=self.history_path)

    def _create_test_data(self, n: int = 100) -> None:
        import numpy as np
        rng = np.random.default_rng(42)
        data = {
            "timestamp": [f"2024-01-01 {h:02d}:00:00" for h in range(n)],
            "city": ["Beijing"] * n,
            "temperature": list(20 + rng.normal(0, 5, n)),
            "humidity": list(60 + rng.normal(0, 10, n)),
            "pressure": list(1013 + rng.normal(0, 5, n)),
            "rainfall": list(np.abs(rng.exponential(scale=5, size=n))),
            "alert_level": ["GREEN"] * n,
        }
        df = pd.DataFrame(data)
        df.to_csv(self.history_path, index=False)

    def test_initial_model_not_trained(self) -> None:
        model_info = self.predictor.get_model_info()
        self.assertFalse(model_info["is_trained"])

    def test_fallback_prediction_when_no_model(self) -> None:
        features = {
            "temperature": 25.0,
            "humidity": 70.0,
            "pressure": 1010.0,
            "rainfall": 5.0,
            "rainfall_lag1": 4.0,
            "rainfall_lag2": 3.0,
            "rainfall_lag3": 2.0,
        }
        prediction = self.predictor.predict(features)
        self.assertIn("prediction_1h", prediction)
        self.assertIn("prediction_3h", prediction)
        self.assertIn("trend", prediction)
        self.assertEqual(prediction["source"], "fallback")

    def test_train_model_with_data(self) -> None:
        self._create_test_data(100)
        self.predictor.train_model(force=True)
        model_info = self.predictor.get_model_info()
        self.assertTrue(model_info["is_trained"])
        self.assertIn("r2_score", model_info["metrics"])

    def test_prediction_after_training(self) -> None:
        self._create_test_data(100)
        self.predictor.train_model(force=True)
        features = {
            "temperature": 25.0,
            "humidity": 70.0,
            "pressure": 1010.0,
            "rainfall": 8.0,
            "rainfall_lag1": 7.0,
            "rainfall_lag2": 6.0,
            "rainfall_lag3": 5.0,
        }
        prediction = self.predictor.predict(features)
        self.assertIn("prediction_1h", prediction)
        self.assertIn("prediction_3h", prediction)
        self.assertGreaterEqual(prediction["prediction_1h"], 0)
        self.assertGreaterEqual(prediction["prediction_3h"], 0)

    def test_prediction_with_uncertainty(self) -> None:
        self._create_test_data(100)
        self.predictor.train_model(force=True)
        features = {
            "temperature": 25.0,
            "humidity": 70.0,
            "pressure": 1010.0,
            "rainfall": 8.0,
            "rainfall_lag1": 7.0,
            "rainfall_lag2": 6.0,
            "rainfall_lag3": 5.0,
        }
        result = self.predictor.predict_with_uncertainty(features)
        self.assertIn("prediction_1h_lower", result)
        self.assertIn("prediction_1h_upper", result)
        self.assertLessEqual(result["prediction_1h_lower"], result["prediction_1h_upper"])

    def test_insufficient_data_no_retrain(self) -> None:
        self._create_test_data(5)
        metrics = self.predictor.train_model(force=False)
        self.assertEqual(metrics, {})

    def test_save_and_load_model(self) -> None:
        self._create_test_data(100)
        self.predictor.train_model(force=True)
        self.assertTrue(self.model_path.exists())

        new_predictor = RainfallPredictor(model_path=self.model_path)
        model_info = new_predictor.get_model_info()
        self.assertTrue(model_info["is_trained"])

    def test_get_model_info_structure(self) -> None:
        info = self.predictor.get_model_info()
        self.assertIn("is_trained", info)
        self.assertIn("model_exists", info)
        self.assertIn("model_path", info)
        self.assertIn("metrics", info)
        self.assertIn("feature_columns", info)


if __name__ == "__main__":
    unittest.main()
