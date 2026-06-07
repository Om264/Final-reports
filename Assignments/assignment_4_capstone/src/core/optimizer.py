import numpy as np
from scipy.optimize import minimize, OptimizeResult
from .constraints import ConstraintBuilder
from .objectives import MultiObjective


class ReservoirOptimizer:
    def __init__(self, n_periods: int = 7, min_storage: float = 50.0, max_storage: float = 500.0, initial_storage: float = 300.0, inflows: np.ndarray | None = None, min_release: float = 10.0, max_release: float = 100.0, head: float = 50.0, efficiency: float = 0.85) -> None:
        self.n = n_periods
        self.s_min = min_storage
        self.s_max = max_storage
        self.s0 = initial_storage
        self.q_in = inflows if inflows is not None else np.full(n_periods, 20.0)
        self.q_min = min_release
        self.q_max = max_release
        self.head = head
        self.efficiency = efficiency
        self.objective = MultiObjective(head=head, efficiency=efficiency, min_eco_flow=min_release)
        self.constraints = ConstraintBuilder(n_periods, min_storage, max_storage, initial_storage, self.q_in, min_release, max_release)

    def solve(self, x0: np.ndarray | None = None, method: str = "SLSQP") -> OptimizeResult:
        if x0 is None:
            x0 = np.full(self.n, self.q_min + 5.0)
        return minimize(fun=self.objective.evaluate, x0=x0, method=method, bounds=self.constraints.get_bounds(), constraints=[self.constraints.storage_constraint()], options={"ftol": 1e-9, "maxiter": 1000})

    def compute_schedule(self, result: OptimizeResult) -> dict:
        releases = result.x
        storage = np.zeros(self.n)
        s_prev = self.s0
        for t in range(self.n):
            inflow_vol = self.q_in[t] * 86400 / 1e6
            release_vol = releases[t] * 86400 / 1e6
            s_prev = s_prev + inflow_vol - release_vol
            storage[t] = s_prev
        return {
            "day": list(range(1, self.n + 1)),
            "inflow": self.q_in.tolist(),
            "release": releases.tolist(),
            "storage": storage.tolist(),
            "eco_flow_satisfied": (releases >= self.q_min).tolist(),
            "hydropower_mw": (releases * 9.81 * self.head * self.efficiency / 1e6).tolist(),
        }
