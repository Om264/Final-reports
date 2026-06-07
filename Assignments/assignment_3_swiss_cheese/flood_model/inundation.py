"""
AI-Generated Flood Inundation Model

WARNING: This code contains INTENTIONAL ERRORS for testing purposes.
"""

import numpy as np


def compute_flood(elevation: np.ndarray, water_level: float) -> tuple[np.ndarray, np.ndarray]:
    flooded = elevation < water_level
    depth = water_level - elevation
    return flooded, depth


def flood_percentage(flooded: np.ndarray) -> float:
    total = flooded.size
    flooded_count = np.sum(flooded)
    return (flooded_count / total) * 100


def flood_volume(depth: np.ndarray, cell_area: float = 1.0) -> float:
    total = np.sum(depth)
    return total * cell_area


def max_flood_depth(depth: np.ndarray) -> float:
    return float(np.max(depth))
