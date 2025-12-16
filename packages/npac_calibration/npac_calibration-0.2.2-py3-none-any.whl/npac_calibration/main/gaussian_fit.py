"""
This module provides functions for fitting 1D and 2D Gaussian distributions to
data. It is used for analyzing detector energy distributions and spatial profiles
of particle bunches.
"""
from .functions import gaussian, gaussian_2d
from scipy.optimize import curve_fit
import numpy as np
from typing import Tuple


def fit_gaussian(
    layer_energies: np.ndarray, bins: int = 30
) -> Tuple[float, float, float, np.ndarray, np.ndarray]:
    """
    Fits a 1D Gaussian to the histogram of energy values for a given layer.

    Args:
        layer_energies (np.ndarray): An array of energy values.
        bins (int, optional): The number of bins for the histogram. Defaults to 30.

    Returns:
        tuple: A tuple containing the amplitude, sigma, mu, bin centers, and
               histogram values.
    """
    # Histogram
    hist, bin_edges = np.histogram(layer_energies, bins=bins)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Fixed mean at minimum energy
    mu = layer_energies.min()

    # Initial guess
    initial_guess = [hist.max(), np.std(layer_energies)]

    # Fit Gaussian: use the imported gaussian(amplitude, sigma, mu)
    popt, _ = curve_fit(
        lambda x, amplitude, sigma: gaussian(x, amplitude, sigma, mu),
        bin_centers,
        hist,
        p0=initial_guess,
    )

    amplitude_fit, sigma_fit = popt
    return float(amplitude_fit), float(sigma_fit), float(mu), bin_centers, hist


def fit_gaussian_2d(subimg: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fits a 2D Gaussian to a sub-image.

    Args:
        subimg (np.ndarray): A 2D numpy array representing the sub-image.

    Returns:
        tuple: A tuple containing the optimized parameters (popt) and the
               covariance matrix (pcov) from the fit.
    """
    nx, ny = subimg.shape

    # coordinates (local)
    x = np.arange(nx)
    y = np.arange(ny)
    X, Y = np.meshgrid(x, y)

    X = X.ravel()
    Y = Y.ravel()
    Z = subimg.ravel()

    # initial guess
    A0 = subimg.max()  # amplitude
    mu_x0 = nx / 2
    mu_y0 = ny / 2
    sigma_x0 = 2.0
    sigma_y0 = 2.0

    p0 = [A0, sigma_x0, mu_x0, sigma_y0, mu_y0]

    # wrap the model
    def model(coords, A, sx, mx, sy, my):
        xx, yy = coords
        return gaussian_2d(xx, yy, A, sx, mx, sy, my).ravel()

    popt, pcov = curve_fit(model, (X, Y), Z, p0=p0, maxfev=5000)

    return popt, pcov
