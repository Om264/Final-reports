import numpy as np
import logging
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)


def load_dem(filepath: Optional[str] = None) -> np.ndarray:
    """Load or generate DEM data.

    Parameters
    ----------
    filepath : str, optional
        Path to DEM file (.npy, .tif, .asc). If None, generate synthetic DEM.

    Returns
    -------
    np.ndarray
        2D array of elevation values in meters.
    """
    if filepath is not None:
        return load_real_dem(filepath)
    return generate_synthetic_dem()


def generate_synthetic_dem(
    shape: Tuple[int, int] = (100, 100),
    method: str = "terrain",
    seed: int = 42
) -> np.ndarray:
    """Generate synthetic DEM data.

    Parameters
    ----------
    shape : tuple
        Grid dimensions (rows, cols).
    method : str
        One of 'terrain', 'slope', 'valley'.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    np.ndarray
        2D elevation array.
    """
    rng = np.random.default_rng(seed)
    rows, cols = shape

    if method == "slope":
        x = np.linspace(0, 1, cols)
        y = np.linspace(0, 1, rows)
        xx, yy = np.meshgrid(x, y)
        dem = 30 + 50 * (1 - yy)
        dem += rng.normal(0, 1.5, size=shape)
        return np.clip(dem, 30, 80)

    if method == "valley":
        cx, cy = cols / 2, rows / 2
        yy, xx = np.ogrid[:rows, :cols]
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        max_dist = np.sqrt(cx ** 2 + cy ** 2)
        valley = 1 - dist / max_dist
        dem = 30 + 50 * valley ** 2
        dem += rng.normal(0, 2.0, size=shape)
        return np.clip(dem, 30, 80)

    x = np.linspace(0, 1, cols)
    y = np.linspace(0, 1, rows)
    xx, yy = np.meshgrid(x, y)
    dem = 30 + 50 * (1 - yy)
    dem += 5 * np.sin(2 * np.pi * xx * 2) * np.cos(2 * np.pi * yy * 1.5)
    dem += rng.normal(0, 1.0, size=shape)
    return np.clip(dem, 30, 80)


def load_real_dem(filepath: str) -> np.ndarray:
    """Load DEM from file.

    Supports .npy, .tif (GeoTIFF), and .asc (ASCII Grid) formats.

    Parameters
    ----------
    filepath : str
        Path to DEM file.

    Returns
    -------
    np.ndarray
        2D elevation array.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"DEM file not found: {filepath}")

    suffix = path.suffix.lower()
    if suffix == ".npy":
        dem = np.load(str(path))
    elif suffix == ".tif":
        try:
            import rasterio
        except ImportError:
            raise ImportError("rasterio required for .tif files. Install with: pip install rasterio")
        with rasterio.open(str(path)) as src:
            dem = src.read(1).astype(np.float64)
            dem[dem <= src.nodata] = np.nan if src.nodata is not None else dem
    elif suffix == ".asc":
        dem = _load_ascii_grid(str(path))
    else:
        raise ValueError(f"Unsupported DEM format: {suffix}. Use .npy, .tif, or .asc")

    dem = np.nan_to_num(dem, nan=np.nanmean(dem))
    return dem


def _load_ascii_grid(filepath: str) -> np.ndarray:
    """Load ASCII Grid (.asc) DEM file."""
    with open(filepath, "r") as f:
        header = {}
        for _ in range(6):
            line = f.readline().strip()
            parts = line.split()
            header[parts[0].lower()] = float(parts[1])
        data = np.loadtxt(f)
    ncols = int(header["ncols"])
    nrows = int(header["nrows"])
    data = data.reshape((nrows, ncols))
    nodata = header.get("nodata_value", -9999)
    data[data == nodata] = np.nan
    return data


def dem_metadata(dem: np.ndarray) -> Dict[str, Any]:
    """Compute DEM metadata.

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array.

    Returns
    -------
    dict
        Metadata with min_elevation, max_elevation, mean_elevation,
        std_elevation, shape, cell_size (assumed 30m default).
    """
    valid = dem[~np.isnan(dem)]
    return {
        "min_elevation": float(valid.min()),
        "max_elevation": float(valid.max()),
        "mean_elevation": float(valid.mean()),
        "std_elevation": float(valid.std()),
        "shape": dem.shape,
        "cell_size": 30.0,
    }


def calculate_flood(
    dem: np.ndarray,
    water_level: float
) -> Dict[str, Any]:
    """Calculate flood inundation for a given water level.

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array (meters).
    water_level : float
        Water surface elevation (meters).

    Returns
    -------
    dict with keys:
        flooded_mask : bool ndarray
        depth_array : ndarray
        flooded_percentage : float
        maximum_depth : float
        average_depth : float
    """
    flooded_mask = dem < water_level
    depth_array = np.maximum(water_level - dem, 0.0)
    flooded_cells = np.sum(flooded_mask)
    total_cells = dem.size
    flooded_percentage = (flooded_cells / total_cells) * 100.0
    flooded_depths = depth_array[flooded_mask]
    maximum_depth = float(flooded_depths.max()) if flooded_cells > 0 else 0.0
    average_depth = float(flooded_depths.mean()) if flooded_cells > 0 else 0.0

    logger.info(
        "Water level %.1fm: %.2f%% flooded, max depth %.2fm, avg depth %.2fm",
        water_level, flooded_percentage, maximum_depth, average_depth
    )
    return {
        "flooded_mask": flooded_mask,
        "depth_array": depth_array,
        "flooded_percentage": flooded_percentage,
        "maximum_depth": maximum_depth,
        "average_depth": average_depth,
    }


def simulate_rising_water(
    dem: np.ndarray,
    levels: Optional[list] = None
) -> Dict[str, Any]:
    """Simulate flooding at multiple water levels.

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array.
    levels : list, optional
        Water levels to simulate. Defaults to range(40, 51).

    Returns
    -------
    dict with keys:
        levels : list
        percentages : list
        volumes : list
        max_depths : list
        avg_depths : list
        monotonically_increasing : bool
    """
    if levels is None:
        levels = list(range(40, 51))

    from volume_analysis import calculate_flood_volume

    percentages = []
    volumes = []
    max_depths = []
    avg_depths = []

    for wl in levels:
        result = calculate_flood(dem, wl)
        percentages.append(result["flooded_percentage"])
        max_depths.append(result["maximum_depth"])
        avg_depths.append(result["average_depth"])
        vol = calculate_flood_volume(dem, result["depth_array"])
        volumes.append(vol["total_volume_m3"])

    monotonically_increasing = all(
        percentages[i] <= percentages[i + 1] for i in range(len(percentages) - 1)
    )

    return {
        "levels": levels,
        "percentages": percentages,
        "volumes": volumes,
        "max_depths": max_depths,
        "avg_depths": avg_depths,
        "monotonically_increasing": monotonically_increasing,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    dem = load_dem()
    meta = dem_metadata(dem)
    logger.info("DEM shape: %s, elevation range: %.1f - %.1f m",
                meta["shape"], meta["min_elevation"], meta["max_elevation"])

    for wl in [40, 45, 50]:
        result = calculate_flood(dem, wl)
        logger.info("WL=%.1f: %.2f%% flooded", wl, result["flooded_percentage"])

    simulation = simulate_rising_water(dem)
    logger.info("Monotonically increasing: %s", simulation["monotonically_increasing"])
