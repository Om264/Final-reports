import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import requests

from app.config import (
    API_KEY,
    CITY_LIST,
    FORECAST_API_URL,
    OFFLINE_SETTINGS,
    WEATHER_API_URL,
    ENABLE_OFFLINE_MODE,
)
from app.utils import (
    city_coordinates,
    current_timestamp,
    generate_synthetic_rainfall,
    safe_float,
)

logger = logging.getLogger(__name__)


class WeatherAPI:
    def __init__(self, api_key: str = "", offline_mode: bool = False):
        self.api_key: str = api_key or API_KEY
        self.offline_mode: bool = offline_mode
        self.session: requests.Session = requests.Session()
        self.retries: int = 3
        self.timeout: int = 10
        self._offline_hour_counter: float = 0.0
        self._synth_state: Dict[str, Dict[str, Any]] = {}
        if not self.api_key and not self.offline_mode:
            logger.warning("No API key provided. Offline mode will be used if enabled.")

    def fetch_weather(self, city: str) -> Dict[str, Any]:
        if not city or not city.strip():
            return self._error_response(city, "Invalid city name")
        city = city.strip()

        if self.offline_mode or not self.api_key:
            logger.info(f"Offline mode: generating synthetic data for {city}")
            return self._generate_synthetic(city)

        for attempt in range(1, self.retries + 1):
            try:
                params: Dict[str, Any] = {
                    "q": city,
                    "appid": self.api_key,
                    "units": "metric",
                }
                response: requests.Response = self.session.get(
                    WEATHER_API_URL,
                    params=params,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data: Dict[str, Any] = response.json()
                logger.info(f"Successfully fetched weather data for {city}")
                return self._parse_response(city, data)

            except requests.exceptions.HTTPError as e:
                status_code: int = response.status_code if hasattr(response, "status_code") else 0
                if status_code == 401:
                    logger.error(f"Invalid API key for {city}")
                    if ENABLE_OFFLINE_MODE:
                        return self._generate_synthetic(city)
                    return self._error_response(city, "Invalid API key. Check your OPENWEATHERMAP_API_KEY.")
                elif status_code == 404:
                    logger.error(f"City not found: {city}")
                    return self._error_response(city, f"City '{city}' not found.")
                else:
                    logger.warning(f"HTTP {status_code} for {city}, attempt {attempt}/{self.retries}")
                    if attempt < self.retries:
                        time.sleep(2 ** attempt)
                    else:
                        if ENABLE_OFFLINE_MODE:
                            return self._generate_synthetic(city)
                        return self._error_response(city, f"HTTP error: {e}")

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error for {city}, attempt {attempt}/{self.retries}: {e}")
                if attempt < self.retries:
                    time.sleep(2 ** attempt)
                else:
                    if ENABLE_OFFLINE_MODE:
                        logger.info("Falling back to offline mode due to connection error.")
                        return self._generate_synthetic(city)
                    return self._error_response(city, f"Connection error: {e}")

            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout for {city}, attempt {attempt}/{self.retries}")
                if attempt < self.retries:
                    time.sleep(2 ** attempt)
                else:
                    if ENABLE_OFFLINE_MODE:
                        return self._generate_synthetic(city)
                    return self._error_response(city, f"Timeout: {e}")

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed for {city}: {e}")
                if ENABLE_OFFLINE_MODE:
                    return self._generate_synthetic(city)
                return self._error_response(city, f"Request failed: {e}")

    def fetch_all_cities(self, cities: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        target_cities: List[str] = cities or CITY_LIST
        results: Dict[str, Dict[str, Any]] = {}
        for city in target_cities:
            results[city] = self.fetch_weather(city)
        return results

    def fetch_forecast(self, city: str) -> Dict[str, Any]:
        if not city:
            return {"city": "", "forecasts": [], "error": "Invalid city name"}

        if self.offline_mode or not self.api_key:
            return self._generate_forecast(city)

        try:
            params: Dict[str, Any] = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "cnt": 8,
            }
            response: requests.Response = self.session.get(
                FORECAST_API_URL,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
            forecasts: List[Dict[str, Any]] = []
            for item in data.get("list", []):
                forecasts.append({
                    "timestamp": item.get("dt_txt", ""),
                    "temperature": safe_float(item.get("main", {}).get("temp")),
                    "humidity": safe_float(item.get("main", {}).get("humidity")),
                    "pressure": safe_float(item.get("main", {}).get("pressure")),
                    "rainfall": safe_float(
                        item.get("rain", {}).get("3h", 0.0)
                    ),
                })
            return {"city": city, "forecasts": forecasts, "error": None}
        except requests.exceptions.RequestException as e:
            logger.error(f"Forecast fetch failed for {city}: {e}")
            return self._generate_forecast(city)

    def _parse_response(self, city: str, data: Dict[str, Any]) -> Dict[str, Any]:
        main: Dict[str, Any] = data.get("main", {})
        weather_list: List[Dict[str, Any]] = data.get("weather", [{}])
        rain_data: Dict[str, Any] = data.get("rain", {})

        rainfall: float = safe_float(rain_data.get("1h", rain_data.get("3h", 0.0)))
        if rainfall == 0.0 and any(
            "rain" in (w.get("description", "") or "").lower() for w in weather_list
        ):
            rainfall = round(np.random.default_rng().exponential(scale=2.0, size=1)[0], 2)

        return {
            "city": city,
            "timestamp": current_timestamp(),
            "temperature": safe_float(main.get("temp")),
            "humidity": safe_float(main.get("humidity")),
            "pressure": safe_float(main.get("pressure")),
            "rainfall": rainfall,
            "description": weather_list[0].get("description", "") if weather_list else "",
            "wind_speed": safe_float(data.get("wind", {}).get("speed")),
            "coord": data.get("coord", {}),
            "error": None,
        }

    def _generate_synthetic(self, city: str) -> Dict[str, Any]:
        rng = np.random.default_rng()
        lat, lon = city_coordinates(city)

        if city not in self._synth_state:
            self._synth_state[city] = {
                "base_rainfall": rng.exponential(scale=5.0, size=1)[0],
                "temperature": rng.uniform(15, 35, size=1)[0],
                "humidity": rng.uniform(40, 95, size=1)[0],
                "pressure": rng.uniform(1000, 1025, size=1)[0],
            }

        state = self._synth_state[city]
        rainfall = generate_synthetic_rainfall(
            base=state["base_rainfall"],
            noise_std=OFFLINE_SETTINGS["noise_std"],
            storm_prob=OFFLINE_SETTINGS["storm_probability"],
            hours_since_last=self._offline_hour_counter,
        )
        self._offline_hour_counter += 1.0

        temp_variation = rng.normal(0, 0.5)
        hum_variation = rng.normal(0, 1.0)
        pres_variation = rng.normal(0, 1.0)

        return {
            "city": city,
            "timestamp": current_timestamp(),
            "temperature": round(state["temperature"] + temp_variation, 1),
            "humidity": round(max(0, min(100, state["humidity"] + hum_variation)), 1),
            "pressure": round(state["pressure"] + pres_variation, 1),
            "rainfall": rainfall,
            "description": self._rainfall_description(rainfall),
            "wind_speed": round(rng.exponential(scale=3.0, size=1)[0], 1),
            "coord": {"lat": lat, "lon": lon},
            "error": None,
        }

    def _generate_forecast(self, city: str) -> Dict[str, Any]:
        forecasts: List[Dict[str, Any]] = []
        base = self.fetch_weather(city)
        rng = np.random.default_rng()
        for i in range(8):
            h = (i + 1) * 3
            forecasts.append({
                "timestamp": (
                    datetime.now().replace(minute=0, second=0, microsecond=0)
                    if i == 0
                    else datetime.now().replace(minute=0, second=0, microsecond=0)
                )
                .strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": safe_float(base.get("temperature", 20)) + rng.normal(0, 1.0),
                "humidity": safe_float(base.get("humidity", 60)) + rng.normal(0, 2.0),
                "pressure": safe_float(base.get("pressure", 1013)) + rng.normal(0, 2.0),
                "rainfall": generate_synthetic_rainfall(
                    base=safe_float(base.get("rainfall", 5.0)),
                    noise_std=2.0,
                    storm_prob=0.03,
                    hours_since_last=h,
                ),
            })
        return {"city": city, "forecasts": forecasts, "error": None}

    @staticmethod
    def _rainfall_description(rainfall: float) -> str:
        if rainfall < 0.5:
            return "clear sky"
        elif rainfall < 2.5:
            return "light rain"
        elif rainfall < 8.0:
            return "moderate rain"
        elif rainfall < 16.0:
            return "heavy rain"
        else:
            return "violent rain"

    @staticmethod
    def _error_response(city: str, message: str) -> Dict[str, Any]:
        return {
            "city": city,
            "timestamp": current_timestamp(),
            "temperature": 0.0,
            "humidity": 0.0,
            "pressure": 0.0,
            "rainfall": 0.0,
            "description": "Error",
            "wind_speed": 0.0,
            "coord": {"lat": 0.0, "lon": 0.0},
            "error": message,
        }

    def validate_api_key(self) -> bool:
        if not self.api_key:
            return False
        try:
            params = {"q": "Beijing", "appid": self.api_key, "units": "metric"}
            response = self.session.get(WEATHER_API_URL, params=params, timeout=10)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
