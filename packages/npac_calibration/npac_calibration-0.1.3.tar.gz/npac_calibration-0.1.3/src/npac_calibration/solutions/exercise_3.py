import pandas as pd

from validator import Validator

from npac_calibration.read_data.read_files import get_event_path

from npac_calibration.main.detector_calibration import DetectorCalibration


def ex(df):
    """

    Exercise 3: noise fit, peak counting, extended peak counting.

    Returns sigma per layer, number of peaks, number of extended peaks.
    """

    calib = DetectorCalibration(print_results=False)

    calib.run_all_layers(df, save_csv=False)

    layers = sorted(calib.all_layers_results.keys())

    sigma_layers = []

    n_peaks = []

    n_peaks_extended = []

    for layer in layers:
        peaks_info = calib.all_layers_results[layer]["peaks_info"]

        sigma_layers.append(peaks_info["sigma_noise"])

        n_peaks.append(len(peaks_info["x_peak"]))

        n_peaks_extended.append(len(peaks_info["x_bunch"]))

    return sigma_layers, n_peaks, n_peaks_extended


def main():
    events_path = get_event_path()

    df = pd.read_csv(events_path)

    sigma_layers, n_peaks, n_peaks_extended = ex(df)

    Validator.set_expected_results("calibration")

    Validator.check("exercise_3.2", sigma_layers)

    Validator.check("exercise_3.3", n_peaks)

    Validator.check("exercise_3.4", n_peaks_extended)


if __name__ == "__main__":
    main()
