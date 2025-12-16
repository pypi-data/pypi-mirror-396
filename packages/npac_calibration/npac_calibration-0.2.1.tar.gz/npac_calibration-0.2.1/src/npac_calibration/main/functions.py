"""
This module contains mathematical functions used in the calibration process,
including 1D and 2D Gaussian functions and a threshold calculation function.
"""
import numpy as np


def gaussian(x: np.ndarray, amplitude: float, sigma: float, mu: float) -> np.ndarray:
    """
    Calculates the value of a 1D Gaussian function.

    Args:
        x (np.ndarray): The input values.
        amplitude (float): The amplitude of the Gaussian.
        sigma (float): The standard deviation of the Gaussian.
        mu (float): The mean of the Gaussian.

    Returns:
        np.ndarray: The calculated Gaussian values.
    """
    return amplitude * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def gaussian_2d(
    x: np.ndarray,
    y: np.ndarray,
    amplitude: float,
    sigma_x: float,
    mu_x: float,
    sigma_y: float,
    mu_y: float,
) -> np.ndarray:
    """
    Calculates the value of a 2D Gaussian function.

    Args:
        x (np.ndarray): The x-coordinates.
        y (np.ndarray): The y-coordinates.
        amplitude (float): The amplitude of the Gaussian.
        sigma_x (float): The standard deviation in the x-direction.
        mu_x (float): The mean in the x-direction.
        sigma_y (float): The standard deviation in the y-direction.
        mu_y (float): The mean in the y-direction.

    Returns:
        np.ndarray: The calculated 2D Gaussian values.
    """
    G = amplitude * gaussian(x, 1.0, sigma_x, mu_x) * gaussian(y, 1.0, sigma_y, mu_y)
    return G


def threshold(mu: float, sigma: float, n: int = 3) -> float:
    """
    Calculates a threshold value based on the mean and standard deviation.

    Args:
        mu (float): The mean value.
        sigma (float): The standard deviation.
        n (int, optional): The number of standard deviations to add to the mean.
                           Defaults to 3.

    Returns:
        float: The calculated threshold value.
    """
    return mu + n * sigma
