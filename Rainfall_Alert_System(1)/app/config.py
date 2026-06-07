import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

API_KEY: str = os.getenv("OPENWEATHERMAP_API_KEY", "")
WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_API_URL: str = "https://api.openweathermap.org/data/2.5/forecast"

REFRESH_INTERVAL: int = int(os.getenv("REFRESH_INTERVAL", "300"))

ALERT_THRESHOLDS: Dict[str, float] = {
    "green_max": 10.0,
    "yellow_max": 20.0,
}

CITY_LIST: List[str] = [
    "Beijing",
    "Shanghai",
    "Guangzhou",
    "Shenzhen",
    "Wuhan",
]

ALERT_LOG_FILE: Path = DATA_DIR / "alert_log.txt"
HISTORY_FILE: Path = DATA_DIR / "rainfall_history.csv"
NOTIFICATION_LOG_FILE: Path = DATA_DIR / "notification_log.txt"
MODEL_FILE: Path = MODELS_DIR / "rainfall_model.pkl"

EMAIL_SETTINGS: Dict[str, Optional[str]] = {
    "smtp_server": os.getenv("SMTP_SERVER"),
    "smtp_port": os.getenv("SMTP_PORT"),
    "sender_email": os.getenv("SENDER_EMAIL"),
    "sender_password": os.getenv("SENDER_PASSWORD"),
    "receiver_email": os.getenv("RECEIVER_EMAIL"),
}

SMS_SETTINGS: Dict[str, Optional[str]] = {
    "twilio_account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
    "twilio_auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
    "twilio_phone_number": os.getenv("TWILIO_PHONE_NUMBER"),
    "receiver_phone": os.getenv("RECEIVER_PHONE"),
}

MODEL_SETTINGS: Dict[str, object] = {
    "model_type": "linear_regression",
    "retrain_threshold": int(os.getenv("RETRAIN_THRESHOLD", "50")),
    "test_size": 0.2,
    "random_state": 42,
}

ENABLE_EMAIL: bool = os.getenv("ENABLE_EMAIL", "false").lower() == "true"
ENABLE_SMS: bool = os.getenv("ENABLE_SMS", "false").lower() == "true"
ENABLE_OFFLINE_MODE: bool = os.getenv("ENABLE_OFFLINE_MODE", "true").lower() == "true"

OFFLINE_SETTINGS: Dict[str, object] = {
    "base_rainfall": float(os.getenv("OFFLINE_BASE_RAINFALL", "5.0")),
    "noise_std": float(os.getenv("OFFLINE_NOISE_STD", "3.0")),
    "storm_probability": float(os.getenv("OFFLINE_STORM_PROB", "0.05")),
}

HISTORY_COLUMNS: List[str] = [
    "timestamp",
    "city",
    "temperature",
    "humidity",
    "pressure",
    "rainfall",
    "alert_level",
]

def validate_config() -> List[str]:
    errors: List[str] = []
    if not API_KEY:
        errors.append("OPENWEATHERMAP_API_KEY is not set. Offline mode will be used.")
    if REFRESH_INTERVAL < 60:
        errors.append("REFRESH_INTERVAL is too low (< 60s). Using 60s minimum.")
    return errors
