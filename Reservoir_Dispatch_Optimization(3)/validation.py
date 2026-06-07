import numpy as np
from typing import Dict, Any
import logging

from reservoir_model import (
    simulate_storage,
    calculate_revenue,
    calculate_ecological_deficit,
    MIN_STORAGE,
    MAX_STORAGE,
    ECOLOGICAL_RELEASE,
    MAX_RELEASE,
    INITIAL_STORAGE,
    NUM_DAYS,
    SECONDS_PER_DAY,
    INFLOW,
    HYDROPOWER_PRICE,
    HYDROPOWER_CONVERSION,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def validate_solution(
    releases: np.ndarray,
) -> Dict[str, Any]:
    results: Dict[str, Any] = {
        "storage_constraints_passed": True,
        "release_constraints_passed": True,
        "mass_balance_passed": True,
        "revenue_verified": True,
        "overall_status": "PASS",
        "storage_violations": [],
        "release_violations": [],
        "mass_balance_errors": [],
        "details": {},
    }

    storage = simulate_storage(releases)

    for t in range(NUM_DAYS + 1):
        s = storage[t]
        if s < MIN_STORAGE - 1.0:
            results["storage_constraints_passed"] = False
            results["storage_violations"].append(
                f"Day {t}: storage={s:.2f} m\u00b3 < MIN={MIN_STORAGE:,.0f} m\u00b3"
            )
        if s > MAX_STORAGE + 1.0:
            results["storage_constraints_passed"] = False
            results["storage_violations"].append(
                f"Day {t}: storage={s:.2f} m\u00b3 > MAX={MAX_STORAGE:,.0f} m\u00b3"
            )

    for t in range(NUM_DAYS):
        q = releases[t]
        if q < ECOLOGICAL_RELEASE - 0.001:
            results["release_constraints_passed"] = False
            results["release_violations"].append(
                f"Day {t + 1}: release={q:.4f} m\u00b3/s < Q_eco={ECOLOGICAL_RELEASE} m\u00b3/s"
            )
        if q > MAX_RELEASE + 0.001:
            results["release_constraints_passed"] = False
            results["release_violations"].append(
                f"Day {t + 1}: release={q:.4f} m\u00b3/s > Q_max={MAX_RELEASE} m\u00b3/s"
            )

    storage_computed = np.zeros(NUM_DAYS + 1, dtype=float)
    storage_computed[0] = INITIAL_STORAGE
    for t in range(NUM_DAYS):
        storage_computed[t + 1] = storage_computed[t] + (INFLOW[t] - releases[t]) * SECONDS_PER_DAY

    for t in range(NUM_DAYS + 1):
        error = abs(storage_computed[t] - storage[t])
        if error > 1.0:
            results["mass_balance_passed"] = False
            results["mass_balance_errors"].append(
                f"Day {t}: mass balance error={error:.4f} m\u00b3"
            )

    revenue_expected = float(np.sum(releases * HYDROPOWER_PRICE * HYDROPOWER_CONVERSION))
    revenue_from_sim = calculate_revenue(releases)
    revenue_error = abs(revenue_expected - revenue_from_sim)
    if revenue_error > 0.01:
        results["revenue_verified"] = False
    results["details"]["revenue_calculated"] = revenue_expected
    results["details"]["revenue_from_sim"] = revenue_from_sim

    if not (
        results["storage_constraints_passed"]
        and results["release_constraints_passed"]
        and results["mass_balance_passed"]
        and results["revenue_verified"]
    ):
        results["overall_status"] = "FAIL"

    results["details"]["ecological_deficit"] = calculate_ecological_deficit(releases)
    results["details"]["min_release"] = float(np.min(releases))
    results["details"]["max_release"] = float(np.max(releases))
    results["details"]["min_storage"] = float(np.min(storage))
    results["details"]["max_storage"] = float(np.max(storage))

    return results


def generate_report(
    releases: np.ndarray,
    results: Dict[str, Any],
    save_path: str = "outputs/validation_report.txt",
) -> str:
    storage = simulate_storage(releases)
    revenue = calculate_revenue(releases)
    deficit = calculate_ecological_deficit(releases)

    lines = []
    lines.append("=" * 70)
    lines.append("RESERVOIR OPTIMIZATION - VALIDATION REPORT")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Overall Status: {results['overall_status']}")
    lines.append("")
    lines.append("-" * 70)
    lines.append("1. RELEASE SCHEDULE")
    lines.append("-" * 70)
    lines.append(f"{'Day':<6} {'Inflow':<10} {'Release':<10} {'Storage':<12} {'Price':<8} {'Revenue':<10}")
    lines.append("-" * 50)
    for t in range(NUM_DAYS):
        rev_t = releases[t] * HYDROPOWER_PRICE[t] * HYDROPOWER_CONVERSION
        lines.append(
            f"{t + 1:<6} {INFLOW[t]:<10.1f} {releases[t]:<10.4f} {storage[t + 1]:<12.1f} "
            f"{HYDROPOWER_PRICE[t]:<8.3f} ${rev_t:<8.2f}"
        )
    lines.append("")
    lines.append(f"Total Revenue: ${revenue:,.2f}")
    lines.append(f"Ecological Deficit: {deficit:.4f} m\u00b3/s \u00d7 days")
    lines.append("")

    lines.append("-" * 70)
    lines.append("2. CONSTRAINT VALIDATION")
    lines.append("-" * 70)
    lines.append("")
    lines.append(f"Storage Constraints: {'PASS' if results['storage_constraints_passed'] else 'FAIL'}")
    if results["storage_violations"]:
        for v in results["storage_violations"]:
            lines.append(f"  VIOLATION: {v}")
    lines.append("")
    lines.append(f"Release Constraints: {'PASS' if results['release_constraints_passed'] else 'FAIL'}")
    if results["release_violations"]:
        for v in results["release_violations"]:
            lines.append(f"  VIOLATION: {v}")
    lines.append("")
    lines.append(f"Mass Balance: {'PASS' if results['mass_balance_passed'] else 'FAIL'}")
    if results["mass_balance_errors"]:
        for e in results["mass_balance_errors"]:
            lines.append(f"  ERROR: {e}")
    lines.append("")
    lines.append(f"Revenue Verification: {'PASS' if results['revenue_verified'] else 'FAIL'}")
    lines.append("")
    lines.append("-" * 70)
    lines.append("3. SUMMARY STATISTICS")
    lines.append("-" * 70)
    lines.append(f"  Min Release: {results['details']['min_release']:.4f} m\u00b3/s")
    lines.append(f"  Max Release: {results['details']['max_release']:.4f} m\u00b3/s")
    lines.append(f"  Min Storage: {results['details']['min_storage']:,.2f} m\u00b3")
    lines.append(f"  Max Storage: {results['details']['max_storage']:,.2f} m\u00b3")
    lines.append(f"  Total Revenue: ${revenue:,.2f}")
    lines.append(f"  Ecological Deficit: {deficit:.4f}")
    lines.append("")
    lines.append("=" * 70)
    lines.append(f"FINAL RESULT: {results['overall_status']}")
    lines.append("=" * 70)

    report = "\n".join(lines)
    with open(save_path, "w") as f:
        f.write(report)

    logger.info("Validation report saved to %s", save_path)
    return report


def main() -> None:
    from reservoir_optimize import optimize_reservoir

    result = optimize_reservoir()
    releases = np.array(result["optimal_release_schedule"])
    validation_results = validate_solution(releases)
    generate_report(releases, validation_results)
    print(validation_results)


if __name__ == "__main__":
    main()
