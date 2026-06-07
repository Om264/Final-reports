import numpy as np


def ecological_deficit(releases: np.ndarray, min_eco_flow: float = 10.0, penalty_weight: float = 1000.0) -> float:
    deficit = np.sum(np.maximum(0, min_eco_flow - releases))
    return deficit * penalty_weight


def hydropower_revenue(releases: np.ndarray, head: float = 50.0, efficiency: float = 0.85, price_per_mwh: float = 50.0, dt_hours: float = 24.0) -> float:
    dt_seconds = dt_hours * 3600.0
    power_mw = releases * 9.81 * head * efficiency / 1e6
    energy_mwh = power_mw * dt_hours
    return -np.sum(energy_mwh) * price_per_mwh


class MultiObjective:
    def __init__(self, eco_weight: float = 1.0, revenue_weight: float = 1.0, min_eco_flow: float = 10.0, head: float = 50.0, efficiency: float = 0.85) -> None:
        self.eco_weight = eco_weight
        self.revenue_weight = revenue_weight
        self.min_eco_flow = min_eco_flow
        self.head = head
        self.efficiency = efficiency

    def evaluate(self, releases: np.ndarray) -> float:
        eco = ecological_deficit(releases, self.min_eco_flow)
        rev = hydropower_revenue(releases, self.head, self.efficiency)
        return self.eco_weight * eco + self.revenue_weight * rev
