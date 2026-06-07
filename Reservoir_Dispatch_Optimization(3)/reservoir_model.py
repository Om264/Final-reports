import numpy as np
from typing import Tuple

SECONDS_PER_DAY: int = 86400
INITIAL_STORAGE: float = 500_000.0
MIN_STORAGE: float = 100_000.0
MAX_STORAGE: float = 1_000_000.0
ECOLOGICAL_RELEASE: float = 10.0
MAX_RELEASE: float = 100.0
INFLOW: np.ndarray = np.array([15, 12, 10, 8, 12, 15, 18], dtype=float)
HYDROPOWER_PRICE: np.ndarray = np.array([0.08, 0.08, 0.08, 0.08, 0.10, 0.12, 0.10], dtype=float)
HYDROPOWER_CONVERSION: float = 5000.0
NUM_DAYS: int = 7


def simulate_storage(releases: np.ndarray) -> np.ndarray:
    storage = np.zeros(NUM_DAYS + 1, dtype=float)
    storage[0] = INITIAL_STORAGE
    for t in range(NUM_DAYS):
        net_volume = (INFLOW[t] - releases[t]) * SECONDS_PER_DAY
        storage[t + 1] = storage[t] + net_volume
    return storage


def calculate_revenue(releases: np.ndarray) -> float:
    daily_revenue = releases * HYDROPOWER_PRICE * HYDROPOWER_CONVERSION
    return float(np.sum(daily_revenue))


def calculate_ecological_deficit(releases: np.ndarray) -> float:
    deficits = np.maximum(0.0, ECOLOGICAL_RELEASE - releases)
    return float(np.sum(deficits))


REVENUE_SCALE: float = 50000.0
DEFICIT_SCALE: float = 70.0


def compute_objective(
    releases: np.ndarray,
    w_revenue: float = 1.0,
    w_ecology: float = 0.0,
) -> float:
    revenue = calculate_revenue(releases)
    deficit = calculate_ecological_deficit(releases)
    revenue_norm = revenue / REVENUE_SCALE
    deficit_norm = deficit / DEFICIT_SCALE
    return -w_revenue * revenue_norm + w_ecology * deficit_norm
