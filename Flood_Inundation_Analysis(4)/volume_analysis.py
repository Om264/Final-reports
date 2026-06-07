import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def calculate_flood_volume(
    dem: np.ndarray,
    depth_array: np.ndarray,
    cell_size: float = 30.0
) -> Dict[str, Any]:
    """Calculate flood volume from depth array.

    Volume = sum(depth * cell_area) for all flooded cells.

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array (used for shape only).
    depth_array : np.ndarray
        Inundation depth per cell (same shape as dem).
    cell_size : float
        Cell resolution in meters (default 30m).

    Returns
    -------
    dict with keys:
        total_volume_m3 : float
        average_depth : float
        maximum_depth : float
        flooded_cells : int
        cell_area_m2 : float
    """
    cell_area = cell_size ** 2
    flooded_mask = depth_array > 0
    flooded_cells = int(np.sum(flooded_mask))
    total_volume = float(np.sum(depth_array) * cell_area)
    flooded_depths = depth_array[flooded_mask]
    avg_depth = float(flooded_depths.mean()) if flooded_cells > 0 else 0.0
    max_depth = float(flooded_depths.max()) if flooded_cells > 0 else 0.0

    logger.info(
        "Flood volume: %.2f m^3 over %d cells, avg depth %.2f m",
        total_volume, flooded_cells, avg_depth
    )
    return {
        "total_volume_m3": total_volume,
        "average_depth": avg_depth,
        "maximum_depth": max_depth,
        "flooded_cells": flooded_cells,
        "cell_area_m2": cell_area,
    }


def flood_volume_curve(
    dem: np.ndarray,
    levels: Optional[list] = None
) -> Dict[str, Any]:
    """Compute flood volume at multiple water levels.

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array.
    levels : list, optional
        Water levels. Defaults to range(40, 51).

    Returns
    -------
    dict with keys:
        levels : list
        volumes : list
        depths : list
    """
    if levels is None:
        levels = list(range(40, 51))
    volumes = []
    depths = []
    for wl in levels:
        from flood_inundation import calculate_flood
        result = calculate_flood(dem, wl)
        vol = calculate_flood_volume(dem, result["depth_array"])
        volumes.append(vol["total_volume_m3"])
        depths.append(vol["average_depth"])
    return {"levels": levels, "volumes": volumes, "depths": depths}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    from flood_inundation import load_dem, calculate_flood
    dem = load_dem()
    result = calculate_flood(dem, 45)
    vol = calculate_flood_volume(dem, result["depth_array"])
    logger.info("Volume at 45m: %.2f m^3", vol["total_volume_m3"])
