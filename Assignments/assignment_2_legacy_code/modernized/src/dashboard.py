import asyncio
from .fetcher import WeatherFetcher
from .alerts import AlertEngine
from .logger import AlertLogger


class RainfallDashboard:
    def __init__(
        self,
        api_key: str,
        lat: float = 39.9,
        lon: float = 116.4,
        threshold: float = 20.0,
        poll_seconds: int = 300,
    ) -> None:
        self.fetcher = WeatherFetcher(api_key, lat, lon)
        self.alerts = AlertEngine(threshold)
        self.logger = AlertLogger()
        self.poll_seconds = poll_seconds
        self.alerts.subscribe(self.logger.log_alert)
        self.alerts.subscribe(self._console_alert)

    @staticmethod
    def _console_alert(event: object) -> None:
        print(f"!!! RED WARNING: {event.rainfall} mm/h exceeds threshold !!!")

    async def run_forever(self) -> None:
        async with self.fetcher:
            while True:
                data = await self.fetcher.fetch_current()
                print(f"[{data.city}] Rainfall: {data.rainfall_1h} mm/h")
                event = await self.alerts.evaluate(data)
                if event is None:
                    print("Status: OK")
                await asyncio.sleep(self.poll_seconds)
