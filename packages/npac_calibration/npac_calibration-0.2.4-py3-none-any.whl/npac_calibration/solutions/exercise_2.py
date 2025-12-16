import pandas as pd

from validator import Validator

from npac_calibration.read_data.read_files import get_event_path


def ex1(events_path):
    """

    Compute the total deposited energy in layer 0 from an event CSV file.


    Args:

        events_path (str): Path to the event CSV file.


    Returns:

        float: Sum of the energy values in layer 0.
    """

    # read dataframe

    df = pd.read_csv(events_path)

    mask = df["layer"] == 0  # only layer 0

    layer0_sum = df[mask]["E"].sum()  # sum of energy on layer 0

    return layer0_sum


def ex2(events_path):
    """

    Compute the image shape (nx, ny) of layer 0 from an event CSV file.


    Args:

        events_path (str): Path to the event CSV file.


    Returns:

        list of int: [nx, ny] shape of the layer 0 image.
    """

    df = pd.read_csv(events_path)

    mask = df["layer"] == 0  # only layer 0

    idx_shape = df[mask]["idx"].max() + 1

    idy_shape = df[mask]["idy"].max() + 1

    return [idx_shape, idy_shape]


def main():
    """

    Run the computations for exercises 2.1 and 2.2
    and validate their outputs.
    """

    events_path = get_event_path()

    layer0_sum = ex1(events_path)

    layer0_shape = ex2(events_path)

    # validation

    Validator.set_expected_results("calibration")

    Validator.check("exercise_2.1", layer0_sum)

    Validator.check("exercise_2.2", layer0_shape)


if __name__ == "__main__":
    main()
