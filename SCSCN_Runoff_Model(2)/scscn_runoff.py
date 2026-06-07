"""
SCS-CN Runoff Calculation Module

Implements the Soil Conservation Service Curve Number (SCS-CN) method
for estimating direct runoff from rainfall. This is the most widely used
approach in hydrological modeling for runoff estimation.

Formulas:
    S = (25400 / CN) - 254
    Ia = 0.2 * S
    Q = (P - Ia)^2 / (P - Ia + S)   if P > Ia
    Q = 0                            if P <= Ia

References:
    - USDA NRCS (formerly SCS) Technical Release 55 (TR-55)
    - Chow, V.T., Maidment, D.R., & Mays, L.W. (1988). Applied Hydrology.
"""

from __future__ import annotations

import logging
from typing import Union

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def calculate_runoff(P: float, CN: float) -> dict[str, float]:
    """Calculate runoff depth using the SCS-CN method for a single event.

    Parameters
    ----------
    P : float
        Rainfall depth in millimeters. Must be non-negative.
    CN : float
        Curve Number in range (0, 100]. CN = 0 is treated as no runoff.
        CN must be > 0 for meaningful calculations.

    Returns
    -------
    dict[str, float]
        Dictionary containing:
        - rainfall: input rainfall depth (mm)
        - curve_number: input curve number
        - retention: potential maximum retention S (mm)
        - initial_abstraction: initial abstraction Ia (mm)
        - runoff: computed runoff depth Q (mm)

    Raises
    ------
    ValueError
        If P is negative or CN is outside valid range.

    Examples
    --------
    >>> result = calculate_runoff(50.0, 80.0)
    >>> round(result["runoff"], 1)
    13.8
    >>> result["retention"]
    63.5
    """
    if P < 0:
        raise ValueError(f"Rainfall P must be non-negative, got {P}")
    if CN < 0 or CN > 100:
        raise ValueError(f"Curve Number CN must be in [0, 100], got {CN}")

    P = float(P)
    CN = float(CN)

    if CN == 0 or P == 0:
        S = float("inf") if CN == 0 else (25400 / CN) - 254
        Ia = 0.2 * S if CN != 0 else float("inf")
        return {
            "rainfall": P,
            "curve_number": CN,
            "retention": S,
            "initial_abstraction": Ia if CN != 0 else float("inf"),
            "runoff": 0.0,
        }

    S = (25400.0 / CN) - 254.0
    Ia = 0.2 * S

    if P <= Ia:
        Q = 0.0
    else:
        Q = (P - Ia) ** 2 / (P - Ia + S)

    Q = min(Q, P)

    return {
        "rainfall": P,
        "curve_number": CN,
        "retention": round(S, 4),
        "initial_abstraction": round(Ia, 4),
        "runoff": round(Q, 4),
    }


def calculate_runoff_series(
    rainfall_values: Union[list[float], np.ndarray],
    curve_numbers: Union[list[float], np.ndarray],
) -> pd.DataFrame:
    """Calculate runoff for multiple rainfall events and curve numbers.

    Computes all combinations of the provided rainfall depths and curve
    numbers, returning results in a structured DataFrame.

    Parameters
    ----------
    rainfall_values : list[float] or np.ndarray
        Array of rainfall depths in millimeters.
    curve_numbers : list[float] or np.ndarray
        Array of curve numbers in [0, 100].

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        Rainfall, Curve_Number, Retention, Initial_Abstraction, Runoff

    Examples
    --------
    >>> df = calculate_runoff_series([10, 50], [60, 80])
    >>> len(df)
    4
    >>> list(df.columns)
    ['Rainfall', 'Curve_Number', 'Retention', 'Initial_Abstraction', 'Runoff']
    """
    rainfall_arr = np.asarray(rainfall_values, dtype=np.float64)
    cn_arr = np.asarray(curve_numbers, dtype=np.float64)

    if np.any(rainfall_arr < 0):
        raise ValueError("All rainfall values must be non-negative")
    if np.any(cn_arr < 0) or np.any(cn_arr > 100):
        raise ValueError("All curve numbers must be in [0, 100]")

    P_grid, CN_grid = np.meshgrid(rainfall_arr, cn_arr)
    P_flat = P_grid.ravel()
    CN_flat = CN_grid.ravel()

    S_arr = np.where(CN_flat == 0, float("inf"), (25400.0 / CN_flat) - 254.0)
    Ia_arr = np.where(CN_flat == 0, float("inf"), 0.2 * S_arr)

    numerator = (P_flat - Ia_arr) ** 2
    denominator = P_flat - Ia_arr + S_arr

    mask_nan = np.isinf(denominator) | (denominator == 0) | np.isnan(denominator)
    Q_arr = np.where(
        (P_flat <= Ia_arr) | mask_nan | (P_flat == 0) | (CN_flat == 0),
        0.0,
        numerator / denominator,
    )
    Q_arr = np.minimum(Q_arr, P_flat)

    df = pd.DataFrame(
        {
            "Rainfall": P_flat,
            "Curve_Number": CN_flat,
            "Retention": np.where(np.isinf(S_arr), float("inf"), np.round(S_arr, 4)),
            "Initial_Abstraction": np.where(
                np.isinf(Ia_arr), float("inf"), np.round(Ia_arr, 4)
            ),
            "Runoff": np.round(Q_arr, 4),
        }
    )
    df = df.sort_values(["Curve_Number", "Rainfall"]).reset_index(drop=True)
    return df


def compute_retention(CN: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Compute potential maximum retention S from curve number.

    Parameters
    ----------
    CN : float or np.ndarray
        Curve number(s) in range (0, 100].

    Returns
    -------
    float or np.ndarray
        Potential maximum retention in millimeters.
    """
    CN_arr = np.asarray(CN, dtype=np.float64)
    if np.any(CN_arr <= 0) or np.any(CN_arr > 100):
        raise ValueError("CN must be in (0, 100]")
    return (25400.0 / CN_arr) - 254.0


def compute_initial_abstraction(CN: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Compute initial abstraction Ia = 0.2 * S.

    Parameters
    ----------
    CN : float or np.ndarray
        Curve number(s) in range (0, 100].

    Returns
    -------
    float or np.ndarray
        Initial abstraction in millimeters.
    """
    return 0.2 * compute_retention(CN)


def runoff_analytics(df: pd.DataFrame) -> dict[str, float]:
    """Compute summary statistics from a runoff DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with at least 'Runoff', 'Curve_Number', and 'Rainfall' columns.

    Returns
    -------
    dict[str, float]
        Dictionary of summary statistics.
    """
    runoff = df["Runoff"]
    cn = df["Curve_Number"]
    rainfall = df["Rainfall"]

    stats = {
        "average_runoff": float(np.mean(runoff)),
        "max_runoff": float(np.max(runoff)),
        "min_runoff": float(np.min(runoff)),
        "std_runoff": float(np.std(runoff)),
        "rainfall_runoff_correlation": float(np.corrcoef(rainfall, runoff)[0, 1]),
        "cn_runoff_correlation": float(np.corrcoef(cn, runoff)[0, 1]),
        "total_rainfall": float(np.sum(rainfall)),
        "total_runoff": float(np.sum(runoff)),
        "runoff_ratio": float(np.sum(runoff) / np.sum(rainfall)) if np.sum(rainfall) > 0 else 0.0,
    }

    logger.info("Runoff analytics computed successfully")
    return stats


def _format_result(result: dict[str, float]) -> str:
    """Format a single runoff result for display.

    Parameters
    ----------
    result : dict[str, float]
        Result dictionary from calculate_runoff.

    Returns
    -------
    str
        Formatted string representation.
    """
    return (
        f"Rainfall P = {result['rainfall']:.1f} mm\n"
        f"Curve Number CN = {result['curve_number']:.0f}\n"
        f"Retention S = {result['retention']:.2f} mm\n"
        f"Initial Abstraction Ia = {result['initial_abstraction']:.2f} mm\n"
        f"Runoff Q = {result['runoff']:.2f} mm\n"
        f"Q <= P: {result['runoff'] <= result['rainfall']}"
    )
