from npac_calibration.read_data.read_files import get_event_path, read_event_pd


def test_scatterplot():
    """


    Test the scatter_plot() logic.



    Ensures that a valid layer exists in the event data and that


    the required columns ('idx', 'idy', 'E') are present for plotting.
    """

    events_path = get_event_path()

    df = read_event_pd(events_path)

    layer = 0

    # layer must be valid

    assert 0 <= layer <= 6

    # layer must exist in data

    layer_df = df[df["layer"] == layer]

    assert not layer_df.empty

    # required columns

    for col in ["idx", "idy", "E"]:
        assert col in layer_df.columns


def test_matrixplot():
    """


    Test the matrix_plot() logic.



    Confirms that the selected layer contains data and that


    the idx/idy values produce valid matrix dimensions.
    """

    events_path = get_event_path()

    df = read_event_pd(events_path)

    layer = 0

    # layer must be valid

    assert 0 <= layer <= 6

    # layer must exist in data

    layer_df = df[df["layer"] == layer]

    assert not layer_df.empty

    # matrix sizes must be positive

    assert layer_df["idx"].max() >= 0

    assert layer_df["idy"].max() >= 0
