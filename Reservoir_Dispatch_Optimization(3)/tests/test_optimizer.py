import numpy as np
import pytest
from reservoir_optimize import optimize_reservoir
from reservoir_model import (
    calculate_revenue,
    calculate_ecological_deficit,
    ECOLOGICAL_RELEASE,
    MAX_RELEASE,
    NUM_DAYS,
)


class TestOptimizer:
    def test_optimization_converges(self):
        result = optimize_reservoir()
        assert result["optimization_success"], (
            f"Optimization failed: {result['message']}"
        )

    def test_feasible_solution_generated(self):
        result = optimize_reservoir()
        releases = np.array(result["optimal_release_schedule"])
        assert len(releases) == NUM_DAYS
        assert np.all(releases >= ECOLOGICAL_RELEASE - 1e-6)
        assert np.all(releases <= MAX_RELEASE + 1e-6)

    def test_revenue_calculated_correctly(self):
        result = optimize_reservoir()
        releases = np.array(result["optimal_release_schedule"])
        revenue = calculate_revenue(releases)
        assert abs(revenue - result["total_revenue"]) < 0.01
        assert revenue > 0

    def test_revenue_single_objective(self):
        result = optimize_reservoir(w_revenue=1.0, w_ecology=0.0)
        assert result["optimization_success"]

    def test_ecology_single_objective(self):
        result = optimize_reservoir(w_revenue=0.0, w_ecology=1.0)
        assert result["optimization_success"]
        releases = np.array(result["optimal_release_schedule"])
        deficit = calculate_ecological_deficit(releases)
        assert deficit < 1e-6

    def test_different_initial_guess(self):
        x0 = np.full(NUM_DAYS, 20.0)
        result = optimize_reservoir(x0=x0)
        assert result["optimization_success"]

    def test_storage_trajectory_length(self):
        result = optimize_reservoir()
        assert len(result["storage_trajectory"]) == NUM_DAYS + 1

    def test_returns_expected_keys(self):
        result = optimize_reservoir()
        expected_keys = {
            "optimal_release_schedule",
            "storage_trajectory",
            "total_revenue",
            "optimization_success",
            "status",
            "message",
        }
        assert set(result.keys()) == expected_keys
