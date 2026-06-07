"""
Comprehensive test suite for the SCS-CN runoff calculation module.

Tests formula correctness, boundary conditions, input validation,
numerical precision, and edge cases.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from scscn_runoff import (
    calculate_runoff,
    calculate_runoff_series,
    compute_retention,
    compute_initial_abstraction,
    runoff_analytics,
)


class TestCalculateRunoff:
    """Tests for the calculate_runoff function."""

    def test_zero_rainfall(self):
        """P = 0 => Q = 0 regardless of CN."""
        result = calculate_runoff(0.0, 80.0)
        assert result["runoff"] == 0.0
        assert result["rainfall"] == 0.0

    def test_rainfall_less_than_initial_abstraction(self):
        """P < Ia => Q = 0."""
        result = calculate_runoff(5.0, 80.0)
        assert result["runoff"] == 0.0
        S = result["retention"]
        Ia = 0.2 * S
        assert 5.0 < Ia

    def test_rainfall_equals_initial_abstraction(self):
        """P = Ia => Q = 0 (boundary case)."""
        result = calculate_runoff(12.7, 80.0)
        assert result["runoff"] == 0.0

    def test_cn_zero(self):
        """CN = 0 => Q = 0 (all infiltration)."""
        result = calculate_runoff(50.0, 0.0)
        assert result["runoff"] == 0.0

    def test_cn_one_hundred(self):
        """CN = 100 => Q = P (impervious surface)."""
        P = 50.0
        result = calculate_runoff(P, 100.0)
        assert result["runoff"] == P
        assert result["retention"] == 0.0
        assert result["initial_abstraction"] == 0.0

    def test_standard_example(self):
        """P=50, CN=80 => Q ~ 13.8 mm (known reference value)."""
        result = calculate_runoff(50.0, 80.0)
        S = (25400.0 / 80.0) - 254.0
        Ia = 0.2 * S
        expected_Q = (50.0 - Ia) ** 2 / (50.0 - Ia + S)
        assert result["retention"] == pytest.approx(S, rel=1e-4)
        assert result["initial_abstraction"] == pytest.approx(Ia, rel=1e-4)
        assert result["runoff"] == pytest.approx(expected_Q, rel=1e-4)
        assert result["runoff"] == pytest.approx(13.8, abs=0.1)

    def test_runoff_never_exceeds_rainfall(self):
        """Q <= P must hold for all valid inputs."""
        test_cases = [
            (10.0, 95.0),
            (100.0, 60.0),
            (200.0, 85.0),
            (5.0, 99.0),
            (0.5, 70.0),
        ]
        for P, CN in test_cases:
            result = calculate_runoff(P, CN)
            assert (
                result["runoff"] <= result["rainfall"] + 1e-10
            ), f"Failed Q <= P for P={P}, CN={CN}: Q={result['runoff']}"

    def test_runoff_non_negative(self):
        """Q >= 0 must hold for all valid inputs."""
        test_cases = [
            (0.0, 50.0),
            (50.0, 60.0),
            (100.0, 80.0),
            (150.0, 95.0),
            (200.0, 100.0),
        ]
        for P, CN in test_cases:
            result = calculate_runoff(P, CN)
            assert result["runoff"] >= 0, f"Negative runoff for P={P}, CN={CN}"

    def test_higher_cn_more_runoff(self):
        """For fixed P, higher CN => more or equal runoff."""
        P = 50.0
        cn_values = [60, 70, 80, 90, 95, 100]
        runoff_values = [calculate_runoff(P, CN)["runoff"] for CN in cn_values]
        for i in range(len(runoff_values) - 1):
            assert runoff_values[i] <= runoff_values[i + 1] + 1e-10, (
                f"Non-monotonic at CN={cn_values[i]}: Q={runoff_values[i]} > "
                f"CN={cn_values[i+1]}: Q={runoff_values[i+1]}"
            )

    def test_large_rainfall_values(self):
        """Test numerical stability with large rainfall."""
        result = calculate_runoff(10000.0, 80.0)
        assert not math.isnan(result["runoff"])
        assert not math.isinf(result["runoff"])
        assert 0 <= result["runoff"] <= 10000.0

    def test_tiny_rainfall_values(self):
        """Test numerical stability with tiny rainfall."""
        result = calculate_runoff(1e-6, 80.0)
        assert not math.isnan(result["runoff"])
        assert result["runoff"] >= 0

    def test_cn_near_one_hundred(self):
        """Test CN near upper limit (99.999)."""
        result = calculate_runoff(50.0, 99.999)
        assert not math.isnan(result["runoff"])
        assert result["runoff"] <= 50.0
        assert result["runoff"] > 0

    def test_cn_near_zero(self):
        """Test CN near 0.001 (effectively all infiltration)."""
        result = calculate_runoff(50.0, 0.001)
        assert result["runoff"] == 0.0

    def test_invalid_negative_rainfall(self):
        """Negative P should raise ValueError."""
        with pytest.raises(ValueError, match="non-negative"):
            calculate_runoff(-10.0, 80.0)

    def test_invalid_cn_above_100(self):
        """CN > 100 should raise ValueError."""
        with pytest.raises(ValueError):
            calculate_runoff(50.0, 120.0)

    def test_invalid_cn_below_0(self):
        """CN < 0 should raise ValueError."""
        with pytest.raises(ValueError):
            calculate_runoff(50.0, -10.0)

    def test_docstring_example(self):
        """Verify the docstring example produces correct output."""
        result = calculate_runoff(50.0, 80.0)
        assert round(result["runoff"], 1) == 13.8
        assert result["retention"] == 63.5

    def test_cn_100_zero_rainfall(self):
        """P=0, CN=100 => Q=0 (no rain to become runoff)."""
        result = calculate_runoff(0.0, 100.0)
        assert result["runoff"] == 0.0
        assert result["retention"] == 0.0

    def test_multiple_scenarios_consistency(self):
        """Run multiple scenarios and verify results are physically consistent."""
        scenarios = [
            (0, 80, 0),
            (50, 100, 50),
            (50, 0, 0),
        ]
        for P, CN, expected_Q in scenarios:
            result = calculate_runoff(float(P), float(CN))
            assert result["runoff"] == pytest.approx(float(expected_Q), abs=1e-10), (
                f"Scenario P={P}, CN={CN}: expected Q={expected_Q}, "
                f"got Q={result['runoff']}"
            )

    def test_return_type(self):
        """Result dictionary has correct keys and types."""
        result = calculate_runoff(50.0, 80.0)
        expected_keys = {
            "rainfall", "curve_number", "retention",
            "initial_abstraction", "runoff",
        }
        assert set(result.keys()) == expected_keys
        assert isinstance(result["rainfall"], float)
        assert isinstance(result["curve_number"], float)
        assert isinstance(result["runoff"], float)

    def test_precision_known_values(self):
        """Test against hand-calculated known values."""
        test_cases = [
            (10.0, 80.0, 0.0),
            (25.0, 80.0, 2.00),
            (50.0, 80.0, 13.80),
            (75.0, 80.0, 30.85),
            (100.0, 80.0, 50.54),
        ]
        for P, CN, expected_runoff in test_cases:
            result = calculate_runoff(P, CN)
            assert result["runoff"] == pytest.approx(expected_runoff, abs=0.06), (
                f"P={P}, CN={CN}: expected Q~{expected_runoff}, got Q={result['runoff']}"
            )


class TestCalculateRunoffSeries:
    """Tests for the calculate_runoff_series function."""

    def test_return_type(self):
        """Returns a pandas DataFrame with expected columns."""
        df = calculate_runoff_series([10, 50], [60, 80])
        assert isinstance(df, pd.DataFrame)
        expected_cols = {
            "Rainfall", "Curve_Number", "Retention",
            "Initial_Abstraction", "Runoff",
        }
        assert set(df.columns) == expected_cols

    def test_number_of_rows(self):
        """For N rainfall and M CN values, expect N * M rows."""
        rainfall = [10, 20, 30]
        cn = [60, 70, 80, 90]
        df = calculate_runoff_series(rainfall, cn)
        assert len(df) == len(rainfall) * len(cn)

    def test_all_combinations_present(self):
        """All combinations of rainfall and CN are present."""
        rainfall = [10, 50]
        cn = [60, 80]
        df = calculate_runoff_series(rainfall, cn)
        for P in rainfall:
            for CN in cn:
                mask = (df["Rainfall"] == P) & (df["Curve_Number"] == CN)
                assert mask.any(), f"Missing combination P={P}, CN={CN}"

    def test_invalid_input_negative_rainfall(self):
        """Negative rainfall raises ValueError."""
        with pytest.raises(ValueError):
            calculate_runoff_series([-10, 50], [60, 80])

    def test_invalid_input_cn_out_of_range(self):
        """CN outside [0,100] raises ValueError."""
        with pytest.raises(ValueError):
            calculate_runoff_series([10, 50], [60, 120])

    def test_single_values(self):
        """Single values work (1x1 grid)."""
        df = calculate_runoff_series([50.0], [80.0])
        assert len(df) == 1
        assert df["Rainfall"].iloc[0] == 50.0
        assert df["Curve_Number"].iloc[0] == 80.0
        assert df["Runoff"].iloc[0] == pytest.approx(13.8, abs=0.1)


class TestHelperFunctions:
    """Tests for helper functions in scscn_runoff."""

    def test_compute_retention(self):
        S = compute_retention(80.0)
        assert S == 63.5

    def test_compute_retention_array(self):
        S_arr = compute_retention(np.array([60, 80, 100]))
        assert S_arr[0] == pytest.approx(169.33, rel=1e-3)
        assert S_arr[1] == 63.5
        assert S_arr[2] == 0.0

    def test_compute_retention_invalid(self):
        with pytest.raises(ValueError):
            compute_retention(0)
        with pytest.raises(ValueError):
            compute_retention(150)

    def test_compute_initial_abstraction(self):
        Ia = compute_initial_abstraction(80.0)
        assert Ia == pytest.approx(12.7)

    def test_runoff_analytics(self):
        df = pd.DataFrame({
            "Runoff": [0.0, 5.0, 10.0],
            "Curve_Number": [60, 80, 100],
            "Rainfall": [10.0, 20.0, 30.0],
        })
        stats = runoff_analytics(df)
        assert stats["average_runoff"] == 5.0
        assert stats["max_runoff"] == 10.0
        assert stats["min_runoff"] == 0.0
        assert stats["total_rainfall"] == 60.0
        assert stats["total_runoff"] == 15.0
