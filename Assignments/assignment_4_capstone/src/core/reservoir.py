from dataclasses import dataclass


@dataclass
class Reservoir:
    name: str
    min_storage: float
    max_storage: float
    initial_storage: float
    max_release: float
    min_release: float
    head: float
    efficiency: float

    def mass_balance(self, storage: float, inflow: float, release: float, dt_hours: float = 24.0) -> float:
        dt_seconds = dt_hours * 3600.0
        inflow_vol = inflow * dt_seconds
        release_vol = release * dt_seconds
        storage_change = (inflow_vol - release_vol) / 1e6
        return storage + storage_change

    def hydropower(self, release: float) -> float:
        return release * 9.81 * self.head * self.efficiency / 1e6
