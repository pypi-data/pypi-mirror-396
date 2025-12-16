import pytest
from npac_calibration.read_data.read_files import get_event_path, read_event_pd
from npac_calibration.main.detector_calibration import DetectorCalibration


def test_detector_calibration_layer0():
    # Load event data
    event_path = get_event_path()
    df = read_event_pd(event_path)

    # Run calibration
    calib = DetectorCalibration()
    result = calib.run_layer(df, layer=0)[0]

    # Expected correct values
    correct_result = {
        "layer": 0,
        "mu_x": -0.21533862193427922,
        "mu_y": 110.56069098293653,
        "sigma_x": 1.7468327263894645,
        "sigma_y": 1.5560098284491228,
    }

    # Compare each value using pytest.approx for floating point safety
    assert result["layer"] == correct_result["layer"]
    assert result["mu_x"] == pytest.approx(correct_result["mu_x"], rel=1e-2, abs=1e-2)
    assert result["mu_y"] == pytest.approx(correct_result["mu_y"], rel=1e-2, abs=1e-2)
    assert result["sigma_x"] == pytest.approx(
        correct_result["sigma_x"], rel=1e-2, abs=1e-2
    )
    assert result["sigma_y"] == pytest.approx(
        correct_result["sigma_y"], rel=1e-2, abs=1e-2
    )
