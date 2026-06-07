import numpy as np
from src.core.optimizer import ReservoirOptimizer


class TestOptimizer:
    def test_optimizer_returns_result(self):
        opt = ReservoirOptimizer(n_periods=7)
        result = opt.solve()
        assert result.success
        assert len(result.x) == 7

    def test_releases_within_bounds(self):
        opt = ReservoirOptimizer(n_periods=7, min_release=10.0, max_release=100.0)
        result = opt.solve()
        assert np.all(result.x >= 10.0 - 1e-6)
        assert np.all(result.x <= 100.0 + 1e-6)

    def test_schedule_structure(self):
        opt = ReservoirOptimizer(n_periods=7)
        sched = opt.compute_schedule(opt.solve())
        assert len(sched["day"]) == 7
        assert len(sched["release"]) == 7
        assert len(sched["storage"]) == 7

    def test_storage_trajectory(self):
        opt = ReservoirOptimizer(n_periods=7, initial_storage=300.0, min_storage=50.0, max_storage=500.0, inflows=np.full(7, 20.0))
        sched = opt.compute_schedule(opt.solve())
        for s in sched["storage"]:
            assert 50.0 - 1e-6 <= s <= 500.0 + 1e-6
