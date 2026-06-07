import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from app.config import HISTORY_FILE, MODEL_FILE, MODEL_SETTINGS

logger = logging.getLogger(__name__)


class RainfallPredictor:
    def __init__(self, model_path: Path = MODEL_FILE, history_file: Optional[Path] = None):
        self.model_path: Path = model_path
        self.history_file: Path = history_file or HISTORY_FILE
        self.model: Optional[LinearRegression] = None
        self._feature_columns: List[str] = [
            "temperature",
            "humidity",
            "pressure",
            "rainfall_lag1",
            "rainfall_lag2",
            "rainfall_lag3",
        ]
        self._is_trained: bool = False
        self._training_metrics: Dict[str, float] = {}
        self._load_model()

    def _load_model(self) -> None:
        if self.model_path.exists():
            try:
                self.model = joblib.load(self.model_path)
                self._is_trained = True
                logger.info(f"Model loaded from {self.model_path}")
            except (joblib.JoblibError, EOFError, ValueError) as e:
                logger.warning(f"Could not load model from {self.model_path}: {e}")
                self.model = None
                self._is_trained = False

    def save_model(self) -> None:
        if self.model is None:
            logger.warning("No model to save.")
            return
        try:
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info(f"Model saved to {self.model_path}")
        except OSError as e:
            logger.error(f"Failed to save model: {e}")

    def train_model(self, force: bool = False) -> Dict[str, float]:
        df: pd.DataFrame = self._load_training_data()
        if df.empty:
            logger.warning("No training data available.")
            return {}

        if not force and len(df) < int(MODEL_SETTINGS["retrain_threshold"]):
            logger.info(
                f"Insufficient data for retraining: {len(df)} < "
                f"{MODEL_SETTINGS['retrain_threshold']}"
            )
            if self._is_trained:
                return self._training_metrics

        df_features: pd.DataFrame = self._engineer_features(df)
        df_features = df_features.dropna()
        if len(df_features) < 10:
            logger.warning(f"Too few samples ({len(df_features)}) after feature engineering.")
            return {}

        feature_cols: List[str] = [c for c in self._feature_columns if c in df_features.columns]
        if not feature_cols:
            logger.warning("No feature columns available.")
            return {}

        X: np.ndarray = df_features[feature_cols].values
        y: np.ndarray = df_features["rainfall_target"].values

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=float(MODEL_SETTINGS["test_size"]),
            random_state=int(MODEL_SETTINGS["random_state"]),
        )
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)

        y_pred: np.ndarray = self.model.predict(X_test)
        self._training_metrics = {
            "r2_score": float(r2_score(y_test, y_pred)),
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "rmse": float(np.sqrt(mean_squared_error(y_test, y_pred))),
            "samples": len(df_features),
        }
        self._is_trained = True
        logger.info(f"Model trained. R2: {self._training_metrics['r2_score']:.3f}")
        self.save_model()
        return self._training_metrics

    def predict(self, features: Dict[str, float]) -> Dict[str, Any]:
        if self.model is None or not self._is_trained:
            return self._fallback_prediction(features)

        feature_vector: np.ndarray = self._build_feature_vector(features)
        if feature_vector is None or np.any(np.isnan(feature_vector)):
            return self._fallback_prediction(features)

        try:
            base_pred: float = float(self.model.predict(feature_vector.reshape(1, -1))[0])
            base_pred = max(0, base_pred)
            pred_1h: float = round(base_pred, 2)
            pred_3h: float = round(base_pred * 1.5 + np.random.default_rng().normal(0, 0.5), 2)
            confidence: float = max(0, min(1, float(self._training_metrics.get("r2_score", 0))))
            trend: str = "increasing" if pred_3h > pred_1h * 1.1 else "decreasing" if pred_3h < pred_1h * 0.9 else "stable"
            return {
                "prediction_1h": max(0, pred_1h),
                "prediction_3h": max(0, pred_3h),
                "confidence": round(confidence, 3),
                "trend": trend,
                "source": "ml_model",
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return self._fallback_prediction(features)

    def predict_with_uncertainty(self, features: Dict[str, float]) -> Dict[str, Any]:
        result: Dict[str, Any] = self.predict(features)
        if result["source"] == "ml_model":
            std_est: float = float(self._training_metrics.get("rmse", 2.0))
            result["prediction_1h_lower"] = round(max(0, result["prediction_1h"] - 1.96 * std_est), 2)
            result["prediction_1h_upper"] = round(result["prediction_1h"] + 1.96 * std_est, 2)
        return result

    def _fallback_prediction(self, features: Dict[str, float]) -> Dict[str, Any]:
        current: float = features.get("rainfall", 0.0)
        rng = np.random.default_rng()
        pred_1h: float = max(0, current * 0.8 + rng.normal(0, 1.0))
        pred_3h: float = max(0, current * 1.2 + rng.normal(0, 2.0))
        trend: str = "stable"
        if pred_3h > pred_1h * 1.2:
            trend = "increasing"
        elif pred_3h < pred_1h * 0.8:
            trend = "decreasing"
        return {
            "prediction_1h": round(pred_1h, 2),
            "prediction_3h": round(pred_3h, 2),
            "confidence": 0.3,
            "trend": trend,
            "source": "fallback",
        }

    def _load_training_data(self) -> pd.DataFrame:
        if not self.history_file.exists():
            return pd.DataFrame()
        try:
            df: pd.DataFrame = pd.read_csv(self.history_file)
            df["rainfall"] = pd.to_numeric(df["rainfall"], errors="coerce")
            df["temperature"] = pd.to_numeric(df["temperature"], errors="coerce")
            df["humidity"] = pd.to_numeric(df["humidity"], errors="coerce")
            df["pressure"] = pd.to_numeric(df["pressure"], errors="coerce")
            return df.dropna(subset=["rainfall", "temperature", "humidity", "pressure"])
        except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as e:
            logger.error(f"Failed to load training data: {e}")
            return pd.DataFrame()

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df_sorted: pd.DataFrame = df.sort_values("timestamp").copy()
        df_sorted["rainfall_lag1"] = df_sorted["rainfall"].shift(1)
        df_sorted["rainfall_lag2"] = df_sorted["rainfall"].shift(2)
        df_sorted["rainfall_lag3"] = df_sorted["rainfall"].shift(3)
        df_sorted["rainfall_target"] = df_sorted["rainfall"].shift(-1)
        return df_sorted

    def _build_feature_vector(self, features: Dict[str, float]) -> Optional[np.ndarray]:
        try:
            vector: List[float] = [
                features.get("temperature", 20.0),
                features.get("humidity", 60.0),
                features.get("pressure", 1013.0),
                features.get("rainfall_lag1", features.get("rainfall", 0.0)),
                features.get("rainfall_lag2", features.get("rainfall", 0.0)),
                features.get("rainfall_lag3", features.get("rainfall", 0.0)),
            ]
            return np.array(vector, dtype=np.float64)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to build feature vector: {e}")
            return None

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "is_trained": self._is_trained,
            "model_exists": self.model_path.exists(),
            "model_path": str(self.model_path),
            "metrics": self._training_metrics,
            "feature_columns": self._feature_columns,
        }
