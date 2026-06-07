"""
Example Applications Module for SCS-CN Runoff Model

Demonstrates the SCS-CN method for different land use/land cover types
including woods, pasture, urban areas, and impervious surfaces.
"""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from scscn_runoff import calculate_runoff, calculate_runoff_series, _format_result

logger = logging.getLogger(__name__)


def example_woods_good_condition() -> dict[str, Any]:
    """Example: Woods in good condition (CN = 65).

    Simulates a 50mm rainfall event on forested land with good
    hydrologic condition.
    """
    P = 50.0
    CN = 65.0
    result = calculate_runoff(P, CN)
    logger.info("Woods (Good Condition) - CN=65")
    logger.info(_format_result(result))
    return result


def example_pasture_fair_condition() -> dict[str, Any]:
    """Example: Pasture in fair condition (CN = 80).

    Simulates a 50mm rainfall event on pasture/grazing land with
    fair hydrologic condition.
    """
    P = 50.0
    CN = 80.0
    result = calculate_runoff(P, CN)
    logger.info("Pasture (Fair Condition) - CN=80")
    logger.info(_format_result(result))
    return result


def example_urban_residential() -> dict[str, Any]:
    """Example: Urban residential area (CN = 92).

    Simulates a 50mm rainfall event on an urban residential area
    with reduced infiltration capacity.
    """
    P = 50.0
    CN = 92.0
    result = calculate_runoff(P, CN)
    logger.info("Urban Residential Area - CN=92")
    logger.info(_format_result(result))
    return result


def example_impervious_surface() -> dict[str, Any]:
    """Example: Impervious / paved surface (CN = 100).

    Simulates a 50mm rainfall event on a completely impervious
    surface where all rainfall becomes runoff.
    """
    P = 50.0
    CN = 100.0
    result = calculate_runoff(P, CN)
    logger.info("Impervious Surface - CN=100")
    logger.info(_format_result(result))
    return result


def run_all_examples() -> pd.DataFrame:
    """Run all land use examples and return a comparison DataFrame.

    Returns
    -------
    pd.DataFrame
        Comparison table of all land use scenarios.
    """
    examples = [
        ("Woods (Good)", 65),
        ("Pasture (Fair)", 80),
        ("Urban Residential", 92),
        ("Impervious Surface", 100),
    ]

    results = []
    P = 50.0

    for name, CN in examples:
        result = calculate_runoff(P, CN)
        results.append(
            {
                "Land Use": name,
                "CN": CN,
                "Rainfall (mm)": P,
                "S (mm)": result["retention"],
                "Ia (mm)": result["initial_abstraction"],
                "Runoff Q (mm)": result["runoff"],
                "Runoff Ratio": f"{result['runoff'] / P * 100:.1f}%",
            }
        )

    df = pd.DataFrame(results)
    print("\n" + "=" * 85)
    print("SCS-CN Runoff Examples: Land Use Comparison (P = 50 mm)")
    print("=" * 85)
    print(df.to_string(index=False))
    print("=" * 85 + "\n")

    return df


if __name__ == "__main__":
    example_woods_good_condition()
    print()
    example_pasture_fair_condition()
    print()
    example_urban_residential()
    print()
    example_impervious_surface()
    print()
    run_all_examples()
