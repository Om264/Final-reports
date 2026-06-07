import numpy as np
import pytest
from src.utils.validation import Validator, ValidationError


class TestValidator:
    def setup_method(self) -> None:
        self.v = Validator()

    def test_valid_schedule_passes(self):
        errors = self.v.validate_all(
            releases=np.array([15.0, 20.0, 25.0]),
            storage=np.array([290.0, 285.0, 280.0]),
            s0=300.0, inflows=np.array([10.0, 15.0, 20.0]),
            s_min=50.0, s_max=500.0, q_min=10.0, q_max=100.0
        )
        assert len(errors) == 0

    def test_release_below_minimum(self):
        errors = self.v.validate_all(
            releases=np.array([5.0, 20.0, 25.0]),
            storage=np.array([290.0, 285.0, 280.0]),
            s0=300.0, inflows=np.array([10.0, 15.0, 20.0]),
            s_min=50.0, s_max=500.0, q_min=10.0, q_max=100.0
        )
        assert any("ecological minimum" in e for e in errors)

    def test_storage_above_maximum(self):
        errors = self.v.validate_all(
            releases=np.array([5.0, 5.0, 5.0]),
            storage=np.array([600.0, 700.0, 800.0]),
            s0=300.0, inflows=np.array([10.0, 10.0, 10.0]),
            s_min=50.0, s_max=500.0, q_min=10.0, q_max=100.0
        )
        assert any("above maximum" in e for e in errors)

    def test_negative_release(self):
        errors = self.v.validate_all(
            releases=np.array([-5.0, 20.0, 25.0]),
            storage=np.array([290.0, 285.0, 280.0]),
            s0=300.0, inflows=np.array([10.0, 15.0, 20.0]),
            s_min=0.0, s_max=500.0, q_min=0.0, q_max=100.0
        )
        assert any("Negative release" in e for e in errors)

    def test_assert_valid_raises(self):
        with pytest.raises(ValidationError):
            self.v.assert_valid(
                releases=np.array([5.0, 20.0]),
                storage=np.array([290.0, 285.0]),
                s0=300.0, inflows=np.array([10.0, 15.0]),
                s_min=50.0, s_max=500.0, q_min=10.0, q_max=100.0
            )

    def test_mass_balance_violation(self):
        errors = self.v.validate_all(
            releases=np.array([100.0, 100.0]),
            storage=np.array([100.0, 100.0]),
            s0=300.0, inflows=np.array([10.0, 10.0]),
            s_min=0.0, s_max=500.0, q_min=0.0, q_max=200.0
        )
        assert any("Mass balance" in e for e in errors)
