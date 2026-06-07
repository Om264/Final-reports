import numpy as np
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


def simulate_flood_routing(
    dem: np.ndarray,
    water_level: float,
    connectivity: str = "8",
    source: Tuple[int, int] = (0, 0)
) -> Dict[str, Any]:
    """Simulate flood routing with spatial spreading.

    Water spreads from the source cell to connected neighbours
    where elevation is below the water level.

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array.
    water_level : float
        Water surface elevation.
    connectivity : str
        '4' for 4-neighbour or '8' for 8-neighbour connectivity.
    source : tuple
        (row, col) starting cell for flood spread.

    Returns
    -------
    dict with keys:
        flood_extent : bool ndarray
        depth_map : ndarray
        arrival_time : ndarray (number of steps to reach each cell, -1 if unreachable)
    """
    rows, cols = dem.shape
    if connectivity == "4":
        neighbours = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    else:
        neighbours = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1),
        ]

    if not (0 <= source[0] < rows and 0 <= source[1] < cols):
        raise ValueError(f"Source {source} is outside DEM bounds ({rows}, {cols})")

    flood_extent = np.zeros((rows, cols), dtype=bool)
    arrival_time = np.full((rows, cols), -1, dtype=int)
    depth_map = np.zeros((rows, cols), dtype=np.float64)

    if dem[source] >= water_level:
        logger.warning("Source cell elevation %.2f m is above water level %.2f m. No flooding.",
                       dem[source], water_level)
        return {
            "flood_extent": flood_extent,
            "depth_map": depth_map,
            "arrival_time": arrival_time,
        }

    stack = [source]
    flood_extent[source] = True
    arrival_time[source] = 0
    depth_map[source] = water_level - dem[source]
    current_time = 0

    while stack:
        next_stack = []
        current_time += 1
        for r, c in stack:
            for dr, dc in neighbours:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and not flood_extent[nr, nc]:
                    if dem[nr, nc] < water_level:
                        flood_extent[nr, nc] = True
                        arrival_time[nr, nc] = current_time
                        depth_map[nr, nc] = water_level - dem[nr, nc]
                        next_stack.append((nr, nc))
        stack = next_stack

    logger.info(
        "Flood routing (%s-connectivity): %d cells flooded, %d steps",
        connectivity, int(np.sum(flood_extent)), int(arrival_time.max())
    )
    return {
        "flood_extent": flood_extent,
        "depth_map": depth_map,
        "arrival_time": arrival_time,
    }


def flood_spread_continuous(flood_extent: np.ndarray, connectivity: str = "8") -> bool:
    """Check that all flooded cells form a single connected component.

    Parameters
    ----------
    flood_extent : np.ndarray
        Boolean flood mask.
    connectivity : str
        '4' or '8' neighbour connectivity.

    Returns
    -------
    bool
        True if flood extent is a single connected component.
    """
    flooded_indices = np.argwhere(flood_extent)
    if len(flooded_indices) == 0:
        return True

    if connectivity == "4":
        neighbours = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    else:
        neighbours = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1),
        ]

    rows, cols = flood_extent.shape
    visited = np.zeros_like(flood_extent, dtype=bool)
    start = tuple(flooded_indices[0])

    stack = [start]
    visited[start] = True
    count = 0

    while stack:
        r, c = stack.pop()
        count += 1
        for dr, dc in neighbours:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if flood_extent[nr, nc] and not visited[nr, nc]:
                    visited[nr, nc] = True
                    stack.append((nr, nc))

    return count == len(flooded_indices)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    from flood_inundation import load_dem
    dem = load_dem()

    for conn in ["4", "8"]:
        result = simulate_flood_routing(dem, 45, connectivity=conn)
    continuous_4 = flood_spread_continuous(result["flood_extent"], "4")
    continuous_8 = flood_spread_continuous(result["flood_extent"], "8")
    logger.info("4-connected continuous: %s, 8-connected continuous: %s",
                continuous_4, continuous_8)
