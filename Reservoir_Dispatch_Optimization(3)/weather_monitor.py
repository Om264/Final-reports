import logging
import sys
from typing import List, Optional

from app.alert_system import AlertSystem
from app.anomaly_detector import AnomalyDetector
from app.config import CITY_LIST, validate_config
from app.data_storage import DataStorage
from app.notification import NotificationService
from app.predictor import RainfallPredictor
from app.utils import setup_logging
from app.weather_api import WeatherAPI


def run_cli() -> None:
    setup_logging("INFO")
    logger: logging.Logger = logging.getLogger(__name__)
    logger.info("Starting Rainfall Monitor CLI mode.")

    config_errors: List[str] = validate_config()
    for err in config_errors:
        logger.warning(err)

    wapi: WeatherAPI = WeatherAPI()
    alert_system: AlertSystem = AlertSystem()
    predictor: RainfallPredictor = RainfallPredictor()
    detector: AnomalyDetector = AnomalyDetector()
    notification_service: NotificationService = NotificationService()
    data_store: DataStorage = DataStorage()

    if wapi.api_key:
        if wapi.validate_api_key():
            logger.info("API key validated successfully.")
        else:
            logger.warning("API key validation failed. Falling back to offline mode.")
            wapi.offline_mode = True
    else:
        logger.info("No API key found. Using offline mode.")
        wapi.offline_mode = True

    logger.info(f"Monitoring cities: {', '.join(CITY_LIST)}")

    all_data = wapi.fetch_all_cities(CITY_LIST)
    for city, data in all_data.items():
        rainfall: float = data.get("rainfall", 0.0)
        logger.info(f"{city}: {rainfall:.2f} mm/h, {data.get('temperature', 0):.1f}°C")

        level, status = alert_system.evaluate(rainfall, city)
        data["alert_level"] = level
        data_store.save_reading(data)

        anomaly_result = detector.detect(rainfall, city)
        if anomaly_result["is_anomaly"]:
            logger.warning(f"Anomaly in {city}: {anomaly_result['description']}")

        if level == "RED":
            logger.warning(f"RED ALERT: {city} - {rainfall:.2f} mm/h")
            notification_service.send_alert_notification(
                city=city,
                rainfall=rainfall,
                alert_level=level,
            )
        elif level == "YELLOW":
            logger.warning(f"YELLOW WARNING: {city} - {rainfall:.2f} mm/h")

    summary = alert_system.alert_summary()
    logger.info(f"Alert summary: GREEN={summary['GREEN']}, YELLOW={summary['YELLOW']}, RED={summary['RED']}")

    predictor.train_model()

    for city in CITY_LIST:
        city_data = all_data.get(city, {})
        if city_data and not city_data.get("error"):
            features = {
                "temperature": city_data.get("temperature", 20.0),
                "humidity": city_data.get("humidity", 60.0),
                "pressure": city_data.get("pressure", 1013.0),
                "rainfall": city_data.get("rainfall", 0.0),
                "rainfall_lag1": city_data.get("rainfall", 0.0),
                "rainfall_lag2": city_data.get("rainfall", 0.0),
                "rainfall_lag3": city_data.get("rainfall", 0.0),
            }
            prediction = predictor.predict(features)
            logger.info(
                f"{city} forecast: 1h={prediction['prediction_1h']:.2f}mm/h, "
                f"3h={prediction['prediction_3h']:.2f}mm/h, "
                f"trend={prediction['trend']}, "
                f"confidence={prediction['confidence']:.1%}"
            )

    logger.info("CLI run complete.")


def run_dashboard() -> None:
    from app.dashboard import run_dashboard as _run_dashboard
    _run_dashboard()


def main() -> None:
    setup_logging("INFO")
    logger: logging.Logger = logging.getLogger(__name__)
    config_errors: List[str] = validate_config()
    for err in config_errors:
        logger.warning(err)

    args: List[str] = sys.argv[1:]
    if "--cli" in args:
        run_cli()
    else:
        logger.info("Starting Streamlit dashboard...")
        print("Starting Streamlit dashboard. Use --cli for command-line mode.")
        print("Run: streamlit run weather_monitor.py")
        run_dashboard()


if __name__ == "__main__":
    main()
