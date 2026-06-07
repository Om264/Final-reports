import numpy as np
import pytest
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
)
from reservoir_optimize import optimize_reservoir
from validation import validate_solution


class TestStorageBounds:
    def test_storage_within_bounds_optimal(self):
        result = optimize_reservoir()
        releases = np.array(result["optimal_release_schedule"])
        storage = simulate_storage(releases)
        assert np.all(storage >= MIN_STORAGE - 1.0)
        assert np.all(storage <= MAX_STORAGE + 1.0)

    def test_initial_storage_within_bounds(self):
        assert MIN_STORAGE <= INITIAL_STORAGE <= MAX_STORAGE

    def test_storage_at_max_boundary(self):
        releases = INFLOW.copy()
        storage = simulate_storage(releases)
        assert np.all(storage >= MIN_STORAGE - 1.0)
        assert np.all(storage <= MAX_STORAGE + 1.0)


class TestReleaseBounds:
    def test_releases_within_bounds_optimal(self):
        result = optimize_reservoir()
        releases = np.array(result["optimal_release_schedule"])
        assert np.all(releases >= ECOLOGICAL_RELEASE - 1e-6)
        assert np.all(releases <= MAX_RELEASE + 1e-6)

    def test_expected_schedule_is_feasible(self):
        releases = np.array([12.5, 10.2, 10.0, 10.0, 13.2, 15.8, 18.0])
        validation = validate_solution(releases)
        assert validation["release_constraints_passed"]
        assert validation["storage_constraints_passed"]

    def test_release_below_eco_violates(self):
        releases = np.full(NUM_DAYS, ECOLOGICAL_RELEASE - 5)
        validation = validate_solution(releases)
        assert not validation["release_constraints_passed"]

    def test_release_above_max_violates(self):
        releases = np.full(NUM_DAYS, MAX_RELEASE + 10)
        validation = validate_solution(releases)
        assert not validation["release_constraints_passed"]


class TestMassBalance:
    def test_mass_balance_holds(self):
        result = optimize_reservoir()
        releases = np.array(result["optimal_release_schedule"])
        storage = simulate_storage(releases)

        storage_check = np.zeros(NUM_DAYS + 1)
        storage_check[0] = INITIAL_STORAGE
        for t in range(NUM_DAYS):
            storage_check[t + 1] = storage_check[t] + (INFLOW[t] - releases[t]) * SECONDS_PER_DAY

        assert np.allclose(storage, storage_check, atol=1.0)

    def test_mass_balance_manual(self):
        releases = np.array([15.0, 10.0, 10.0, 8.0, 12.0, 15.0, 18.0])
        storage = simulate_storage(releases)

        expected = np.zeros(NUM_DAYS + 1)
        expected[0] = INITIAL_STORAGE
        for t in range(NUM_DAYS):
            expected[t + 1] = expected[t] + (INFLOW[t] - releases[t]) * SECONDS_PER_DAY

        assert np.allclose(storage, expected, atol=1.0)

    def test_mass_balance_all_inflow_released(self):
        releases = INFLOW.copy()
        storage = simulate_storage(releases)
        expected = np.full(NUM_DAYS + 1, INITIAL_STORAGE)
        assert np.allclose(storage, expected, atol=1.0)


class TestEcologicalDeficit:
    def test_no_deficit_when_above_eco(self):
        releases = np.full(NUM_DAYS, ECOLOGICAL_RELEASE + 5)
        deficit = calculate_ecological_deficit(releases)
        assert deficit == 0.0

    def test_deficit_when_below_eco(self):
        releases = np.full(NUM_DAYS, ECOLOGICAL_RELEASE - 5)
        deficit = calculate_ecological_deficit(releases)
        assert deficit == pytest.approx(5.0 * NUM_DAYS)

    def test_partial_deficit(self):
        releases = np.array([5.0, 10.0, 8.0, 10.0, 12.0, 10.0, 3.0])
        deficit = calculate_ecological_deficit(releases)
        expected = (10 - 5) + (10 - 8) + (10 - 3)
        assert deficit == pytest.approx(float(expected))

    def test_zero_deficit_at_eco(self):
        releases = np.full(NUM_DAYS, ECOLOGICAL_RELEASE)
        deficit = calculate_ecological_deficit(releases)
        assert deficit == 0.0


class TestRevenueCalculation:
    def test_revenue_zero_when_no_release(self):
        releases = np.zeros(NUM_DAYS)
        revenue = calculate_revenue(releases)
        assert revenue == 0.0

    def test_revenue_positive(self):
        releases = np.full(NUM_DAYS, ECOLOGICAL_RELEASE)
        revenue = calculate_revenue(releases)
        assert revenue > 0.0

    def test_revenue_increases_with_release(self):
        low_releases = np.full(NUM_DAYS, ECOLOGICAL_RELEASE)
        high_releases = np.full(NUM_DAYS, ECOLOGICAL_RELEASE + 10)
        rev_low = calculate_revenue(low_releases)
        rev_high = calculate_revenue(high_releases)
        assert rev_high > rev_low
