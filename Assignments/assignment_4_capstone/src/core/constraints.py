import numpy as np
from scipy.optimize import NonlinearConstraint, Bounds


class ConstraintBuilder:
    def __init__(self, n_periods: int, min_storage: float, max_storage: float, initial_storage: float, inflows: np.ndarray, min_release: float, max_release: float, dt_hours: float = 24.0) -> None:
        self.n = n_periods
        self.s_min = min_storage
        self.s_max = max_storage
        self.s0 = initial_storage
        self.q_in = inflows
        self.q_min = min_release
        self.q_max = max_release
        self.dt = dt_hours * 3600.0

    def storage_constraint(self) -> NonlinearConstraint:
        def storage_balance(releases: np.ndarray) -> np.ndarray:
            storage = np.zeros(self.n)
            s_prev = self.s0
            for t in range(self.n):
                inflow_vol = self.q_in[t] * self.dt / 1e6
                release_vol = releases[t] * self.dt / 1e6
                s_prev = s_prev + inflow_vol - release_vol
                storage[t] = s_prev
            return storage
        return NonlinearConstraint(storage_balance, np.full(self.n, self.s_min), np.full(self.n, self.s_max))

    def get_bounds(self) -> Bounds:
        return Bounds(lb=np.full(self.n, self.q_min), ub=np.full(self.n, self.q_max))
