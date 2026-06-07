"""
Physical Validation Module for SCS-CN Runoff Model

Validates hydrological constraints and physical correctness of the
SCS-CN runoff calculations. Ensures that all boundary conditions
and physical laws are satisfied.

Validation Checks:
    1. Runoff is non-negative (Q >= 0)
    2. Runoff does not exceed rainfall (Q <= P)
    3. Higher CN produces more runoff (monotonicity)
    4. No runoff when P < Ia
    5. No runoff when P = 0
    6. Numerical stability for edge cases
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from scscn_runoff import calculate_runoff, calculate_runoff_series

logger = logging.getLogger(__name__)


def validate_runoff_non_negative(
    df: pd.DataFrame, verbose: bool = True
) -> dict[str, Any]:
    """Check that all runoff values are non-negative.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'Runoff' column.
    verbose : bool, optional
        If True, log detailed results.

    Returns
    -------
    dict[str, Any]
        Validation result with passed status and details.
    """
    violations = df[df["Runoff"] < -1e-10]
    passed = len(violations) == 0
    result = {
        "test": "Q >= 0 (Runoff non-negative)",
        "passed": passed,
        "violations": len(violations),
        "details": (
            "All runoff values are non-negative"
            if passed
            else f"Found {len(violations)} negative runoff values"
        ),
    }
    if verbose:
        logger.info(f"{result['test']}: {'PASS' if passed else 'FAIL'}")
    return result


def validate_runoff_not_exceed_rainfall(
    df: pd.DataFrame, verbose: bool = True
) -> dict[str, Any]:
    """Check that runoff never exceeds rainfall.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'Runoff' and 'Rainfall' columns.
    verbose : bool, optional
        If True, log detailed results.

    Returns
    -------
    dict[str, Any]
        Validation result with passed status and details.
    """
    violations = df[df["Runoff"] > df["Rainfall"] + 1e-10]
    passed = len(violations) == 0
    result = {
        "test": "Q <= P (Runoff does not exceed rainfall)",
        "passed": passed,
        "violations": len(violations),
        "details": (
            "All runoff values respect the rainfall limit"
            if passed
            else f"Found {len(violations)} violations of Q <= P"
        ),
    }
    if verbose:
        logger.info(f"{result['test']}: {'PASS' if passed else 'FAIL'}")
    return result


def validate_monotonic_behavior(
    df: pd.DataFrame, verbose: bool = True
) -> dict[str, Any]:
    """Check that for a fixed rainfall, higher CN produces more runoff.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with 'Rainfall', 'Curve_Number', 'Runoff' columns.
    verbose : bool, optional
        If True, log detailed results.

    Returns
    -------
    dict[str, Any]
        Validation result with passed status and details.
    """
    passed = True
    violations_details = []

    for rainfall_val in df["Rainfall"].unique():
        subset = df[df["Rainfall"] == rainfall_val].sort_values("Curve_Number")
        runoff_vals = subset["Runoff"].values
        cn_vals = subset["Curve_Number"].values
        for i in range(len(runoff_vals) - 1):
            if runoff_vals[i] > runoff_vals[i + 1] + 1e-10:
                passed = False
                violations_details.append(
                    f"P={rainfall_val}: CN={cn_vals[i]}->Q={runoff_vals[i]:.4f} > "
                    f"CN={cn_vals[i+1]}->Q={runoff_vals[i+1]:.4f}"
                )

    result = {
        "test": "Monotonic: Higher CN -> More runoff (fixed P)",
        "passed": passed,
        "violations": len(violations_details),
        "details": (
            "Monotonic behavior confirmed for all rainfall values"
            if passed
            else f"Non-monotonic at: {violations_details}"
        ),
    }
    if verbose:
        logger.info(f"{result['test']}: {'PASS' if passed else 'FAIL'}")
    return result


def validate_initial_abstraction_threshold(
    verbose: bool = True,
) -> dict[str, Any]:
    """Check that no runoff occurs when P <= Ia.

    Tests multiple cases where rainfall is below the initial abstraction
    threshold to confirm zero runoff.

    Parameters
    ----------
    verbose : bool, optional
        If True, log detailed results.

    Returns
    -------
    dict[str, Any]
        Validation result with passed status and details.
    """
    test_cases = [
        (0.0, 80),
        (5.0, 80),
        (10.0, 60),
        (0.0, 100),
        (0.0, 0),
    ]

    failures = []
    for P, CN in test_cases:
        result = calculate_runoff(P, CN)
        S = result["retention"]
        Ia = result["initial_abstraction"]
        Q = result["runoff"]
        if P < Ia and Q != 0:
            failures.append(f"P={P}, CN={CN}: P<Ia ({P}<{Ia}) but Q={Q}!=0")
        if P <= Ia and Q != 0:
            failures.append(f"P={P}, CN={CN}: P<=Ia but Q={Q}!=0")

    passed = len(failures) == 0
    result_dict = {
        "test": "P <= Ia => Q = 0 (Initial abstraction threshold)",
        "passed": passed,
        "violations": len(failures),
        "details": (
            "All threshold cases pass"
            if passed
            else f"Failures: {failures}"
        ),
    }
    if verbose:
        logger.info(f"{result_dict['test']}: {'PASS' if passed else 'FAIL'}")
    return result_dict


def validate_cn_100_impervious(verbose: bool = True) -> dict[str, Any]:
    """Check that CN = 100 produces maximum runoff behavior.

    For CN = 100: S = 0, Ia = 0, Q = P (all rainfall becomes runoff).

    Parameters
    ----------
    verbose : bool, optional
        If True, log detailed results.

    Returns
    -------
    dict[str, Any]
        Validation result with passed status and details.
    """
    test_rainfalls = [10.0, 25.0, 50.0, 100.0]
    failures = []

    for P in test_rainfalls:
        result = calculate_runoff(P, 100.0)
        Q = result["runoff"]
        if abs(Q - P) > 1e-10:
            failures.append(f"P={P}: expected Q={P}, got Q={Q}")
        if result["retention"] != 0:
            failures.append(f"P={P}: expected S=0, got S={result['retention']}")
        if result["initial_abstraction"] != 0:
            failures.append(
                f"P={P}: expected Ia=0, got Ia={result['initial_abstraction']}"
            )

    passed = len(failures) == 0
    result_dict = {
        "test": "CN = 100 => Impervious (S=0, Ia=0, Q=P)",
        "passed": passed,
        "violations": len(failures),
        "details": (
            "CN=100 behaves as impervious surface"
            if passed
            else f"Failures: {failures}"
        ),
    }
    if verbose:
        logger.info(f"{result_dict['test']}: {'PASS' if passed else 'FAIL'}")
    return result_dict


def validate_cn_0_infiltration(verbose: bool = True) -> dict[str, Any]:
    """Check that CN = 0 produces zero runoff (all infiltration).

    For CN = 0: all water infiltrates, Q = 0.

    Parameters
    ----------
    verbose : bool, optional
        If True, log detailed results.

    Returns
    -------
    dict[str, Any]
        Validation result with passed status and details.
    """
    test_rainfalls = [10.0, 25.0, 50.0, 100.0]
    failures = []

    for P in test_rainfalls:
        result = calculate_runoff(P, 0.0)
        Q = result["runoff"]
        if Q != 0:
            failures.append(f"P={P}, CN=0: expected Q=0, got Q={Q}")

    passed = len(failures) == 0
    result_dict = {
        "test": "CN = 0 => All infiltration (Q = 0)",
        "passed": passed,
        "violations": len(failures),
        "details": (
            "CN=0 produces zero runoff as expected"
            if passed
            else f"Failures: {failures}"
        ),
    }
    if verbose:
        logger.info(f"{result_dict['test']}: {'PASS' if passed else 'FAIL'}")
    return result_dict


def validate_numerical_stability(verbose: bool = True) -> dict[str, Any]:
    """Check numerical stability for extreme and edge-case inputs.

    Tests very large rainfall values and values near boundaries to
    ensure floating-point stability.

    Parameters
    ----------
    verbose : bool, optional
        If True, log detailed results.

    Returns
    -------
    dict[str, Any]
        Validation result with passed status and details.
    """
    test_cases = [
        (1e6, 80, "Large rainfall"),
        (0.001, 80, "Tiny rainfall"),
        (1e6, 99.999, "Large rainfall, high CN"),
        (50.0, 0.001, "CN near zero"),
        (50.0, 99.999, "CN near max"),
        (0.0, 50.0, "Zero rainfall"),
    ]

    failures = []
    for P, CN, label in test_cases:
        try:
            result = calculate_runoff(P, CN)
            Q = result["runoff"]
            if np.isnan(Q) or np.isinf(Q):
                failures.append(f"{label} (P={P}, CN={CN}): Q is {Q}")
            if Q < 0 or Q > P + 1e-10:
                failures.append(f"{label} (P={P}, CN={CN}): Q={Q} violates 0<=Q<=P")
        except Exception as e:
            failures.append(f"{label} (P={P}, CN={CN}): exception {e}")

    passed = len(failures) == 0
    result_dict = {
        "test": "Numerical stability for edge cases",
        "passed": passed,
        "violations": len(failures),
        "details": (
            "All edge cases handled with numerical stability"
            if passed
            else f"Failures: {failures}"
        ),
    }
    if verbose:
        logger.info(f"{result_dict['test']}: {'PASS' if passed else 'FAIL'}")
    return result_dict


def validate_runoff_model(
    rainfall_range: tuple[float, float, int] = (0, 200, 21),
    cn_range: tuple[float, float, int] = (1, 100, 20),
    verbose: bool = True,
) -> dict[str, Any]:
    """Run comprehensive physical validation of the SCS-CN model.

    Tests all physical constraints across a grid of rainfall and CN
    values and generates a detailed validation report.

    Parameters
    ----------
    rainfall_range : tuple[float, float, int]
        (min, max, num_points) for rainfall grid. Default (0, 200, 21).
    cn_range : tuple[float, float, int]
        (min, max, num_points) for curve number grid. Default (1, 100, 20).
    verbose : bool, optional
        If True, log detailed results.

    Returns
    -------
    dict[str, Any]
        Complete validation report with all test results.
    """
    logger.info("=" * 60)
    logger.info("SCS-CN Runoff Model: Physical Validation")
    logger.info("=" * 60)

    rainfall_values = np.linspace(*rainfall_range)
    cn_values = np.linspace(*cn_range)

    df = calculate_runoff_series(rainfall_values, cn_values)
    logger.info(f"Generated {len(df)} test cases for validation")

    test_results = {}

    test_results["non_negative"] = validate_runoff_non_negative(df, verbose)
    test_results["runoff_limit"] = validate_runoff_not_exceed_rainfall(df, verbose)
    test_results["monotonic"] = validate_monotonic_behavior(df, verbose)
    test_results["threshold"] = validate_initial_abstraction_threshold(verbose)
    test_results["cn_100"] = validate_cn_100_impervious(verbose)
    test_results["cn_0"] = validate_cn_0_infiltration(verbose)
    test_results["numerical"] = validate_numerical_stability(verbose)

    all_passed = all(t["passed"] for t in test_results.values())

    report = {
        "tests_passed": all_passed,
        "physical_constraints": test_results["non_negative"]["passed"]
        and test_results["runoff_limit"]["passed"],
        "monotonic_behavior": test_results["monotonic"]["passed"],
        "runoff_limit_verified": test_results["runoff_limit"]["passed"],
        "total_tests": len(test_results),
        "passed_tests": sum(1 for t in test_results.values() if t["passed"]),
        "failed_tests": sum(1 for t in test_results.values() if not t["passed"]),
        "test_details": test_results,
        "grid_shape": {"rainfall_points": len(rainfall_values), "cn_points": len(cn_values)},
    }

    logger.info("=" * 60)
    logger.info(f"Validation Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    logger.info(f"  Total: {report['total_tests']} | "
                f"Passed: {report['passed_tests']} | "
                f"Failed: {report['failed_tests']}")
    logger.info("=" * 60)

    return report


def generate_validation_report(
    report: dict[str, Any], output_path: str = None
) -> str:
    """Generate a human-readable validation report string.

    Parameters
    ----------
    report : dict[str, Any]
        Validation report from validate_runoff_model.
    output_path : str, optional
        If provided, write report to this file.

    Returns
    -------
    str
        Formatted validation report.
    """
    lines = []
    lines.append("=" * 60)
    lines.append("SCS-CN Runoff Model - Physical Validation Report")
    lines.append("=" * 60)
    lines.append(f"Overall Status: {'PASS' if report['tests_passed'] else 'FAIL'}")
    lines.append(f"  {report['passed_tests']}/{report['total_tests']} tests passed")
    lines.append("")
    lines.append("Grid:")
    lines.append(f"  Rainfall points: {report['grid_shape']['rainfall_points']}")
    lines.append(f"  CN points:       {report['grid_shape']['cn_points']}")
    lines.append("")

    for test_name, test_result in report["test_details"].items():
        status = "PASS" if test_result["passed"] else "FAIL"
        lines.append(f"  [{status}] {test_result['test']}")
        lines.append(f"         {test_result['details']}")

    lines.append("")
    lines.append("Key Physical Constraints:")
    constraints = [
        ("Q >= 0", report["physical_constraints"]),
        ("Q <= P", report["runoff_limit_verified"]),
        ("Monotonic (higher CN -> more runoff)", report["monotonic_behavior"]),
    ]
    for label, ok in constraints:
        status = "PASS" if ok else "FAIL"
        lines.append(f"  [{status}] {label}")

    lines.append("")
    lines.append("=" * 60)
    report_str = "\n".join(lines)

    if output_path:
        with open(output_path, "w") as f:
            f.write(report_str)
        logger.info(f"Validation report written to {output_path}")

    return report_str


if __name__ == "__main__":
    report = validate_runoff_model(verbose=True)
    print(generate_validation_report(report, "outputs/validation_report.txt"))
