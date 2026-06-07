import numpy as np


class ValidationError(Exception):
    pass


class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def check_storage_bounds(self, storage: np.ndarray, s_min: float, s_max: float) -> None:
        if np.any(storage < s_min - 1e-6):
            self.errors.append(f"Storage below minimum ({s_min})")
        if np.any(storage > s_max + 1e-6):
            self.errors.append(f"Storage above maximum ({s_max})")

    def check_release_bounds(self, releases: np.ndarray, q_min: float, q_max: float) -> None:
        if np.any(releases < q_min - 1e-6):
            self.errors.append(f"Release below ecological minimum ({q_min})")
        if np.any(releases > q_max + 1e-6):
            self.errors.append(f"Release above maximum ({q_max})")

    def check_mass_balance(self, storage: np.ndarray, s0: float, inflows: np.ndarray, releases: np.ndarray, dt_hours: float = 24.0) -> None:
        dt = dt_hours * 3600.0
        s_calc = float(s0)
        for t in range(len(storage)):
            s_calc += (inflows[t] - releases[t]) * dt / 1e6
        if abs(s_calc - storage[-1]) > 1e-3:
            self.errors.append(f"Mass balance violation: expected {s_calc:.2f}, got {storage[-1]:.2f}")

    def check_physical_plausibility(self, releases: np.ndarray, storage: np.ndarray) -> None:
        if np.any(releases < 0):
            self.errors.append("Negative release values")
        if np.any(storage < 0):
            self.errors.append("Negative storage")

    def validate_all(self, releases, storage, s0, inflows, s_min, s_max, q_min, q_max) -> list[str]:
        self.errors = []
        self.check_storage_bounds(storage, s_min, s_max)
        self.check_release_bounds(releases, q_min, q_max)
        self.check_mass_balance(storage, s0, inflows, releases)
        self.check_physical_plausibility(releases, storage)
        return self.errors

    def assert_valid(self, **kwargs) -> None:
        errors = self.validate_all(**kwargs)
        if errors:
            raise ValidationError("\n".join(errors))
