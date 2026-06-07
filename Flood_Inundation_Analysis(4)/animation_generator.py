import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def create_flood_animation(
    dem: np.ndarray,
    min_level: float = 40.0,
    max_level: float = 50.0,
    step: float = 1.0,
    interval: int = 500,
    save_path: Optional[str] = None
) -> Optional[str]:
    """Create animation of rising flood levels.

    Uses imageio to assemble frames showing flood extent, water level,
    flood percentage, and volume at each frame.

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array.
    min_level : float
        Starting water level.
    max_level : float
        Ending water level.
    step : float
        Water level increment.
    interval : int
        Frame delay in ms (for matplotlib animation).
    save_path : str, optional
        Path to save the GIF. Default: outputs/rising_flood.gif.

    Returns
    -------
    str or None
        Path to saved GIF if successful.
    """
    from flood_inundation import calculate_flood
    from volume_analysis import calculate_flood_volume

    if save_path is None:
        save_path = str(OUTPUT_DIR / "rising_flood.gif")

    levels = np.arange(min_level, max_level + step, step)
    fig, ax = plt.subplots(figsize=(8, 6))

    def update(frame_idx: int) -> list:
        wl = levels[frame_idx]
        result = calculate_flood(dem, wl)
        vol = calculate_flood_volume(dem, result["depth_array"])

        ax.clear()
        ax.imshow(dem, cmap="gray", aspect="auto")
        ax.imshow(np.ma.masked_where(~result["flooded_mask"], result["flooded_mask"]),
                  cmap="Blues", alpha=0.6, aspect="auto")

        stats = (
            f"Water Level: {wl:.1f} m\n"
            f"Flooded: {result['flooded_percentage']:.2f}%\n"
            f"Max Depth: {result['maximum_depth']:.2f} m\n"
            f"Volume: {vol['total_volume_m3'] / 1e6:.2f} M m³"
        )
        ax.text(0.02, 0.98, stats, transform=ax.transAxes,
                fontsize=11, verticalalignment="top",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.9))
        ax.set_title(f"Rising Flood Simulation — Level {wl:.1f} m")
        ax.set_xlabel("Column")
        ax.set_ylabel("Row")
        return [ax]

    anim = FuncAnimation(fig, update, frames=len(levels), interval=interval, repeat=True)
    anim.save(save_path, writer="pillow", dpi=100)
    plt.close(fig)
    logger.info("Saved flood animation (%d frames): %s", len(levels), save_path)
    return save_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    from flood_inundation import load_dem
    dem = load_dem()
    create_flood_animation(dem, 40, 50, 1.0)
