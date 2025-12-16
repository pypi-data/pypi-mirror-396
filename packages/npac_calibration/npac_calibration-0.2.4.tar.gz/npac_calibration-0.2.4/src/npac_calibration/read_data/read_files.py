"""
This module provides functions for reading event data from CSV files.
"""

import pandas as pd
import os


def read_event_pd(events_path: str) -> pd.DataFrame:
    """


    Read event data from a CSV file using pandas.



    Args:


        events_path (str): Path to the CSV file.



    Returns:


        pd.DataFrame: DataFrame containing the event data.
    """

    events = pd.read_csv(events_path)
    return events


def get_event_path() -> str:
    """


    Build and return the full path to the default events CSV file.



    Returns:


        str: Absolute path to the events CSV file.
    """

    test_dir = os.path.dirname(os.path.abspath(__file__))

    repo_root = os.path.abspath(os.path.join(test_dir, "../../../"))

    return os.path.join(
        repo_root, "data", "electron_1GeV_Shower", "event000000047-hits_digitised.csv"
    )


def read_all_events() -> pd.DataFrame:
    """
    Read all events from the default CSV file.

    Returns:
        pd.DataFrame: DataFrame containing all event data.
    """
    events_path = get_event_path()
    return read_event_pd(events_path)
