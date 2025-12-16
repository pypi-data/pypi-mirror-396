import csv


from validator import Validator


from npac_calibration.read_data.read_files import get_event_path, read_event_pd


# Read events using csv


def read_events_csv(events_path):
    """


    Read event data from a CSV file using the csv module.



    Args:


        events_path (str): Path to the CSV file.



    Returns:


        list of dict: List of events as dictionaries.
    """

    events = []

    with open(events_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            event = {
                "idx": int(row["idx"]),
                "idy": int(row["idy"]),
                "layer": int(row["layer"]),
                "id": int(row["id"]),
                "E": float(row["E"]),
            }

            events.append(event)

    return events


def main():
    """


    Run Exercise 1 validation by reading the event file using two methods


    (csv module and pandas) and checking the number of columns with the validator.
    """

    events_path = get_event_path()

    Validator.set_expected_results("calibration")  # given fron NPAC

    # Check CSV version

    events = read_events_csv(events_path)

    Validator.check("exercise_1", [len(events[0].keys())])

    # Check pandas version

    events = read_event_pd(events_path)

    Validator.check("exercise_1", [len(events.columns)])


if __name__ == "__main__":
    main()
