import numpy as np
import pytest
from tradeoff_analysis import generate_pareto_frontier, WEIGHTS
from reservoir_model import calculate_revenue, calculate_ecological_deficit


class TestTradeoffGeneration:
    def test_pareto_frontier_generates_correct_length(self):
        revenues, deficits, solutions = generate_pareto_frontier()
        assert len(revenues) == len(WEIGHTS)
        assert len(deficits) == len(WEIGHTS)
        assert len(solutions) == len(WEIGHTS)

    def test_pareto_frontier_all_successful(self):
        revenues, deficits, solutions = generate_pareto_frontier()
        for sol in solutions:
            assert sol["optimization_success"], f"Optimization failed: {sol['message']}"

    def test_revenue_decreases_with_ecology_weight(self):
        revenues, deficits, solutions = generate_pareto_frontier()
        rev_only = revenues[0]
        eco_only = revenues[-1]
        assert rev_only >= eco_only, (
            f"Revenue-only ({rev_only}) should be >= ecology-only ({eco_only})"
        )

    def test_deficit_decreases_with_ecology_weight(self):
        revenues, deficits, solutions = generate_pareto_frontier()
        assert deficits[-1] <= deficits[0] + 1e-6

    def test_revenue_consistency(self):
        revenues, deficits, solutions = generate_pareto_frontier()
        for i, sol in enumerate(solutions):
            releases = np.array(sol["optimal_release_schedule"])
            expected_revenue = calculate_revenue(releases)
            assert abs(expected_revenue - revenues[i]) < 0.01

    def test_deficit_consistency(self):
        revenues, deficits, solutions = generate_pareto_frontier()
        for i, sol in enumerate(solutions):
            releases = np.array(sol["optimal_release_schedule"])
            expected_deficit = calculate_ecological_deficit(releases)
            assert abs(expected_deficit - deficits[i]) < 1e-6

    def test_pareto_frontier_non_empty(self):
        revenues, deficits, solutions = generate_pareto_frontier()
        assert len(revenues) > 0
        assert all(r > 0 for r in revenues)

    def test_weights_cover_full_range(self):
        w_rev = [w[0] for w in WEIGHTS]
        w_eco = [w[1] for w in WEIGHTS]
        assert w_rev[0] == 1.0 and w_rev[-1] == 0.0
        assert w_eco[0] == 0.0 and w_eco[-1] == 1.0


class TestPlotGeneration:
    def test_tradeoff_plot_does_not_error(self, monkeypatch):
        import matplotlib
        matplotlib.use("Agg")
        from tradeoff_analysis import plot_pareto_frontier

        revenues = [50000, 40000, 30000, 20000]
        deficits = [0, 10, 20, 30]
        try:
            plot_pareto_frontier(revenues, deficits, "/tmp/test_pareto.png")
        except Exception as e:
            pytest.fail(f"Plot generation failed: {e}")

    def test_storage_plot_does_not_error(self, monkeypatch):
        import matplotlib
        matplotlib.use("Agg")
        from tradeoff_analysis import plot_storage_trajectory

        solutions = [
            {
                "storage_trajectory": [500000, 600000, 700000, 800000, 700000, 600000, 500000, 400000],
                "optimal_release_schedule": [10, 10, 10, 10, 10, 10, 10],
                "total_revenue": 42000,
                "optimization_success": True,
                "status": 0,
                "message": "",
            }
        ]
        try:
            plot_storage_trajectory(solutions, "/tmp/test_storage.png")
        except Exception as e:
            pytest.fail(f"Storage plot generation failed: {e}")
