#!/usr/bin/env python3
"""Flood Inundation Analysis — Main Pipeline.

Generates all deliverables specified in Experiment 4.
"""

import numpy as np
import pandas as pd
import logging
import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    OUTPUT_DIR, DATA_DIR, WATER_LEVELS, CELL_SIZE,
    BUILDING_KWARGS, FLOOD_ROUTING_KWARGS, ANIMATION_KWARGS,
    LOGGING_CONFIG
)
from flood_inundation import load_dem, calculate_flood, dem_metadata
from visualization import (
    visualize_flood, visualize_comparison, visualize_flood_curve,
    visualize_volume_curve, visualize_building_impact, visualize_routing
)
from building_barriers import create_building_mask, calculate_flood_with_buildings
from flood_routing import simulate_flood_routing
from volume_analysis import flood_volume_curve
from animation_generator import create_flood_animation
from validation import validate_flood_model

logging.basicConfig(**LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("FLOOD INUNDATION ANALYSIS - MAIN PIPELINE")
    logger.info("=" * 60)

    # Step 1: Load/generate DEM
    logger.info("\n[1] Loading DEM data...")
    dem = load_dem()
    meta = dem_metadata(dem)
    logger.info("  DEM shape: %s, range: %.1f-%.1f m, mean: %.1f m",
                meta["shape"], meta["min_elevation"],
                meta["max_elevation"], meta["mean_elevation"])

    # Save DEM data
    np.save(str(DATA_DIR / "dem_data.npy"), dem)
    logger.info("  Saved DEM to %s", DATA_DIR / "dem_data.npy")

    # Step 2: Flood calculation at key levels
    logger.info("\n[2] Calculating flood inundation...")
    for wl in [40, 45, 50]:
        result = calculate_flood(dem, float(wl))
        logger.info("  WL=%.0fm: %.2f%% flooded, max depth=%.2fm",
                    wl, result["flooded_percentage"], result["maximum_depth"])

    # Step 3: Visualizations
    logger.info("\n[3] Generating flood extent maps...")
    for wl in [40, 50]:
        result = calculate_flood(dem, float(wl))
        path = str(OUTPUT_DIR / f"flood_extent_{wl}m.png")
        visualize_flood(dem, result["flooded_mask"], result["depth_array"],
                        float(wl), save_path=path)

    logger.info("\n[3b] Generating comparison visualization...")
    visualize_comparison(dem, [40, 45, 50],
                         save_path=str(OUTPUT_DIR / "flood_comparison.png"))

    # Step 4: Dynamic simulation
    logger.info("\n[4] Running dynamic simulation...")
    from flood_inundation import simulate_rising_water
    sim = simulate_rising_water(dem, WATER_LEVELS)

    # Save flood curve
    visualize_flood_curve(sim["levels"], sim["percentages"],
                          save_path=str(OUTPUT_DIR / "flood_curve.png"))

    # Step 5: Volume analysis
    logger.info("\n[5] Running volume analysis...")
    vc = flood_volume_curve(dem, WATER_LEVELS)
    visualize_volume_curve(vc["levels"], vc["volumes"],
                           save_path=str(OUTPUT_DIR / "flood_volume_analysis.png"))

    # Step 6: Building barriers
    logger.info("\n[6] Building impact analysis...")
    building_mask = create_building_mask(dem.shape, **BUILDING_KWARGS)
    bres = calculate_flood_with_buildings(dem, 45, building_mask)
    visualize_building_impact(dem, building_mask, bres, 45,
                              save_path=str(OUTPUT_DIR / "building_impact.png"))

    # Step 7: Flood routing
    logger.info("\n[7] Flood routing analysis...")
    source_routing = FLOOD_ROUTING_KWARGS["source"]
    if source_routing is None:
        min_idx = np.unravel_index(np.argmin(dem), dem.shape)
        source_routing = min_idx
    rres = simulate_flood_routing(dem, 45, connectivity=FLOOD_ROUTING_KWARGS["connectivity"],
                                  source=source_routing)
    visualize_routing(dem, rres, 45, FLOOD_ROUTING_KWARGS["connectivity"],
                      save_path=str(OUTPUT_DIR / "flood_routing_map.png"))

    # Step 8: Animation
    logger.info("\n[8] Generating flood animation...")
    create_flood_animation(dem, **ANIMATION_KWARGS,
                           save_path=str(OUTPUT_DIR / "rising_flood.gif"))

    # Step 9: Export statistics
    logger.info("\n[9] Exporting flood statistics...")
    stats_df = pd.DataFrame({
        "Water_Level": sim["levels"],
        "Flooded_Percentage": sim["percentages"],
        "Flood_Volume": sim["volumes"],
        "Maximum_Depth": sim["max_depths"],
        "Average_Depth": sim["avg_depths"],
    })
    stats_path = OUTPUT_DIR / "flood_statistics.csv"
    stats_df.to_csv(str(stats_path), index=False)
    logger.info("  Saved statistics to %s", stats_path)

    # Step 10: Validation
    logger.info("\n[10] Running physical validation...")
    vres = validate_flood_model(dem, WATER_LEVELS, bres, rres)
    logger.info("  Validation status: %s", vres["overall_status"])

    logger.info("\n" + "=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)

    # Verify deliverables
    expected = [
        OUTPUT_DIR / "flood_extent_40m.png",
        OUTPUT_DIR / "flood_extent_50m.png",
        OUTPUT_DIR / "flood_curve.png",
        OUTPUT_DIR / "flood_volume_analysis.png",
        OUTPUT_DIR / "building_impact.png",
        OUTPUT_DIR / "flood_routing_map.png",
        OUTPUT_DIR / "rising_flood.gif",
        OUTPUT_DIR / "flood_statistics.csv",
        OUTPUT_DIR / "validation_report.txt",
        DATA_DIR / "dem_data.npy",
    ]
    logger.info("\nDeliverables check:")
    for p in expected:
        status = "OK" if p.exists() else "MISSING"
        logger.info("  [%s] %s", status, p.name)


if __name__ == "__main__":
    main()
