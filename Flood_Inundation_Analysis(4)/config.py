"""Configuration constants for the Flood Inundation Analysis system."""

from pathlib import Path
from typing import Dict, Any

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "outputs"
TEST_DIR = PROJECT_DIR / "tests"

DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

DEM_SHAPE = (100, 100)
DEM_METHOD = "terrain"
CELL_SIZE = 30.0

WATER_LEVELS = list(range(40, 51))

SYNTHETIC_DEM_KWARGS: Dict[str, Any] = {
    "shape": DEM_SHAPE,
    "method": DEM_METHOD,
    "seed": 42,
}

BUILDING_KWARGS: Dict[str, Any] = {
    "num_buildings": 8,
    "seed": 42,
}

FLOOD_ROUTING_KWARGS: Dict[str, Any] = {
    "connectivity": "8",
    "source": None,  # Will use minimum elevation cell
}

ANIMATION_KWARGS: Dict[str, Any] = {
    "min_level": 40.0,
    "max_level": 50.0,
    "step": 1.0,
    "interval": 500,
}

LOGGING_CONFIG: Dict[str, Any] = {
    "level": "INFO",
    "format": "%(levelname)s: %(message)s",
}
