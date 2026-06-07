import csv
from pathlib import Path
from typing import Any
import numpy as np


def save_schedule(schedule: dict[str, Any], path: str | Path = "outputs/schedule.csv") -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(schedule.keys())
        for row in zip(*schedule.values()):
            writer.writerow(row)


def load_inflows(path: str | Path) -> np.ndarray:
    return np.loadtxt(Path(path), delimiter=",", skiprows=1)
