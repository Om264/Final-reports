import numpy as np
import matplotlib.pyplot as plt


def plot_flood_map(elevation, water_level, flooded, depth, save_path=None):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    im0 = axes[0].imshow(elevation, cmap="terrain")
    axes[0].set_title("Digital Elevation Model")
    plt.colorbar(im0, ax=axes[0])
    im1 = axes[1].imshow(flooded, cmap="Blues", vmin=0, vmax=1)
    axes[1].set_title(f"Flood Extent (Water Level = {water_level}m)")
    plt.colorbar(im1, ax=axes[1])
    depth_masked = np.ma.masked_where(~flooded, depth)
    im2 = axes[2].imshow(depth_masked, cmap="Blues")
    axes[2].set_title("Inundation Depth")
    plt.colorbar(im2, ax=axes[2])
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=150)
    plt.show()
