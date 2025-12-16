import os
import pandas as pd

from npac_calibration.read_data.read_files import read_event_pd


def test_read_events_pd():
    """

    Test the read_events_pd() function.


    Ensures that the event CSV file is correctly read into a pandas DataFrame

    with the expected structure.
    """

    # Get the directory of this test file

    test_dir = os.path.dirname(os.path.abspath(__file__))

    # Go up two levels to reach the repo root

    repo_root = os.path.abspath(os.path.join(test_dir, "../"))

    # Build full path to the CSV

    events_path = os.path.join(
        repo_root, "data", "electron_1GeV_Shower", "event000000047-hits_digitised.csv"
    )

    # Read events

    events = read_event_pd(events_path)

    # Check that the result is a DataFrame

    assert isinstance(events, pd.DataFrame)

    # Make sure there is at least 1 row (= 1 hit)

    assert len(events) > 0

    # Make sure there are 5 columns

    assert len(events.columns) == 5

    # Check that the expected column names exist

    expected_cols = {"idx", "idy", "layer", "id", "E"}

    assert expected_cols.issubset(events.columns)
