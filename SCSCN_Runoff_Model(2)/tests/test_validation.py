"""
Tests for the physical validation module.

Verifies that all validation checks correctly identify valid and
invalid physical conditions in the SCS-CN model.
"""

from __future__ import annotations

import pandas as pd
import pytest

from scscn_runoff import calculate_runoff
from validation import (
    validate_runoff_non_negative,
    validate_runoff_not_exceed_rainfall,
    validate_runoff_model,
    generate_validation_report,
)


class TestPhysicalConstraints:
    """Verify physical constraint checks."""

    def test_q_non_negative_across_range(self):
        """Q >= 0 for a wide range of inputs."""
        test_cases = [
            (0, 50), (10, 60), (25, 70), (50, 80), (75, 90),
            (100, 100), (150, 85), (200, 95), (500, 50), (1000, 99),
        ]
        for P, CN in test_cases:
            result = calculate_runoff(float(P), float(CN))
            assert result["runoff"] >= 0, f"Negative runoff: P={P}, CN={CN}"

    def test_q_never_exceeds_p(self):
        """Q <= P for all cases."""
        test_cases = [
            (10, 95), (25, 85), (50, 100), (100, 60), (200, 80),
            (300, 90), (1, 99), (0.5, 70), (10000, 50),
        ]
        for P, CN in test_cases:
            result = calculate_runoff(float(P), float(CN))
            assert result["runoff"] <= result["rainfall"] + 1e-10, (
                f"Q > P: P={P}, CN={CN}, Q={result['runoff']}"
            )

    def test_monotonic_increasing_with_cn(self):
        """Higher CN always yields >= runoff for fixed P."""
        P = 50.0
        cns = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100]
        prev_q = -1.0
        for CN in cns:
            result = calculate_runoff(P, float(CN))
            assert result["runoff"] >= prev_q - 1e-10, (
                f"Non-monotonic at CN={CN}: Q={result['runoff']} < prev Q={prev_q}"
            )
            prev_q = result["runoff"]

    def test_zero_runoff_when_p_less_than_ia(self):
        """Q = 0 whenever P < Ia."""
        for CN in [60, 70, 80, 90, 95]:
            result = calculate_runoff(1.0, float(CN))
            S = result["retention"]
            Ia = 0.2 * S
            if 1.0 < Ia:
                assert result["runoff"] == 0.0, (
                    f"P < Ia but Q != 0: CN={CN}, S={S}, Ia={Ia}"
                )

    def test_cn_100_impervious(self):
        """CN=100 => S=0, Ia=0, Q=P."""
        for P in [0, 10, 25, 50, 100, 200]:
            result = calculate_runoff(float(P), 100.0)
            assert result["retention"] == 0.0
            assert result["initial_abstraction"] == 0.0
            assert result["runoff"] == float(P)

    def test_cn_0_infiltration(self):
        """CN=0 => Q=0."""
        for P in [0, 10, 25, 50, 100, 200]:
            result = calculate_runoff(float(P), 0.0)
            assert result["runoff"] == 0.0

    def test_no_runoff_for_small_events(self):
        """Small rainfall events produce no runoff for low CN."""
        small_rainfalls = [1, 2, 3, 4, 5]
        for P in small_rainfalls:
            result = calculate_runoff(float(P), 60.0)
            S = result["retention"]
            Ia = 0.2 * S
            if P < Ia:
                assert result["runoff"] == 0.0

    def test_validate_runoff_non_negative(self):
        df = pd.DataFrame({"Runoff": [0.0, 1.5, -0.1]})
        result = validate_runoff_non_negative(df)
        assert result["passed"] is False
        assert result["violations"] == 1

    def test_validate_runoff_not_exceed_rainfall(self):
        df = pd.DataFrame({"Runoff": [1.0, 6.0], "Rainfall": [5.0, 5.0]})
        result = validate_runoff_not_exceed_rainfall(df)
        assert result["passed"] is False
        assert result["violations"] == 1

    def test_validate_runoff_model_full(self):
        report = validate_runoff_model(
            rainfall_range=(0, 50, 11),
            cn_range=(1, 100, 10),
            verbose=False,
        )
        assert report["tests_passed"] is True
        assert report["passed_tests"] == 7

    def test_generate_validation_report(self):
        report = validate_runoff_model(
            rainfall_range=(0, 50, 6),
            cn_range=(1, 100, 5),
            verbose=False,
        )
        text = generate_validation_report(report)
        assert "PASS" in text
        assert "SCS-CN" in text

    def test_runoff_ratio_increases_with_cn(self):
        """Runoff ratio (Q/P) increases with CN for fixed P."""
        P = 100.0
        cns = [50, 60, 70, 80, 90, 95]
        ratios = []
        for CN in cns:
            result = calculate_runoff(P, float(CN))
            ratios.append(result["runoff"] / P)
        for i in range(len(ratios) - 1):
            assert ratios[i] <= ratios[i + 1] + 1e-10, (
                f"Runoff ratio decreased: CN={cns[i]} ratio={ratios[i]:.4f} -> "
                f"CN={cns[i+1]} ratio={ratios[i+1]:.4f}"
            )
