import numpy as np
from typing import Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def validate_flood_model(
    dem: np.ndarray,
    water_levels: List[float],
    building_result: Dict[str, Any],
    routing_results: Dict[str, Any]
) -> Dict[str, Any]:
    """Run full physical validation suite for the flood model.

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array.
    water_levels : list
        Water levels used in simulation.
    building_result : dict
        Output from calculate_flood_with_buildings.
    routing_results : dict
        Output from simulate_flood_routing (any connectivity).

    Returns
    -------
    dict with validation results and overall status.
    """
    from flood_inundation import calculate_flood
    from volume_analysis import calculate_flood_volume
    from flood_routing import flood_spread_continuous

    checks = {}

    percentages = []
    volumes = []
    max_depths = []

    for wl in water_levels:
        result = calculate_flood(dem, wl)
        vol = calculate_flood_volume(dem, result["depth_array"])
        percentages.append(result["flooded_percentage"])
        volumes.append(vol["total_volume_m3"])
        max_depths.append(result["maximum_depth"])

    checks["area_monotonic"] = all(
        percentages[i] <= percentages[i + 1] for i in range(len(percentages) - 1)
    )
    logger.info("Area monotonic: %s", checks["area_monotonic"])

    checks["volume_monotonic"] = all(
        volumes[i] <= volumes[i + 1] for i in range(len(volumes) - 1)
    )
    logger.info("Volume monotonic: %s", checks["volume_monotonic"])

    valid_depths = all(d >= 0.0 for d in max_depths)
    checks["depth_nonnegative"] = valid_depths
    logger.info("Max depths non-negative: %s", valid_depths)

    valid_percentages = all(0.0 <= p <= 100.0 for p in percentages)
    checks["percentage_range"] = valid_percentages
    logger.info("Flood percentages in [0, 100]: %s", valid_percentages)

    checks["volume_nonnegative"] = all(v >= 0.0 for v in volumes)
    logger.info("Volumes non-negative: %s", checks["volume_nonnegative"])

    if routing_results["flood_extent"] is not None:
        continuous = flood_spread_continuous(routing_results["flood_extent"])
        checks["routing_continuous"] = continuous
        logger.info("Routing continuous: %s", continuous)
    else:
        checks["routing_continuous"] = True

    if building_result:
        checks["buildings_reduce_flood"] = (
            building_result["flooded_cells_without_buildings"]
            >= building_result["flooded_cells_with_buildings"]
        )
        logger.info("Buildings reduce flood: %s", checks["buildings_reduce_flood"])
    else:
        checks["buildings_reduce_flood"] = True

    all_pass = all(checks.values())
    overall = "PASS" if all_pass else "FAIL"
    checks["overall_status"] = overall

    report_path = OUTPUT_DIR / "validation_report.txt"
    with open(str(report_path), "w") as f:
        f.write("FLOOD MODEL VALIDATION REPORT\n")
        f.write("=" * 50 + "\n\n")
        for key, value in checks.items():
            f.write(f"{key:30s}: {'PASS' if value else 'FAIL'}\n")
        f.write(f"\nOVERALL: {overall}\n")
    logger.info("Validation report saved: %s", report_path)

    checks["overall_status"] = overall
    return checks


def _check_max_depth_against_min_elevation(
    dem: np.ndarray,
    water_level: float,
    result: Dict[str, Any]
) -> bool:
    """Check that maximum depth equals (water_level - min_elevation)."""
    min_elev = float(dem.min())
    expected_max = water_level - min_elev
    actual_max = result["maximum_depth"]
    return abs(actual_max - expected_max) < 1e-6


def _check_edge_cases(dem: np.ndarray) -> Dict[str, bool]:
    """Validate edge cases: below min, above max, at boundaries."""
    from flood_inundation import calculate_flood

    min_elev = float(dem.min())
    max_elev = float(dem.max())

    below_min = calculate_flood(dem, min_elev - 10)
    above_max = calculate_flood(dem, max_elev + 10)

    return {
        "below_min_elevation_zero_flood": below_min["flooded_percentage"] == 0.0,
        "above_max_elevation_full_flood": above_max["flooded_percentage"] == 100.0,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    from flood_inundation import load_dem
    from building_barriers import create_building_mask, calculate_flood_with_buildings
    from flood_routing import simulate_flood_routing

    dem = load_dem()
    bm = create_building_mask(dem.shape)
    bres = calculate_flood_with_buildings(dem, 45, bm)
    rres = simulate_flood_routing(dem, 45, connectivity="8")

    result = validate_flood_model(dem, list(range(40, 51)), bres, rres)
    print(f"Validation overall: {result['overall_status']}")
