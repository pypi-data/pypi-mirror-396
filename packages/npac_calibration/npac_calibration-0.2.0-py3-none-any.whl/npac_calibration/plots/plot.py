"""
This module provides functions for visualizing detector data, including scatter
plots, matrix plots, and histograms with Gaussian fits.
"""
from ..main.functions import gaussian
from ..main.gaussian_fit import fit_gaussian
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import pandas as pd
import numpy as np


def plot_all_extended_peaks(image, xs, ys, layer):
    """
    'all' mode plot: imshow + scatter only.
    """
    plt.figure()
    plt.imshow(image, origin="lower")
    plt.scatter(xs, ys, marker="x", s=20, c="white")

    title = f"{len(xs)} extended peak(s) in layer {layer}"

    plt.title(title)
    plt.xlabel("idx")
    plt.ylabel("idy")
    plt.colorbar().set_label("Energy")
    plt.show()


def plot_focus_extended_peak(sub, sigma_x, sigma_y, sigma_level=3, focus_size=20):
    """
    'focus' mode plot:
    - extract patch around (x_peak, y_peak)
    - set ellipse at patch center
    - draw 3σ ellipse
    """

    # patch center
    x0 = sub.shape[0] // 2
    y0 = sub.shape[1] // 2

    fig, ax = plt.subplots()

    im = ax.imshow(sub, origin="lower")

    ellipse = Ellipse(
        xy=(x0, y0),
        width=2 * sigma_level * sigma_x,
        height=2 * sigma_level * sigma_y,
        angle=0,
        fill=False,
        edgecolor="white",
        linewidth=1,
    )
    ax.add_patch(ellipse)

    ax.scatter(x0, y0, marker="x", c="black")

    title = f"{focus_size}x{focus_size} Zoom with {sigma_level}σ contour"
    ax.set_title(title)
    ax.set_xlabel("idx")
    ax.set_ylabel("idy")

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Energy")

    plt.show()


def scatter_plot(df: pd.DataFrame, layer: int) -> None:
    """
    Create a scatter plot of hit positions for a given detector layer,
    with energy represented as color.

    Args:
        df (pd.DataFrame): DataFrame containing the event data.
        layer (int): Detector layer to visualise (0–6).

    Returns:
        None
    """

    # Validate input layer
    if layer < 0 or layer > 6:
        raise ValueError("Layer must be between 0 and 6.")

    layer_df = df[df["layer"] == layer]

    plt.figure()
    plt.scatter(layer_df["idx"], layer_df["idy"], c=layer_df["E"], cmap="viridis", s=20)
    plt.colorbar(label="Energy")
    plt.xlabel("idx")
    plt.ylabel("idy")
    plt.show()


def plot_hist_with_fit(layer_pixels: np.ndarray, bins: int = 30) -> None:
    """
    Plot the histogram of layer pixels with fitted Gaussian.

    Args:
        layer_pixels (np.ndarray): An array of energy values for a layer.
        bins (int, optional): The number of bins for the histogram.
                              Defaults to 30.
    """
    amplitude_fit, sigma_fit, mu, bin_centers, hist = fit_gaussian(
        layer_pixels, bins=bins
    )

    plt.figure()
    plt.bar(
        bin_centers,
        hist,
        width=bin_centers[1] - bin_centers[0],
        alpha=0.6,
        label="Histogram",
    )
    plt.plot(
        bin_centers,
        gaussian(bin_centers, amplitude_fit, sigma_fit, mu),
        "r-",
        label=f"Fit: sigma={sigma_fit:.3f}",
    )
    plt.xlabel("Energy")
    plt.ylabel("Counts")
    plt.title("Layer noise fit")
    plt.legend()
    plt.show()
