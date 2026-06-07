import numpy as np


def generate_synthetic_dem(
    nrows: int = 100,
    ncols: int = 100,
    min_elev: float = 30.0,
    max_elev: float = 80.0,
    seed: int | None = 42,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.uniform(min_elev, max_elev, (nrows, ncols))


def generate_valley_dem(nrows: int = 100, ncols: int = 100) -> np.ndarray:
    x = np.linspace(0, 1, ncols)
    y = np.linspace(0, 1, nrows)
    xx, yy = np.meshgrid(x, y)
    dem = 80 - 50 * (1 - np.sqrt((xx - 0.5)**2 + (yy - 0.5)**2) * 2)
    return np.clip(dem, 30, 80)
