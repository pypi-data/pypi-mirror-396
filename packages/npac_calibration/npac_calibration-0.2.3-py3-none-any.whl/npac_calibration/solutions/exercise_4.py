import pandas as pd
from validator import Validator
from npac_calibration.read_data.read_files import get_event_path
from npac_calibration.main.detector_calibration import DetectorCalibration


def ex(df):
    """
    Exercise 4.1 using DetectorCalibration.

    We run the full calibration on layer 0, then take the most luminous bunch
    (the class already sorts by luminosity descending).
    Returns (mu_x, mu_y, sigma_x, sigma_y) in mm.
    """
    calib = DetectorCalibration()
    results = calib.run_layer(df, layer=0)

    if not results:
        raise RuntimeError("No bunches found in layer 0, cannot validate exercise_4.1")

    best = results[0]  # most luminous bunch (already sorted)

    mu_x = best["mu_x"]
    mu_y = best["mu_y"]
    sigma_x = best["sigma_x"]
    sigma_y = best["sigma_y"]

    return mu_x, mu_y, sigma_x, sigma_y


def main():
    events_path = get_event_path()
    df = pd.read_csv(events_path)

    mu_x, mu_y, sigma_x, sigma_y = ex(df)

    Validator.set_expected_results("calibration")
    Validator.check("exercise_4.1", [mu_x, mu_y, sigma_x, sigma_y])


if __name__ == "__main__":
    main()
