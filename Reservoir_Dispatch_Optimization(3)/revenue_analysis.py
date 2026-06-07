import numpy as np
import pandas as pd
from typing import Dict, Any
import logging

from reservoir_model import (
    calculate_revenue,
    NUM_DAYS,
    HYDROPOWER_PRICE,
    HYDROPOWER_CONVERSION,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def analyze_revenue(releases: np.ndarray) -> Dict[str, Any]:
    daily_revenue = releases * HYDROPOWER_PRICE * HYDROPOWER_CONVERSION
    total_revenue = float(np.sum(daily_revenue))
    avg_revenue = float(np.mean(daily_revenue))
    max_revenue_day = int(np.argmax(daily_revenue)) + 1
    max_revenue_value = float(np.max(daily_revenue))
    contribution_pct = (daily_revenue / total_revenue * 100).tolist()

    return {
        "daily_revenue": daily_revenue.tolist(),
        "total_revenue": total_revenue,
        "average_daily_revenue": avg_revenue,
        "max_revenue_day": max_revenue_day,
        "max_revenue_value": max_revenue_value,
        "revenue_contribution_pct": contribution_pct,
    }


def export_revenue_csv(
    releases: np.ndarray,
    save_path: str = "outputs/revenue_breakdown.csv",
) -> None:
    from reservoir_model import INFLOW, simulate_storage

    storage = simulate_storage(releases)
    daily_revenue = releases * HYDROPOWER_PRICE * HYDROPOWER_CONVERSION

    data = {
        "Day": list(range(1, NUM_DAYS + 1)),
        "Inflow": INFLOW.tolist(),
        "Release": releases.tolist(),
        "Storage": [storage[t] for t in range(1, NUM_DAYS + 1)],
        "Price": HYDROPOWER_PRICE.tolist(),
        "Revenue": daily_revenue.tolist(),
    }

    df = pd.DataFrame(data)
    df.to_csv(save_path, index=False)
    logger.info("Revenue breakdown saved to %s", save_path)


def export_schedule_csv(
    releases: np.ndarray,
    save_path: str = "outputs/optimal_schedule.csv",
) -> None:
    from reservoir_model import INFLOW, simulate_storage

    storage = simulate_storage(releases)
    daily_revenue = releases * HYDROPOWER_PRICE * HYDROPOWER_CONVERSION

    data = {
        "Day": list(range(1, NUM_DAYS + 1)),
        "Inflow": INFLOW.tolist(),
        "Release": releases.tolist(),
        "Storage": [storage[t] for t in range(1, NUM_DAYS + 1)],
        "Price": HYDROPOWER_PRICE.tolist(),
        "Daily_Revenue": daily_revenue.tolist(),
    }

    df = pd.DataFrame(data)
    df.to_csv(save_path, index=False)
    logger.info("Optimal schedule saved to %s", save_path)


def main() -> None:
    from reservoir_optimize import optimize_reservoir

    result = optimize_reservoir()
    releases = np.array(result["optimal_release_schedule"])

    analysis = analyze_revenue(releases)
    print("Revenue Analysis:")
    print(f"  Total Revenue: ${analysis['total_revenue']:,.2f}")
    print(f"  Average Daily Revenue: ${analysis['average_daily_revenue']:,.2f}")
    print(f"  Max Revenue Day: Day {analysis['max_revenue_day']} (${analysis['max_revenue_value']:,.2f})")
    print(f"  Revenue Contribution by Day: {[f'{p:.1f}%' for p in analysis['revenue_contribution_pct']]}")

    export_revenue_csv(releases)
    export_schedule_csv(releases)


if __name__ == "__main__":
    main()
