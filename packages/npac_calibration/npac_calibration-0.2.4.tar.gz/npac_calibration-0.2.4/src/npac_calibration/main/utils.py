"""
This module provides utility functions for data manipulation and conversion,
including transforming data into a matrix, extracting sub-images, and converting
pixel coordinates to millimeters.
"""
import numpy as np
import pandas as pd
from typing import Tuple


def df_to_matrix(layer_df: pd.DataFrame) -> np.ndarray:
    """
    Converts a DataFrame of layer data into a 2D numpy array (image).

    Args:
        layer_df (pd.DataFrame): DataFrame containing layer data with columns
                                 'idx', 'idy', and 'E'.

    Returns:
        np.ndarray: A 2D numpy array representing the detector image.
    """
    # determine the shape
    x_shape = layer_df["idx"].max() + 1
    y_shape = layer_df["idy"].max() + 1

    # create empty image (rows = y, columns = x)
    image = np.zeros((y_shape, x_shape))

    # fill the image correctly
    for x, y, E in zip(layer_df["idx"], layer_df["idy"], layer_df["E"]):
        image[y, x] += E

    return image


def extracted_image(image: np.ndarray, x0: int, y0: int, size: int = 20) -> np.ndarray:
    """
    Extracts a square sub-image (patch) from a larger image centered at (x0, y0).

    Args:
        image (np.ndarray): The input image.
        x0 (int): The x-coordinate of the center of the patch.
        y0 (int): The y-coordinate of the center of the patch.
        size (int): The size of the square patch to extract.

    Returns:
        np.ndarray: The extracted sub-image.
    """
    half = size // 2
    out = np.zeros((size, size))  # 20×20

    # compute the region inside the image
    x_min_img = max(0, x0 - half)
    x_max_img = min(image.shape[0], x0 + half)
    y_min_img = max(0, y0 - half)
    y_max_img = min(image.shape[1], y0 + half)

    # compute the corresponding region inside the output 20×20
    x_min_out = x_min_img - (x0 - half)
    x_max_out = x_max_img - (x0 - half)
    y_min_out = y_min_img - (y0 - half)
    y_max_out = y_max_img - (y0 - half)

    # copy the valid part
    out[x_min_out:x_max_out, y_min_out:y_max_out] = image[
        x_min_img:x_max_img, y_min_img:y_max_img
    ]

    return out


def convert_to_mm(
    coords_pixels: Tuple[float, float],
    sigma_pixels: Tuple[float, float],
    pixel_size: int = 2,
    min_position_mm: int = -400,
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    Convert pixel coordinates and sigmas to millimeter units.

    Args:
        coords_pixels (tuple): (x, y) coordinates in pixels.
        sigma_pixels (tuple): (sigma_x, sigma_y) in pixels.
        pixel_size (int, optional): Size of a pixel in mm. Defaults to 2.
        min_position_mm (int, optional): The minimum position in mm, corresponding
                                         to the origin of the pixel grid.
                                         Defaults to -400.

    Returns:
        tuple: A tuple containing (coords_mm, sigma_mm) in millimeters.
    """
    x_px, y_px = coords_pixels
    sigma_x_px, sigma_y_px = sigma_pixels

    coords_mm = (
        x_px * pixel_size + min_position_mm,
        y_px * pixel_size + min_position_mm,
    )
    sigma_mm = (sigma_x_px * pixel_size, sigma_y_px * pixel_size)

    return coords_mm, sigma_mm
