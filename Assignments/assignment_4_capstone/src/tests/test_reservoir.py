import numpy as np
from src.core.reservoir import Reservoir


class TestReservoir:
    def setup_method(self) -> None:
        self.r = Reservoir(name="Test", min_storage=50.0, max_storage=500.0, initial_storage=300.0, max_release=100.0, min_release=10.0, head=50.0, efficiency=0.85)

    def test_mass_balance_no_change(self):
        assert self.r.mass_balance(300.0, 0.0, 0.0) == 300.0

    def test_mass_balance_inflow_only(self):
        s = self.r.mass_balance(300.0, 10.0, 0.0)
        expected = 300.0 + (10.0 * 86400 / 1e6)
        assert abs(s - expected) < 1e-6

    def test_mass_balance_release_only(self):
        s = self.r.mass_balance(300.0, 0.0, 10.0)
        expected = 300.0 - (10.0 * 86400 / 1e6)
        assert abs(s - expected) < 1e-6

    def test_hydropower_zero(self):
        assert self.r.hydropower(0.0) == 0.0

    def test_hydropower_positive(self):
        assert self.r.hydropower(50.0) > 0.0
