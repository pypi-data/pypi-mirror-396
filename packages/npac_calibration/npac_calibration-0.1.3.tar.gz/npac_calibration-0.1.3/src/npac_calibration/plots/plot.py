"""
This module provides functions for visualizing detector data, including scatter
plots, matrix plots, and histograms with Gaussian fits.
"""
from ..main.functions import gaussian
from ..main.gaussian_fit import fit_gaussian
import matplotlib.pyplot as plt
from npac_calibration.main.utils import df_to_matrix
import pandas as pd
import numpy as np


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


def matrix_plot(df: pd.DataFrame, layer: int) -> None:
    """
    Plot the energy as a 2D image for a given detector layer from a DataFrame
    with columns ['idx', 'idy', 'E'].

    Args:
        df (pd.DataFrame): DataFrame containing the event data.
        layer (int): Detector layer to visualise (0–6).

    Returns:
        None
    """

    # Validate input layer
    if layer < 0 or layer > 6:
        raise ValueError("Layer must be an integer between 0 and 6.")

    layer_df = df[df["layer"] == layer]

    image = df_to_matrix(layer_df)

    # plot
    plt.figure()
    plt.imshow(image, origin="lower", cmap="coolwarm", aspect="auto")
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
