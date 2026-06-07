import numpy as np
from src.core.constraints import ConstraintBuilder


class TestConstraints:
    def test_storage_constraint_shape(self):
        cb = ConstraintBuilder(7, 50, 500, 300, np.full(7, 20.0), 10, 100)
        con = cb.storage_constraint()
        storage = con.fun(np.full(7, 15.0))
        assert len(storage) == 7

    def test_storage_decreases_with_high_release(self):
        cb = ConstraintBuilder(3, 0, 1000, 300, np.full(3, 10.0), 10, 200)
        storage = cb.storage_constraint().fun(np.full(3, 100.0))
        assert storage[0] < 300.0
        assert storage[1] < storage[0]
        assert storage[2] < storage[1]

    def test_storage_increases_with_low_release(self):
        cb = ConstraintBuilder(3, 0, 1000, 100, np.full(3, 50.0), 5, 200)
        storage = cb.storage_constraint().fun(np.full(3, 5.0))
        assert storage[0] > 100.0

    def test_release_bounds(self):
        cb = ConstraintBuilder(7, 50, 500, 300, np.full(7, 20.0), 10, 100)
        bounds = cb.get_bounds()
        assert np.all(bounds.lb == 10.0)
        assert np.all(bounds.ub == 100.0)
