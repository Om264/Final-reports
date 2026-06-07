import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from app.weather_api import WeatherAPI


class TestWeatherAPI(unittest.TestCase):
    def setUp(self) -> None:
        self.api = WeatherAPI(api_key="test_key", offline_mode=False)

    def test_fetch_weather_invalid_city(self) -> None:
        result = self.api.fetch_weather("")
        self.assertIsNotNone(result.get("error"))

    def test_fetch_weather_offline_mode(self) -> None:
        self.api.offline_mode = True
        result = self.api.fetch_weather("Beijing")
        self.assertIsNone(result.get("error"))
        self.assertIn("rainfall", result)
        self.assertIn("temperature", result)
        self.assertIn("humidity", result)
        self.assertGreaterEqual(result["rainfall"], 0)

    def test_offline_generates_valid_data(self) -> None:
        self.api.offline_mode = True
        result = self.api.fetch_weather("Shanghai")
        self.assertIsNone(result.get("error"))
        self.assertEqual(result["city"], "Shanghai")

    @patch("app.weather_api.requests.Session.get")
    @patch("app.weather_api.ENABLE_OFFLINE_MODE", False)
    def test_api_error_handling_401(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = __import__("requests").exceptions.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response
        self.api.offline_mode = False
        result = self.api.fetch_weather("Beijing")
        self.assertIsNotNone(result.get("error"))

    @patch("app.weather_api.requests.Session.get")
    def test_api_error_handling_404(self, mock_get: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = __import__("requests").exceptions.HTTPError(
            response=mock_response
        )
        mock_get.return_value = mock_response
        self.api.offline_mode = False
        result = self.api.fetch_weather("NonExistentCity")
        self.assertIsNotNone(result.get("error"))

    def test_fetch_all_cities(self) -> None:
        self.api.offline_mode = True
        results = self.api.fetch_all_cities(["Beijing", "Shanghai"])
        self.assertEqual(len(results), 2)
        for city, data in results.items():
            self.assertIn("rainfall", data)
            self.assertIsNone(data.get("error"))

    def test_synthetic_rainfall_range(self) -> None:
        self.api.offline_mode = True
        rainfalls = []
        for _ in range(100):
            result = self.api.fetch_weather("Beijing")
            rainfalls.append(result["rainfall"])
        self.assertGreater(len([r for r in rainfalls if r >= 0]), 90)

    def test_fetch_forecast_offline(self) -> None:
        self.api.offline_mode = True
        forecast = self.api.fetch_forecast("Beijing")
        self.assertIn("forecasts", forecast)
        self.assertGreater(len(forecast["forecasts"]), 0)

    def test_validate_api_key_invalid(self) -> None:
        self.api.api_key = ""
        self.assertFalse(self.api.validate_api_key())

    def test_rainfall_description(self) -> None:
        self.assertEqual(self.api._rainfall_description(0.1), "clear sky")
        self.assertEqual(self.api._rainfall_description(1.0), "light rain")
        self.assertEqual(self.api._rainfall_description(5.0), "moderate rain")
        self.assertEqual(self.api._rainfall_description(12.0), "heavy rain")
        self.assertEqual(self.api._rainfall_description(20.0), "violent rain")


if __name__ == "__main__":
    unittest.main()
