"""
This module provides unit tests for the utility functions in utils.py.

It tests:
- df_to_matrix()
- extracted_image()
- convert_to_mm()
"""


import numpy as np
import pandas as pd

from npac_calibration.main.utils import df_to_matrix, extracted_image, convert_to_mm


def test_df_to_matrix():
    """
    Test the df_to_matrix() function.

    Ensures that:
    - the output has the expected shape from max(idx), max(idy),
    - energies are placed at the correct (y, x) positions,
    - energies at duplicate (idx, idy) positions are summed.
    """

    # assume a small synthetic layer with known coordinates
    layer_df = pd.DataFrame(
        {
            "idx": [0, 2, 2],
            "idy": [0, 1, 1],
            "E": [1.0, 3.0, 4.0],
        }
    )

    img = df_to_matrix(layer_df)

    # shape is (max(idy)+1, max(idx)+1) = (1+1, 2+1) = (2, 3)
    assert img.shape == (2, 3)

    # value at (idy=0, idx=0)
    assert img[0, 0] == 1.0

    # duplicate hits at (idy=1, idx=2) should sum: 3 + 4 = 7
    assert img[1, 2] == 7.0

    # a location not hit should remain zero
    assert img[0, 1] == 0.0


def test_extracted_image():
    """
    Test the extracted_image() function.

    Ensures that:
    - the returned patch has the requested shape,
    - extracting near the image border pads with zeros,
    - extracting at a central location preserves the corresponding region.
    """

    img = np.arange(25, dtype=float).reshape(5, 5)

    # assume a small patch size for easy checking
    patch = extracted_image(img, x0=0, y0=0, size=4)

    # always returns (size, size)
    assert patch.shape == (4, 4)

    # since we are at the corner, part of the patch should be zero-padded
    assert patch[0, 0] == 0.0

    # the bottom-right of the patch should include the original top-left values
    # original img[0,0] == 0, img[0,1] == 1, img[1,0] == 5, img[1,1] == 6
    assert patch[2, 2] == img[0, 0]
    assert patch[2, 3] == img[0, 1]
    assert patch[3, 2] == img[1, 0]
    assert patch[3, 3] == img[1, 1]


def test_convert_to_mm():
    """
    Test the convert_to_mm() function.

    Ensures that:
    - coordinates are converted using x_mm = x_px * pixel_size + min_position_mm,
    - sigmas are scaled by pixel_size,
    - the return type is a pair of tuples (coords_mm, sigma_mm).
    """

    # assume simple pixel coordinates and sigmas
    coords_px = (10.0, 20.0)
    sigma_px = (1.5, 2.0)

    coords_mm, sigma_mm = convert_to_mm(
        coords_pixels=coords_px,
        sigma_pixels=sigma_px,
        pixel_size=2,
        min_position_mm=-400,
    )

    assert isinstance(coords_mm, tuple)
    assert isinstance(sigma_mm, tuple)

    # coords: (10*2 - 400, 20*2 - 400) = (-380, -360)
    assert coords_mm == (-380.0, -360.0)

    # sigmas: (1.5*2, 2.0*2) = (3.0, 4.0)
    assert sigma_mm == (3.0, 4.0)
