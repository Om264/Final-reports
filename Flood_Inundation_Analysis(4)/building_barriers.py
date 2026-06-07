import numpy as np
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


def create_building_mask(
    dem_shape: Tuple[int, int],
    num_buildings: int = 8,
    seed: int = 42
) -> np.ndarray:
    """Create a synthetic building footprint mask.

    Generates rectangular buildings at random locations within the DEM grid.
    Buildings are treated as impermeable barriers.

    Parameters
    ----------
    dem_shape : tuple
        (rows, cols) of the DEM grid.
    num_buildings : int
        Number of buildings to place.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    np.ndarray
        Boolean mask where True indicates building footprint.
    """
    rows, cols = dem_shape
    building_mask = np.zeros(dem_shape, dtype=bool)
    rng = np.random.default_rng(seed)

    for _ in range(num_buildings):
        b_size_h = int(rng.integers(3, 8))
        b_size_w = int(rng.integers(3, 8))
        max_r = rows - b_size_h
        max_c = cols - b_size_w
        if max_r < 1 or max_c < 1:
            continue
        r0 = rng.integers(0, max_r)
        c0 = rng.integers(0, max_c)
        building_mask[r0:r0 + b_size_h, c0:c0 + b_size_w] = True

    total_building_cells = int(np.sum(building_mask))
    logger.info("Building mask: %d cells (%.2f%% of grid)",
                total_building_cells, 100.0 * total_building_cells / (rows * cols))
    return building_mask


def calculate_flood_with_buildings(
    dem: np.ndarray,
    water_level: float,
    building_mask: np.ndarray
) -> Dict[str, Any]:
    """Calculate flood extent accounting for building barriers.

    Buildings are impermeable: cells with building footprints are
    treated as barriers (elevation reset to water_level + 1 to prevent flooding).

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array.
    water_level : float
        Water surface elevation.
    building_mask : np.ndarray
        Boolean mask of building footprints.

    Returns
    -------
    dict with keys:
        flooded_mask_with_buildings : ndarray
        flooded_mask_without_buildings : ndarray
        depth_array_with_buildings : ndarray
        flooded_cells_with_buildings : int
        flooded_cells_without_buildings : int
        reduction_percentage : float
    """
    flooded_without = dem < water_level

    dem_with_barriers = dem.copy()
    dem_with_barriers[building_mask] = water_level + 1.0
    flooded_with = dem_with_barriers < water_level

    cells_without = int(np.sum(flooded_without))
    cells_with = int(np.sum(flooded_with))
    reduction = 0.0
    if cells_without > 0:
        reduction = (1.0 - cells_with / cells_without) * 100.0

    depth_with = np.maximum(water_level - dem_with_barriers, 0.0)

    logger.info(
        "Buildings: without=%d cells, with=%d cells, reduction=%.2f%%",
        cells_without, cells_with, reduction
    )
    return {
        "flooded_mask_with_buildings": flooded_with,
        "flooded_mask_without_buildings": flooded_without,
        "depth_array_with_buildings": depth_with,
        "flooded_cells_with_buildings": cells_with,
        "flooded_cells_without_buildings": cells_without,
        "reduction_percentage": reduction,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    from flood_inundation import load_dem
    dem = load_dem()
    bmask = create_building_mask(dem.shape)
    result = calculate_flood_with_buildings(dem, 45, bmask)
    logger.info("Flood reduction from buildings: %.2f%%", result["reduction_percentage"])
