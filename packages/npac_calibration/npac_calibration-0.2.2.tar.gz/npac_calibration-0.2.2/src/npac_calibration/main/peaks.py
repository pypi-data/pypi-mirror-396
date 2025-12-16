"""
This module provides functions for peak finding and luminosity calculation in
detector images. It includes methods to identify peaks and bunches (extended peaks)
and to compute the integrated luminosity around a given peak.
"""
import numpy as np
from typing import Tuple, List


def adjust_neighbor(x: int, xmin: int, xmax: int) -> Tuple[int, int]:
    """
    Adjusts the neighborhood range for edge cases in an image.

    Args:
        x (int): The coordinate of the pixel.
        xmin (int): The minimum possible coordinate value.
        xmax (int): The maximum possible coordinate value.

    Returns:
        tuple: A tuple (a, b) with adjustment values for the neighborhood slice.
    """
    a = 0
    b = 0
    if x == xmin:
        a = 1
    if x == xmax:
        b = -1
    return a, b


def find_peaks_and_bunches(
    image: np.ndarray, t: float, n: int = 3
) -> Tuple[List[int], List[int], List[int], List[int]]:
    """
    Locates peaks and extended peaks (bunches) in a square image.

    A peak is a pixel with a value greater than the threshold `t` and also
    greater than or equal to all its neighbors. A bunch is a peak that has at
    least `n` non-zero neighbors.

    Args:
        image (np.ndarray): The input square image.
        t (float): The threshold value for peak candidates.
        n (int, optional): The minimum number of non-zero neighbors to classify
                           a peak as a bunch. Defaults to 3.

    Returns:
        tuple: A tuple containing four lists of integers:
               - x_peak: x-coordinates of the peaks.
               - y_peak: y-coordinates of the peaks.
               - x_bunch: x-coordinates of the bunches.
               - y_bunch: y-coordinates of the bunches.
    """
    x_peak = []
    y_peak = []
    x_bunch = []
    y_bunch = []

    x_candidate, y_candidate = np.where(image > t)
    # loop over candidates
    for x, y in zip(x_candidate, y_candidate):
        if n < 6:
            ax, bx = adjust_neighbor(x, 0, image.shape[0] - 1)
            ay, by = adjust_neighbor(y, 0, image.shape[0] - 1)
        else:
            ax = bx = ay = by = 0

        # extract 3x3 neighborhood
        neighborhood = image[x - 1 + ax : x + 2 + bx, y - 1 + ay : y + 2 + by]

        n_neighbors = np.delete(neighborhood.flatten(), 4)

        # check if center pixel is the max
        if image[x, y] >= neighborhood.max():
            x_peak.append(x)
            y_peak.append(y)
            # if at least n of the 8 neighbors different from 0, extended
            if np.count_nonzero(n_neighbors) >= n:
                x_bunch.append(x)
                y_bunch.append(y)

    return x_peak, y_peak, x_bunch, y_bunch


def integrated_luminosity_for_peak(image: np.ndarray, x: int, y: int) -> float:
    """
    Computes the integrated luminosity around a peak at coordinates (x, y).

    This function iteratively expands a square region centered on the peak until
    the outermost ring of the region contains only zeros. The integrated
    luminosity is the sum of all pixel values within that final region.

    If the expansion reaches the image boundary and the border is still not all
    zeros, the luminosity is the sum of the entire image.

    Args:
        image (np.ndarray): A 2D array of energies.
        x (int): The row index of the peak.
        y (int): The column index of the peak.

    Returns:
        float: The integrated luminosity around the specified peak.
    """
    nrows, ncols = image.shape
    max_row = nrows - 1
    max_col = ncols - 1

    r = 0  # radius (in pixels) around peak

    while True:
        # Compute bounds of current square, clipped to image borders
        x0 = max(0, x - r)
        x1 = min(max_row, x + r)
        y0 = max(0, y - r)
        y1 = min(max_col, y + r)

        # +1 on the upper bound because Python slicing is exclusive at the end
        sub = image[x0 : x1 + 1, y0 : y1 + 1]

        # Extract border ("outer ring") of sub-image
        top = sub[0, :]
        bottom = sub[-1, :]
        if sub.shape[0] > 2 and sub.shape[1] > 1:
            left = sub[1:-1, 0]
            right = sub[1:-1, -1]
            ring = np.concatenate([top, bottom, left, right])
        else:
            # For very small sub-images, top and bottom cover all border pixels
            ring = np.concatenate([top, bottom])

        # If every pixel in the outermost ring is zero -> stop
        if np.all(ring == 0):
            return float(sub.sum())

        # If we've reached the whole image, we can't expand further
        if x0 == 0 and x1 == max_row and y0 == 0 and y1 == max_col:
            return float(sub.sum())

        # Otherwise increase radius and try again
        r += 1
