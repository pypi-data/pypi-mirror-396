"""
This module provides unit tests for the peak finding and luminosity utilities.

It tests:
- adjust_neighbor()
- find_peaks_and_bunches()
- integrated_luminosity_for_peak()
"""


import numpy as np

from npac_calibration.main.peaks import (
    adjust_neighbor,
    find_peaks_and_bunches,
    integrated_luminosity_for_peak,
)


def test_adjust_neighbor():
    """
    Test the adjust_neighbor() function.

    Ensures that:
    - the left edge pixel gets the correct positive shift,
    - the right edge pixel gets the correct negative shift,
    - a middle pixel gets no adjustment.
    """

    # assume xmax = 9 for this test

    # left edge, the function shifts the neighborhood inward
    assert adjust_neighbor(0, 0, 9) == (1, 0)  # = (a, b)

    # right edge, the function shifts the neighborhood inward
    assert adjust_neighbor(9, 0, 9) == (0, -1)

    # middle, no shift is needed for the neighborhood
    assert adjust_neighbor(5, 0, 9) == (0, 0)


def test_find_peaks_and_bunches():
    """
    Test the find_peaks_and_bunches() function.

    Ensures that:
    - the function returns the expected tuple structure,
    - a clear peak above threshold is detected,
    - a peak with at least n non-zero neighbors is classified as a bunch.
    """

    # assume a small 5x5 image for simplicity
    img = np.zeros((5, 5), dtype=float)

    # Make a clear peak at center
    img[2, 2] = 10.0

    # Make 3 non-zero neighbors => should count as bunch for n=3
    img[2, 1] = 1.0
    img[2, 3] = 1.0
    img[1, 2] = 1.0

    x_peak, y_peak, x_bunch, y_bunch = find_peaks_and_bunches(img, t=1.0, n=3)

    # Structure checks
    assert isinstance((x_peak, y_peak, x_bunch, y_bunch), tuple)
    assert all(isinstance(lst, list) for lst in [x_peak, y_peak, x_bunch, y_bunch])
    assert len(x_peak) == len(y_peak)
    assert len(x_bunch) == len(y_bunch)

    # Content checks: peak exists and is also a bunch
    assert (2, 2) in list(zip(x_peak, y_peak))
    assert (2, 2) in list(zip(x_bunch, y_bunch))


def test_integrated_luminosity_for_peak_expansion_behavior():
    """
    Test the integrated_luminosity_for_peak() function.

    Ensures that:
    - the result is a float,
    - the luminosity is at least the peak energy,
    - the returned luminosity is consistent with expanding regions
      (i.e. it should be greater or equal than the sum of smaller regions).
    """

    # assume a small 7x7 image for simplicity
    img = np.zeros((7, 7), dtype=float)

    # Center peak
    img[3, 3] = 10.0

    # Put energy on ring r=1 so the algorithm must expand at least to r=2
    img[2, 3] = 1.0
    img[3, 2] = 1.0
    img[3, 4] = 1.0

    # Put some energy on ring r=2 as well, so it must expand beyond r=1
    img[1, 3] = 2.0

    L = integrated_luminosity_for_peak(img, 3, 3)

    # Basic tests
    assert isinstance(L, float)
    assert L >= 10.0  # at least includes the peak

    # Expansion consistency checks
    assert L >= float(img[3, 3])  # r=0 region (just the peak)

    sub_r1 = img[2:5, 2:5]  # r=1 region (3x3)
    assert L >= float(sub_r1.sum())
