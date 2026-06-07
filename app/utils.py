import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def rainfall_to_alert_level(rainfall: float, thresholds: Dict[str, float]) -> str:
    if rainfall >= thresholds["yellow_max"]:
        return "RED"
    elif rainfall >= thresholds["green_max"]:
        return "YELLOW"
    return "GREEN"


def alert_color(level: str) -> str:
    colors = {
        "GREEN": "#00cc00",
        "YELLOW": "#ffcc00",
        "RED": "#ff3333",
    }
    return colors.get(level, "#999999")


def moving_average(values: List[float], window: int = 3) -> List[Optional[float]]:
    if not values or window < 1:
        return []
    series = pd.Series(values)
    return series.rolling(window=window, min_periods=1).mean().tolist()


def generate_synthetic_rainfall(
    base: float = 5.0,
    noise_std: float = 3.0,
    storm_prob: float = 0.05,
    hours_since_last: float = 0.0,
) -> float:
    rng = np.random.default_rng()

    if rng.random() < storm_prob:
        rainfall = base + rng.exponential(scale=15.0, size=1)[0]
    else:
        diurnal_factor = 1.0 + 0.3 * np.sin(2 * np.pi * (hours_since_last / 24) - np.pi / 2)
        rainfall = max(0, base * diurnal_factor + rng.normal(0, noise_std))

    return round(rainfall, 2)


def city_coordinates(city: str) -> tuple:
    coords = {
        "Beijing": (39.9042, 116.4074),
        "Shanghai": (31.2304, 121.4737),
        "Guangzhou": (23.1291, 113.2644),
        "Shenzhen": (22.5431, 114.0579),
        "Wuhan": (30.5928, 114.3055),
    }
    return coords.get(city, (0.0, 0.0))
