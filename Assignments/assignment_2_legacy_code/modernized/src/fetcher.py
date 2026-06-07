from dataclasses import dataclass
from typing import Optional
import httpx


@dataclass
class WeatherData:
    rainfall_1h: float
    rainfall_3h: Optional[float]
    city: str
    timestamp: int


class WeatherFetcher:
    def __init__(self, api_key: str, lat: float, lon: float) -> None:
        self.api_key = api_key
        self.lat = lat
        self.lon = lon
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "WeatherFetcher":
        self._client = httpx.AsyncClient()
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._client:
            await self._client.aclose()

    async def fetch_current(self) -> WeatherData:
        if not self._client:
            raise RuntimeError("Use 'async with WeatherFetcher(...)'")
        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?lat={self.lat}&lon={self.lon}"
            f"&appid={self.api_key}&units=metric"
        )
        resp = await self._client.get(url, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        rain = data.get("rain", {}) or {}
        return WeatherData(
            rainfall_1h=rain.get("1h", 0.0),
            rainfall_3h=rain.get("3h"),
            city=data.get("name", "unknown"),
            timestamp=data.get("dt", 0),
        )
