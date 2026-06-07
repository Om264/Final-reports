import numpy as np
from scipy.optimize import minimize, OptimizeResult
from typing import Optional, Dict, Any
import logging

from reservoir_model import (
    simulate_storage,
    calculate_revenue,
    compute_objective,
    MIN_STORAGE,
    MAX_STORAGE,
    ECOLOGICAL_RELEASE,
    MAX_RELEASE,
    INITIAL_STORAGE,
    NUM_DAYS,
    SECONDS_PER_DAY,
    INFLOW,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _make_objective(w_revenue: float, w_ecology: float):
    def objective(releases: np.ndarray) -> float:
        return compute_objective(releases, w_revenue, w_ecology)
    return objective


def _make_storage_constraints() -> list[dict[str, Any]]:
    constraints = []
    for t in range(1, NUM_DAYS + 1):
        cumulative_inflow = float(np.sum(INFLOW[:t]) * SECONDS_PER_DAY)

        def lower_cons(releases: np.ndarray, day: int = t, cum_inflow: float = cumulative_inflow) -> float:
            cum_release = float(np.sum(np.array(releases)[:day])) * SECONDS_PER_DAY
            storage_t = INITIAL_STORAGE + cum_inflow - cum_release
            return storage_t - MIN_STORAGE
        constraints.append({"type": "ineq", "fun": lower_cons})

        def upper_cons(releases: np.ndarray, day: int = t, cum_inflow: float = cumulative_inflow) -> float:
            cum_release = float(np.sum(np.array(releases)[:day])) * SECONDS_PER_DAY
            storage_t = INITIAL_STORAGE + cum_inflow - cum_release
            return MAX_STORAGE - storage_t
        constraints.append({"type": "ineq", "fun": upper_cons})
    return constraints


def _check_feasibility(releases: np.ndarray, eco_bound: bool = True) -> bool:
    storage = simulate_storage(np.array(releases))
    if np.any(storage < MIN_STORAGE - 1.0) or np.any(storage > MAX_STORAGE + 1.0):
        return False
    lower = ECOLOGICAL_RELEASE if eco_bound else 0.0
    if np.any(np.array(releases) < lower - 1e-6) or np.any(np.array(releases) > MAX_RELEASE + 1e-6):
        return False
    return True


def optimize_reservoir(
    w_revenue: float = 1.0,
    w_ecology: float = 0.0,
    eco_bound: bool = True,
    x0: Optional[np.ndarray] = None,
    method: str = "SLSQP",
    options: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    if x0 is None:
        x0 = np.array(INFLOW, dtype=float)

    lower_bound = ECOLOGICAL_RELEASE if eco_bound else 0.0
    bounds = [(lower_bound, MAX_RELEASE)] * NUM_DAYS
    constraints = _make_storage_constraints()

    default_options = {
        "ftol": 1e-12,
        "maxiter": 2000,
        "disp": False,
    }
    if options:
        default_options.update(options)

    objective = _make_objective(w_revenue, w_ecology)

    logger.info(
        "Starting optimization with w_revenue=%.2f, w_ecology=%.2f",
        w_revenue,
        w_ecology,
    )

    result: OptimizeResult = minimize(
        objective,
        x0,
        method=method,
        bounds=bounds,
        constraints=constraints,
        options=default_options,
    )

    optimal_releases = result.x
    storage = simulate_storage(optimal_releases)
    revenue = calculate_revenue(optimal_releases)
    feasible = _check_feasibility(optimal_releases, eco_bound)
    success = bool(result.success) or feasible

    logger.info("Optimization %s (status=%d, feasible=%s)", "succeeded" if success else "failed", result.status, feasible)
    logger.info("Total revenue: $%.2f", revenue)

    return {
        "optimal_release_schedule": optimal_releases.tolist(),
        "storage_trajectory": storage.tolist(),
        "total_revenue": revenue,
        "optimization_success": success,
        "status": result.status,
        "message": result.message,
    }


if __name__ == "__main__":
    result = optimize_reservoir()
    print("Optimal Release Schedule:", result["optimal_release_schedule"])
    print("Storage Trajectory:", result["storage_trajectory"])
    print("Total Revenue: ${:,.2f}".format(result["total_revenue"]))
    print("Optimization Success:", result["optimization_success"])
