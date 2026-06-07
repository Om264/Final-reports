import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
import logging

from reservoir_optimize import optimize_reservoir
from reservoir_model import calculate_revenue, calculate_ecological_deficit

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

WEIGHTS: List[Tuple[float, float]] = [
    (1.0, 0.0),
    (0.9, 0.1),
    (0.8, 0.2),
    (0.7, 0.3),
    (0.6, 0.4),
    (0.5, 0.5),
    (0.4, 0.6),
    (0.3, 0.7),
    (0.2, 0.8),
    (0.1, 0.9),
    (0.0, 1.0),
]


def generate_pareto_frontier() -> Tuple[List[float], List[float], List[dict]]:
    revenues: List[float] = []
    ecological_deficits: List[float] = []
    solutions: List[dict] = []

    for w_rev, w_eco in WEIGHTS:
        logger.info("Running optimization w_revenue=%.1f, w_ecology=%.1f", w_rev, w_eco)
        result = optimize_reservoir(w_revenue=w_rev, w_ecology=w_eco, eco_bound=False)
        releases = np.array(result["optimal_release_schedule"])
        revenue = calculate_revenue(releases)
        deficit = calculate_ecological_deficit(releases)

        revenues.append(revenue)
        ecological_deficits.append(deficit)
        solutions.append(result)

        logger.info("  Revenue: $%.2f, Ecological Deficit: %.2f", revenue, deficit)

    return revenues, ecological_deficits, solutions


def plot_pareto_frontier(
    revenues: List[float],
    ecological_deficits: List[float],
    save_path: str = "outputs/tradeoff_analysis.png",
) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.scatter(ecological_deficits, revenues, color="steelblue", s=80, zorder=5)

    sorted_indices = np.argsort(ecological_deficits)
    sorted_deficits = [ecological_deficits[i] for i in sorted_indices]
    sorted_revenues = [revenues[i] for i in sorted_indices]
    ax.plot(sorted_deficits, sorted_revenues, "b--", alpha=0.5, label="Pareto Frontier")

    for i, (d, r) in enumerate(zip(ecological_deficits, revenues)):
        label = f"({d:.1f}, ${r:,.0f})"
        ax.annotate(
            label,
            (d, r),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )

    ax.set_xlabel("Ecological Deficit (m\u00b3/s \u00d7 days)", fontsize=12)
    ax.set_ylabel("Hydropower Revenue ($)", fontsize=12)
    ax.set_title("Pareto Frontier: Hydropower Revenue vs Ecological Deficit", fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(save_path, dpi=150)
    logger.info("Pareto frontier saved to %s", save_path)
    plt.close(fig)


def plot_storage_trajectory(
    solutions: List[dict],
    save_path: str = "outputs/storage_trajectory.png",
) -> None:
    from reservoir_model import MIN_STORAGE, MAX_STORAGE, INITIAL_STORAGE, NUM_DAYS

    fig, ax = plt.subplots(figsize=(10, 6))

    days = np.arange(NUM_DAYS + 1)

    for i, sol in enumerate(solutions):
        label = f"w_r={WEIGHTS[i][0]:.1f}, w_e={WEIGHTS[i][1]:.1f}"
        ax.plot(days, sol["storage_trajectory"], "-o", label=label, alpha=0.7)

    ax.axhline(y=MAX_STORAGE, color="r", linestyle="--", label=f"Max Storage ({MAX_STORAGE:,.0f} m\u00b3)")
    ax.axhline(y=MIN_STORAGE, color="r", linestyle="--", label=f"Min Storage ({MIN_STORAGE:,.0f} m\u00b3)")
    ax.axhline(y=INITIAL_STORAGE, color="gray", linestyle=":", label=f"Initial ({INITIAL_STORAGE:,.0f} m\u00b3)")

    ax.set_xlabel("Day", fontsize=12)
    ax.set_ylabel("Storage (m\u00b3)", fontsize=12)
    ax.set_title("Reservoir Storage Trajectories", fontsize=14)
    ax.legend(fontsize=8, loc="best")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(save_path, dpi=150)
    logger.info("Storage trajectory saved to %s", save_path)
    plt.close(fig)


def main() -> None:
    logger.info("Generating Pareto frontier...")
    revenues, deficits, solutions = generate_pareto_frontier()
    plot_pareto_frontier(revenues, deficits)
    plot_storage_trajectory(solutions)
    logger.info("Trade-off analysis complete.")


if __name__ == "__main__":
    main()
