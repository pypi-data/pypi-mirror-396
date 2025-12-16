# NPAC Detector Calibration

[![CI/CD](https://img.shields.io/badge/CI%2FCD-passing-brightgreen)](https://gitlab.in2p3.fr/informatique-des-deux-infinis/npac/2026/silver-wolf/calibration/-/pipelines)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/npac_calibration.svg)](https://pypi.org/project/npac_calibration/)

A suite of tools for the calibration of particle detectors using simulation data. This project is designed to process raw data, identify particle interaction peaks, perform Gaussian fits, and determine calibration constants.

## Features

- Read and process particle detector simulation data.
- Identify particle interaction peaks in detector layers.
- Perform Gaussian fits on identified peaks.
- Determine calibration constants for energy calibration.
- Command-line interface for running calibration on all layers.

## Installation

This project is managed with [PDM](https://pdm.fming.dev).

### Option 1: Install from PyPI

```bash
pip install npac_calibration
# or using PDM
pdm add npac_calibration
````

### Option 2: Install from GitLab repository (development version)

```bash
pdm add git+https://gitlab.in2p3.fr/informatique-des-deux-infinis/npac/2026/silver-wolf/calibration.git
```

### Optional: Add NPAC Validator

To use the validator, install the `npac_validator` package in your PDM environment, then edit the `pyproject.toml` file and add:

```toml
[[tool.pdm.source]]
name = "npac_gitlab"
url = "https://gitlab.in2p3.fr/api/v4/projects/26344/packages/pypi/simple"
```

## Usage

After installation, you can use the package like this:

```python
from npac_calibration.main.detector_calibration import DetectorCalibration
import pandas as pd

# Path to event files
event_path = "data/electron_1GeV_Shower/event000000047-hits_digitised.csv"

# Read events into a DataFrame
df = pd.read_csv(event_path)

# Initialize the detector calibration
calib = DetectorCalibration()

# Run calibration for all layers
all_results = calib.run_all_layers(df, save_csv=True)

# Get peak information for a specific layer
layer0_peaks = calib.get_peaks_info(layer=0)
print("Peaks found in layer 0:", layer0_peaks["x_peak"])
```

You can also run the calibration for all layers from the command line:

```bash
pdm run calibrate
```

## Contributing

Contributions are welcome! Feel free to open an issue or submit a merge request.


## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
