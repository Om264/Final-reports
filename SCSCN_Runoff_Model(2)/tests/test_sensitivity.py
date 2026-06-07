"""
Tests for the sensitivity analysis module.

Verifies correct plot generation, sensitivity calculations,
and data consistency in the analysis outputs.
"""

from __future__ import annotations

import math
import os
import tempfile

import matplotlib
import numpy as np
import pandas as pd
import pytest

matplotlib.use("Agg")

import runoff_examples
from scscn_runoff import calculate_runoff, calculate_runoff_series, runoff_analytics
from sensitivity_analysis import (
    generate_analytics_report,
    rainfall_vs_runoff_comparison,
    sensitivity_cn_vs_runoff,
)


class TestSensitivityCalculations:
    """Verify sensitivity analysis calculations."""

    def test_cn_vs_runoff_monotonic(self):
        """Runoff increases monotonically with CN at fixed P."""
        P = 50.0
        cns = [60, 70, 80, 90, 95, 100]
        runoff_vals = [calculate_runoff(P, CN)["runoff"] for CN in cns]
        for i in range(len(runoff_vals) - 1):
            assert runoff_vals[i] <= runoff_vals[i + 1] + 1e-10

    def test_sensitivity_curve_generation(self):
        """sensitivity_cn_vs_runoff produces a valid figure."""
        fig, ax = sensitivity_cn_vs_runoff(
            P=50.0,
            cn_values=[60, 70, 80, 90, 95, 100],
            save_path=None,
        )
        assert fig is not None
        assert ax is not None
        assert len(ax.lines) > 0
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_comparison_plot_generation(self):
        """rainfall_vs_runoff_comparison produces a valid figure."""
        fig, ax = rainfall_vs_runoff_comparison(
            rainfall_max=150.0,
            cn_values=[60, 80, 95],
            save_path=None,
        )
        assert fig is not None
        assert ax is not None
        assert len(ax.lines) > 0
        import matplotlib.pyplot as plt
        plt.close(fig)

    def test_save_sensitivity_curve(self):
        """Sensitivity curve saves correctly to disk."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            path = tmp.name
        try:
            fig, _ = sensitivity_cn_vs_runoff(
                P=50.0,
                cn_values=[60, 80, 100],
                save_path=path,
            )
            import matplotlib.pyplot as plt
            plt.close(fig)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_save_comparison_plot(self):
        """Comparison plot saves correctly to disk."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            path = tmp.name
        try:
            fig, _ = rainfall_vs_runoff_comparison(
                rainfall_max=100.0,
                cn_values=[60, 80],
                save_path=path,
            )
            import matplotlib.pyplot as plt
            plt.close(fig)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_analytics_report_structure(self):
        """Analytics report CSV has correct structure."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            path = tmp.name
        try:
            df = generate_analytics_report(
                rainfall_values=[10, 50],
                cn_values=[60, 80],
                save_path=path,
            )
            assert isinstance(df, pd.DataFrame)
            assert os.path.exists(path)
            content = pd.read_csv(path)
            assert list(content.columns) == [
                "Rainfall", "Curve_Number", "Retention",
                "Initial_Abstraction", "Runoff",
            ]
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def test_analytics_report_data_correctness(self):
        """Analytics report contains valid data."""
        df = generate_analytics_report(
            rainfall_values=[10, 20, 30],
            cn_values=[60, 70, 80],
            save_path=None,
        )
        assert len(df) == 9
        assert df["Runoff"].min() >= 0
        assert (df["Runoff"] <= df["Rainfall"] + 1e-10).all()

    def test_runoff_analytics_statistics(self):
        """runoff_analytics computes correct statistics."""
        df = pd.DataFrame(
            {
                "Runoff": [0.0, 1.0, 2.0, 3.0, 4.0],
                "Curve_Number": [60, 70, 80, 90, 100],
                "Rainfall": [10.0, 10.0, 10.0, 10.0, 10.0],
            }
        )
        stats = runoff_analytics(df)
        assert stats["average_runoff"] == pytest.approx(2.0)
        assert stats["max_runoff"] == 4.0
        assert stats["min_runoff"] == 0.0
        assert stats["total_runoff"] == 10.0

    def test_different_p_values_sensitivity(self):
        """Sensitivity analysis works for various P values."""
        for P in [25, 50, 75, 100]:
            cns = [60, 80, 95]
            runoff_vals = [calculate_runoff(float(P), float(CN))["runoff"] for CN in cns]
            for i in range(len(runoff_vals) - 1):
                assert runoff_vals[i] <= runoff_vals[i + 1] + 1e-10

    def test_runoff_convergence(self):
        """As P increases, Q/P approaches 1 for all CN > 0."""
        cns = [50, 70, 90]
        for CN in cns:
            Q1 = calculate_runoff(1000.0, float(CN))["runoff"]
            Q2 = calculate_runoff(10000.0, float(CN))["runoff"]
            ratio1 = Q1 / 1000.0
            ratio2 = Q2 / 10000.0
            assert ratio2 >= ratio1, f"CN={CN}: Q/P ratio should increase with P"

    def test_full_sensitivity_pipeline(self):
        """Run the full sensitivity pipeline without errors."""
        from sensitivity_analysis import run_full_sensitivity_analysis
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_full_sensitivity_analysis(output_dir=tmpdir)
            assert "sensitivity_curve" in result
            assert "runoff_comparison" in result
            assert "analysis_report" in result
            for key, path in result.items():
                assert os.path.exists(path), f"{key} not found at {path}"

    def test_runoff_examples_module(self):
        """Verify runoff_examples module functions work."""
        result = runoff_examples.example_woods_good_condition()
        assert result["curve_number"] == 65
        assert result["runoff"] > 0

        result = runoff_examples.example_pasture_fair_condition()
        assert result["curve_number"] == 80

        result = runoff_examples.example_urban_residential()
        assert result["curve_number"] == 92

        result = runoff_examples.example_impervious_surface()
        assert result["curve_number"] == 100
        assert result["runoff"] == 50.0

    def test_runoff_examples_comparison(self):
        """Verify the comparison DataFrame is correct."""
        df = runoff_examples.run_all_examples()
        assert len(df) == 4
        assert list(df["CN"]) == [65, 80, 92, 100]
        assert all(df["Runoff Q (mm)"] <= 50.0)
        assert df["Runoff Q (mm)"].iloc[-1] == 50.0  # CN=100
