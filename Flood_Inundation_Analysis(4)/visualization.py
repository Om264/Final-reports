import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def visualize_dem(
    dem: np.ndarray,
    title: str = "Digital Elevation Model",
    save_path: Optional[str] = None
) -> plt.Figure:
    """Display DEM as grayscale image with elevation colorbar.

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array.
    title : str
        Plot title.
    save_path : str, optional
        Path to save figure.

    Returns
    -------
    plt.Figure
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(dem, cmap="gray", aspect="auto")
    cbar = plt.colorbar(im, ax=ax, label="Elevation (m)")
    ax.set_title(title)
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
        logger.info("Saved DEM visualization: %s", save_path)
    return fig


def visualize_flood(
    dem: np.ndarray,
    flooded_mask: np.ndarray,
    depth_array: np.ndarray,
    water_level: float,
    save_path: Optional[str] = None,
    title_suffix: str = ""
) -> plt.Figure:
    """Create flood extent and depth visualisation.

    Generates a 2-panel figure:
      Left: Flood extent (blue overlay on DEM)
      Right: Inundation depth heatmap

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array.
    flooded_mask : np.ndarray
        Boolean flood mask.
    depth_array : np.ndarray
        Inundation depth per cell.
    water_level : float
        Water level used for flooding.
    save_path : str, optional
        Path to save figure.
    title_suffix : str
        Additional text for title.

    Returns
    -------
    plt.Figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    ax = axes[0]
    ax.imshow(dem, cmap="gray", aspect="auto")
    ax.imshow(np.ma.masked_where(~flooded_mask, flooded_mask),
              cmap="Blues", alpha=0.6, aspect="auto")
    ax.set_title(f"Flood Extent at {water_level:.0f}m{title_suffix}")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")

    ax = axes[1]
    depth_masked = np.ma.masked_where(depth_array == 0, depth_array)
    im = ax.imshow(depth_masked, cmap="Blues", aspect="auto")
    cbar = plt.colorbar(im, ax=ax, label="Depth (m)")
    ax.set_title(f"Inundation Depth at {water_level:.0f}m{title_suffix}")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")

    # Annotate statistics
    flooded_pct = 100.0 * np.sum(flooded_mask) / flooded_mask.size
    max_depth = float(depth_array.max())
    avg_depth = float(depth_array[depth_array > 0].mean()) if np.any(depth_array > 0) else 0.0
    stats_text = (
        f"Flooded: {flooded_pct:.1f}%\n"
        f"Max Depth: {max_depth:.2f} m\n"
        f"Avg Depth: {avg_depth:.2f} m"
    )
    axes[0].text(
        0.02, 0.98, stats_text, transform=axes[0].transAxes,
        fontsize=10, verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8)
    )

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
        logger.info("Saved flood visualization: %s", save_path)
    plt.close(fig)
    return fig


def visualize_comparison(
    dem: np.ndarray,
    water_levels: list,
    save_path: Optional[str] = None
) -> plt.Figure:
    """Create side-by-side comparison of flood extent at different water levels.

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array.
    water_levels : list
        Water levels to compare.
    save_path : str, optional
        Path to save figure.

    Returns
    -------
    plt.Figure
    """
    from flood_inundation import calculate_flood

    n = len(water_levels)
    fig, axes = plt.subplots(2, n, figsize=(5 * n, 10))

    for i, wl in enumerate(water_levels):
        result = calculate_flood(dem, wl)

        ax = axes[0, i]
        ax.imshow(dem, cmap="gray", aspect="auto")
        ax.imshow(np.ma.masked_where(~result["flooded_mask"], result["flooded_mask"]),
                  cmap="Blues", alpha=0.6, aspect="auto")
        ax.set_title(f"Water Level: {wl:.0f} m")
        ax.set_xlabel("Column")
        ax.set_ylabel("Row")

        ax = axes[1, i]
        depth_masked = np.ma.masked_where(result["depth_array"] == 0, result["depth_array"])
        im = ax.imshow(depth_masked, cmap="Blues", aspect="auto")
        plt.colorbar(im, ax=ax, label="Depth (m)")
        ax.set_title(f"Depth at {wl:.0f} m")
        ax.set_xlabel("Column")
        ax.set_ylabel("Row")

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
        logger.info("Saved comparison visualization: %s", save_path)
    plt.close(fig)
    return fig


def visualize_flood_curve(
    levels: list,
    percentages: list,
    save_path: Optional[str] = None
) -> plt.Figure:
    """Plot water level vs flooded percentage curve.

    Parameters
    ----------
    levels : list
        Water levels.
    percentages : list
        Flooded area percentages.
    save_path : str, optional
        Path to save figure.

    Returns
    -------
    plt.Figure
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(levels, percentages, "b-o", linewidth=2, markersize=6)
    ax.set_xlabel("Water Level (m)")
    ax.set_ylabel("Flooded Area (%)")
    ax.set_title("Flood Curve: Water Level vs Flooded Percentage")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(min(levels), max(levels))

    for x, y in zip(levels, percentages):
        ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=9)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
        logger.info("Saved flood curve: %s", save_path)
    plt.close(fig)
    return fig


def visualize_volume_curve(
    levels: list,
    volumes: list,
    save_path: Optional[str] = None
) -> plt.Figure:
    """Plot water level vs flood volume curve.

    Parameters
    ----------
    levels : list
        Water levels.
    volumes : list
        Flood volumes in m^3.
    save_path : str, optional
        Path to save figure.

    Returns
    -------
    plt.Figure
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(levels, volumes, "b-o", linewidth=2, markersize=6)
    ax.set_xlabel("Water Level (m)")
    ax.set_ylabel("Flood Volume (m³)")
    ax.set_title("Flood Volume Curve: Water Level vs Flood Volume")
    ax.grid(True, alpha=0.3)

    volume_labels = [f"{v / 1e6:.1f}M" for v in volumes]
    for x, y, label in zip(levels, volumes, volume_labels):
        ax.annotate(label, (x, y), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=9)

    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
        logger.info("Saved volume curve: %s", save_path)
    plt.close(fig)
    return fig


def visualize_building_impact(
    dem: np.ndarray,
    building_mask: np.ndarray,
    result: dict,
    water_level: float,
    save_path: Optional[str] = None
) -> plt.Figure:
    """Visualize building impact on flood extent.

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array.
    building_mask : np.ndarray
        Boolean building footprint mask.
    result : dict
        Output from calculate_flood_with_buildings.
    water_level : float
        Water level used for flooding.
    save_path : str, optional
        Path to save figure.

    Returns
    -------
    plt.Figure
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    ax = axes[0]
    ax.imshow(dem, cmap="gray", aspect="auto")
    ax.imshow(np.ma.masked_where(~building_mask, building_mask),
              cmap="Reds", alpha=0.7, aspect="auto")
    ax.set_title("Building Footprints")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")

    ax = axes[1]
    ax.imshow(dem, cmap="gray", aspect="auto")
    ax.imshow(np.ma.masked_where(~result["flooded_mask_without_buildings"],
                                 result["flooded_mask_without_buildings"]),
              cmap="Blues", alpha=0.5, aspect="auto")
    ax.set_title(f"Flood Without Buildings\n({result['flooded_cells_without_buildings']} cells)")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")

    ax = axes[2]
    ax.imshow(dem, cmap="gray", aspect="auto")
    ax.imshow(np.ma.masked_where(~result["flooded_mask_with_buildings"],
                                 result["flooded_mask_with_buildings"]),
              cmap="Blues", alpha=0.5, aspect="auto")
    ax.imshow(np.ma.masked_where(~building_mask, building_mask),
              cmap="Reds", alpha=0.7, aspect="auto")
    ax.set_title(f"Flood With Buildings\n({result['flooded_cells_with_buildings']} cells)")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")

    fig.suptitle(f"Building Impact on Flood Extent at {water_level:.0f}m | "
                 f"Reduction: {result['reduction_percentage']:.1f}%", fontsize=14)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
        logger.info("Saved building impact visualization: %s", save_path)
    plt.close(fig)
    return fig


def visualize_routing(
    dem: np.ndarray,
    routing_result: dict,
    water_level: float,
    connectivity: str,
    save_path: Optional[str] = None
) -> plt.Figure:
    """Visualize flood routing results.

    Parameters
    ----------
    dem : np.ndarray
        2D elevation array.
    routing_result : dict
        Output from simulate_flood_routing.
    water_level : float
        Water level used.
    connectivity : str
        Connectivity used for routing.
    save_path : str, optional
        Path to save figure.

    Returns
    -------
    plt.Figure
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    ax = axes[0]
    ax.imshow(dem, cmap="gray", aspect="auto")
    ax.imshow(np.ma.masked_where(~routing_result["flood_extent"],
                                 routing_result["flood_extent"]),
              cmap="Blues", alpha=0.6, aspect="auto")
    flooded_pct = 100.0 * np.sum(routing_result["flood_extent"]) / dem.size
    ax.set_title(f"Flood Extent ({connectivity}-conn)\n{flooded_pct:.1f}% flooded")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")

    ax = axes[1]
    depth_masked = np.ma.masked_where(routing_result["depth_map"] == 0,
                                      routing_result["depth_map"])
    im = ax.imshow(depth_masked, cmap="Blues", aspect="auto")
    plt.colorbar(im, ax=ax, label="Depth (m)")
    ax.set_title("Inundation Depth")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")

    ax = axes[2]
    arrival = routing_result["arrival_time"]
    arrival_masked = np.ma.masked_where(arrival < 0, arrival)
    im = ax.imshow(arrival_masked, cmap="viridis", aspect="auto")
    plt.colorbar(im, ax=ax, label="Arrival Time (steps)")
    ax.set_title("Flood Arrival Time")
    ax.set_xlabel("Column")
    ax.set_ylabel("Row")

    fig.suptitle(f"Flood Routing at {water_level:.0f}m ({connectivity}-connectivity)",
                 fontsize=14)
    plt.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
        logger.info("Saved routing visualization: %s", save_path)
    plt.close(fig)
    return fig
