"""
Sensitivity Analysis Module for SCS-CN Runoff Model

Analyzes how runoff responds to changes in Curve Number (CN) and
rainfall depth. Generates publication-quality visualizations for
hydrological interpretation.

Generated Plots:
    - sensitivity_curve.png: CN vs Runoff at fixed P = 50 mm
    - runoff_comparison.png: Rainfall vs Runoff for multiple CN values
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scscn_runoff import calculate_runoff, calculate_runoff_series, runoff_analytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

plt.style.use("seaborn-v0_8-darkgrid")
plt.rcParams.update(
    {
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "legend.fontsize": 10,
        "figure.figsize": (10, 6),
    }
)


def sensitivity_cn_vs_runoff(
    P: float = 50.0,
    cn_values: Optional[list[float]] = None,
    save_path: Optional[str] = "outputs/sensitivity_curve.png",
    show: bool = False,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot runoff (Q) vs Curve Number (CN) for a fixed rainfall depth.

    Parameters
    ----------
    P : float, optional
        Fixed rainfall depth in mm, by default 50.0.
    cn_values : list[float], optional
        Sequence of CN values to evaluate. Defaults to
        [60, 70, 80, 90, 95, 100].
    save_path : str, optional
        Path to save the figure. None to skip saving.
    show : bool, optional
        If True, display the plot window.

    Returns
    -------
    tuple[Figure, Axes]
        Matplotlib figure and axes objects.
    """
    if cn_values is None:
        cn_values = [60, 70, 80, 90, 95, 100]

    runoff_values = []
    results = []

    for CN in cn_values:
        result = calculate_runoff(P, CN)
        runoff_values.append(result["runoff"])
        results.append(result)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(cn_values, runoff_values, "o-", color="#1f77b4", linewidth=2.5, markersize=8)

    for CN, Q, r in zip(cn_values, runoff_values, results):
        label = f"CN={CN:.0f}, S={r['retention']:.1f}mm\nIa={r['initial_abstraction']:.1f}mm, Q={Q:.2f}mm"
        ax.annotate(
            label,
            (CN, Q),
            textcoords="offset points",
            xytext=(0, 15 if Q < max(runoff_values) * 0.8 else -20),
            ha="center",
            fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="gray", alpha=0.8),
        )

    ax.set_xlabel("Curve Number (CN)")
    ax.set_ylabel("Runoff Q (mm)")
    ax.set_title(f"SCS-CN Sensitivity: Runoff vs Curve Number (P = {P} mm)")
    ax.set_xlim(min(cn_values) - 2, max(cn_values) + 2)
    ax.set_ylim(0, max(runoff_values) * 1.15)
    ax.grid(True, alpha=0.3)

    for Q_val in runoff_values:
        ax.axhline(y=Q_val, color="gray", linestyle="--", alpha=0.15)

    annotation_text = (
        f"Fixed Rainfall: P = {P} mm\n"
        f"Linear increase in CN produces\n"
        f"non-linear increase in runoff"
    )
    ax.text(
        0.02,
        0.98,
        annotation_text,
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    fig.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path)
        logger.info(f"Sensitivity curve saved to {save_path}")

    if show:
        plt.show()

    return fig, ax


def rainfall_vs_runoff_comparison(
    rainfall_max: float = 150.0,
    cn_values: Optional[list[float]] = None,
    save_path: Optional[str] = "outputs/runoff_comparison.png",
    show: bool = False,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot Rainfall vs Runoff for multiple Curve Numbers.

    Generates a comparison plot showing how different land cover types
    (represented by CN) respond to increasing rainfall.

    Parameters
    ----------
    rainfall_max : float, optional
        Maximum rainfall depth in mm, by default 150.0.
    cn_values : list[float], optional
        List of CN values to compare. Defaults to [60, 80, 95].
    save_path : str, optional
        Path to save the figure. None to skip saving.
    show : bool, optional
        If True, display the plot window.

    Returns
    -------
    tuple[Figure, Axes]
        Matplotlib figure and axes objects.
    """
    if cn_values is None:
        cn_values = [60, 80, 95]

    rainfall_values = np.linspace(0, rainfall_max, 200)

    colors = {60: "#2ca02c", 80: "#ff7f0e", 95: "#d62728"}
    labels = {60: "Woods (Good) - CN=60", 80: "Pasture - CN=80", 95: "Urban - CN=95"}
    line_styles = {60: "-", 80: "--", 95: ":"}

    fig, ax = plt.subplots(figsize=(10, 6))

    for CN in cn_values:
        runoff_vals = []
        for P in rainfall_values:
            result = calculate_runoff(P, CN)
            runoff_vals.append(result["runoff"])

        ax.plot(
            rainfall_values,
            runoff_vals,
            label=labels[CN],
            color=colors[CN],
            linestyle=line_styles[CN],
            linewidth=2.5,
        )

    ax.plot(
        rainfall_values,
        rainfall_values,
        "k-",
        alpha=0.3,
        linewidth=1,
        label="Q = P (Impervious)",
    )

    ax.set_xlabel("Rainfall P (mm)")
    ax.set_ylabel("Runoff Q (mm)")
    ax.set_title("SCS-CN: Rainfall vs Runoff for Different Curve Numbers")
    ax.legend(loc="lower right")
    ax.set_xlim(0, rainfall_max)
    ax.set_ylim(0, rainfall_max)
    ax.grid(True, alpha=0.3)

    ax.fill_between(rainfall_values, rainfall_values, alpha=0.05, color="blue")
    ax.text(
        0.95,
        0.05,
        "Q <= P (always satisfied)",
        transform=ax.transAxes,
        fontsize=9,
        ha="right",
        style="italic",
        alpha=0.6,
    )

    fig.tight_layout()

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path)
        logger.info(f"Runoff comparison plot saved to {save_path}")

    if show:
        plt.show()

    return fig, ax


def generate_analytics_report(
    rainfall_values: Optional[list[float]] = None,
    cn_values: Optional[list[float]] = None,
    save_path: Optional[str] = "outputs/analysis_report.csv",
) -> pd.DataFrame:
    """Generate and save a comprehensive analytics report as CSV.

    Parameters
    ----------
    rainfall_values : list[float], optional
        Rainfall depths in mm. Defaults to [10, 20, 30, 40, 50, 75, 100].
    cn_values : list[float], optional
        Curve numbers. Defaults to [60, 70, 80, 90, 100].
    save_path : str, optional
        Path to save the CSV file. None to skip saving.

    Returns
    -------
    pd.DataFrame
        Analytics report DataFrame.
    """
    if rainfall_values is None:
        rainfall_values = [10, 20, 30, 40, 50, 75, 100]
    if cn_values is None:
        cn_values = [60, 70, 80, 90, 100]

    df = calculate_runoff_series(rainfall_values, cn_values)

    stats = runoff_analytics(df)

    if save_path:
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(save_path, index=False)
        logger.info(f"Analysis report saved to {save_path}")

    logger.info("Analytics summary:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value:.4f}")

    return df


def run_full_sensitivity_analysis(
    output_dir: str = "outputs",
) -> dict[str, str]:
    """Run the complete sensitivity analysis pipeline.

    Parameters
    ----------
    output_dir : str, optional
        Directory to save outputs, by default "outputs".

    Returns
    -------
    dict[str, str]
        Paths to generated files.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    logger.info("Running SCS-CN Sensitivity Analysis")
    logger.info("=" * 50)

    fig1, _ = sensitivity_cn_vs_runoff(
        P=50.0,
        cn_values=[60, 70, 80, 90, 95, 100],
        save_path=f"{output_dir}/sensitivity_curve.png",
    )
    plt.close(fig1)

    fig2, _ = rainfall_vs_runoff_comparison(
        rainfall_max=150.0,
        cn_values=[60, 80, 95],
        save_path=f"{output_dir}/runoff_comparison.png",
    )
    plt.close(fig2)

    df = generate_analytics_report(save_path=f"{output_dir}/analysis_report.csv")

    generated = {
        "sensitivity_curve": f"{output_dir}/sensitivity_curve.png",
        "runoff_comparison": f"{output_dir}/runoff_comparison.png",
        "analysis_report": f"{output_dir}/analysis_report.csv",
    }

    logger.info("Sensitivity analysis complete. Generated files:")
    for name, path in generated.items():
        logger.info(f"  {name}: {path}")

    return generated


if __name__ == "__main__":
    run_full_sensitivity_analysis()
