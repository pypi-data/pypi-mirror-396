"""
This module defines the DetectorCalibration class, which is used to process and
analyze detector data. It includes methods for finding peaks, fitting Gaussian
distributions, and calculating luminosity for different layers of the detector.
"""
import os
import numpy as np
import pandas as pd
import npac_calibration.plots.plot as npt
from npac_calibration.main.gaussian_fit import fit_gaussian, fit_gaussian_2d
from npac_calibration.main.functions import threshold
from npac_calibration.main.peaks import (
    find_peaks_and_bunches,
    integrated_luminosity_for_peak,
)
from .utils import df_to_matrix, extracted_image, convert_to_mm
from typing import List, Dict, Any, Optional


class DetectorCalibration:
    """
    A class to handle the calibration of the detector by processing data from
    different layers.
    """

    def __init__(
        self, outdir: str = "beam_results", print_results: bool = True
    ) -> None:
        """
        Initializes the DetectorCalibration object.

        Args:
            outdir (str): The directory where the output results will be saved.
            print_results (bool): If True, prints the results to the console.
        """
        self.outdir = outdir
        self.print_results = print_results
        self._reset_all()

    def _reset_all(self) -> None:
        """
        Resets all attributes of the class to their initial states. This is useful
        when starting a new calibration process.
        """
        self._reset_peaks()
        self.all_layers_results: Dict[
            int, Dict[str, Any]
        ] = {}  # Store results for all layers
        self.combined_df: Optional[
            pd.DataFrame
        ] = None  # Combined DataFrame for all layers

    def _reset_peaks(self) -> None:
        """
        Resets the peak-related attributes for the current layer. This is called
        before processing a new layer.
        """
        self.x_peak: Optional[np.ndarray] = None
        self.y_peak: Optional[np.ndarray] = None
        self.x_bunch: Optional[np.ndarray] = None
        self.y_bunch: Optional[np.ndarray] = None
        self.luminosity: Optional[np.ndarray] = None
        self.sigma_noise: Optional[float] = None
        self.threshold: Optional[float] = None
        self.image: Optional[np.ndarray] = None
        self.layer: Optional[int] = None

    def get_peaks_info(self, layer: Optional[int] = None) -> Dict[str, Any]:
        """
        Returns a dictionary containing information about the peaks for a specified
        layer.

        Args:
            layer (int, optional): The layer for which to retrieve peak information.
                                 If None, returns info for the current layer.

        Returns:
            dict: A dictionary with peak information.
        """
        if layer is not None and layer in self.all_layers_results:
            peaks_data = self.all_layers_results[layer].get("peaks_info", {})
            return peaks_data

        return {
            "x_peak": self.x_peak,
            "y_peak": self.y_peak,
            "x_bunch": self.x_bunch,
            "y_bunch": self.y_bunch,
            "luminosity": self.luminosity,
            "sigma_noise": self.sigma_noise,
            "threshold": self.threshold,
            "layer": self.layer,
        }

    def _save_to_csv(
        self,
        results: List[Dict[str, Any]],
        filename: str,
        sort_by_luminosity: bool = True,
    ) -> str:
        """
        Saves the given results to a CSV file.

        Args:
            results (list of dict): The data to be saved.
            filename (str): The name of the output CSV file.
            sort_by_luminosity (bool): If True, sorts the results by luminosity
                                     in descending order.

        Returns:
            str: The path to the saved CSV file.
        """
        # Create output directory if it doesn't exist
        os.makedirs(self.outdir, exist_ok=True)

        # Convert results to DataFrame
        df = pd.DataFrame(results)

        # Sort by luminosity if requested
        if sort_by_luminosity and "luminosity" in df.columns:
            df = df.sort_values("luminosity", ascending=False)

        filepath = os.path.join(self.outdir, filename)

        # Save to CSV
        df.to_csv(filepath, index=False)
        if self.print_results:
            print(f"Results saved to: {filepath}")

        return filepath

    def _process_layer(self, df: pd.DataFrame, layer: int) -> List[Dict[str, Any]]:
        """
        Processes the data for a single detector layer.

        Args:
            df (pd.DataFrame): The input DataFrame containing detector data.
            layer (int): The layer number to process.

        Returns:
            list: A list of dictionaries, where each dictionary contains the
                  calibration results for a detected bunch.
        """
        # Reset peaks for current layer
        self._reset_peaks()
        self.layer = layer

        # Select layer data
        layer_df = df[df["layer"] == layer]

        # Noise fit + threshold
        _, sigma_noise, mu_noise, _, _ = fit_gaussian(layer_df["E"].values)
        thres = threshold(mu_noise, sigma_noise, n=3)

        # Store noise info
        self.sigma_noise = float(sigma_noise)
        self.threshold = float(thres)

        # Convert df -> image
        image = df_to_matrix(layer_df)
        self.image = image

        # Find all bunch peaks
        x_peak, y_peak, x_bunch, y_bunch = find_peaks_and_bunches(image, thres)

        # Store peaks as numpy arrays
        self.x_peak = np.asarray(x_peak)
        self.y_peak = np.asarray(y_peak)
        self.x_bunch = np.asarray(x_bunch)
        self.y_bunch = np.asarray(y_bunch)

        if len(x_bunch) == 0:
            if self.print_results:
                print(f"Warning: No peaks found in layer {layer}")
            return []

        results = []
        L_values = []

        # Process all bunches
        for x0, y0 in zip(x_bunch, y_bunch):
            # extract 20x20 patch
            sub = extracted_image(image, int(x0), int(y0))

            # fit 2D Gaussian
            popt, _ = fit_gaussian_2d(sub)
            _, sigma_x, mu_x, sigma_y, mu_y = popt

            # convert local → global pixel coordinates
            mu_x_det = y0 + mu_y - 10
            mu_y_det = x0 + mu_x - 10

            coords_mm, sigma_mm = convert_to_mm(
                (mu_x_det, mu_y_det),
                (sigma_x, sigma_y),
                pixel_size=2,
                min_position_mm=-400,
            )

            # Calculate luminosity
            L = integrated_luminosity_for_peak(image, int(x0), int(y0))
            L_values.append(float(L))

            # store result
            result = {
                "layer": layer,
                "mu_x": float(coords_mm[0]),
                "mu_y": float(coords_mm[1]),
                "sigma_x": float(sigma_mm[0]),
                "sigma_y": float(sigma_mm[1]),
                "pixel_x": int(x0),
                "pixel_y": int(y0),
                "luminosity": float(L),
            }

            results.append(result)

        # Store luminosities
        self.luminosity = np.asarray(L_values)

        # Sort results by luminosity
        if results:
            # Create a DataFrame to sort easily
            results_df = pd.DataFrame(results)
            results_df = results_df.sort_values("luminosity", ascending=False)
            results = results_df.to_dict("records")

        # Store peaks info for this layer
        self.all_layers_results[layer] = {
            "results": results,
            "peaks_info": self.get_peaks_info(),
        }

        return results

    def run_layer(
        self, df: pd.DataFrame, layer: int, save_csv: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Runs the calibration process for a single specified layer.

        Args:
            df (pd.DataFrame): The input DataFrame.
            layer (int): The layer number to process.
            save_csv (bool): If True, saves the results to a CSV file.

        Returns:
            list: A list of calibration results for the layer.
        """
        results = self._process_layer(df, layer)

        if not results:
            return []

        # Save to CSV if requested
        if save_csv:
            filename = f"layer_{layer}_bunches.csv"
            self._save_to_csv(
                results, filename, sort_by_luminosity=False
            )  # Already sorted

        # Return results (already sorted by luminosity)
        return results

    def run_all_layers(
        self,
        df: pd.DataFrame,
        layers: Optional[List[int]] = None,
        save_csv: bool = True,
    ) -> Dict[int, List[Dict[str, Any]]]:
        """
        Run calibration for all layers.

        Args:
            df (pd.DataFrame): Input data.
            layers (list, optional): List of layers to process. If None, all
                                     unique layers in df will be processed.
            save_csv (bool): If True, saves CSV files for each layer and a
                             combined file for all layers.

        Returns:
            dict: A dictionary with results for each layer.
        """
        # Reset all data
        self._reset_all()

        # Determine which layers to process
        if layers is None:
            layers = sorted(df["layer"].unique())

        all_results: Dict[int, List[Dict[str, Any]]] = {}
        all_combined_results: List[Dict[str, Any]] = []

        if self.print_results:
            print(f"Processing {len(layers)} layers: {layers}")

        for layer in layers:
            if self.print_results:
                print(f"\nProcessing layer {layer}...")

            try:
                results = self._process_layer(df, layer)

                if not results:
                    if self.print_results:
                        print(f"  No peaks found in layer {layer}")
                    all_results[layer] = []
                    continue

                # Store results
                all_results[layer] = results
                all_combined_results.extend(results)

                # Save individual layer CSV if requested
                if save_csv:
                    filename = f"layer_{layer}_bunches.csv"
                    self._save_to_csv(
                        results, filename, sort_by_luminosity=False
                    )  # Already sorted

                if self.print_results:
                    print(f"  Found {len(results)} bunches")

            except Exception as e:
                if self.print_results:
                    print(f"  Error processing layer {layer}: {e}")
                all_results[layer] = []

        # Save combined CSV if requested and we have results
        if save_csv and all_combined_results:
            # Sort all combined results by luminosity
            combined_df = pd.DataFrame(all_combined_results)
            # combined_df = combined_df.sort_values('luminosity', ascending=False)
            self.combined_df = combined_df

            filename = "all_layers_bunches.csv"
            filepath = os.path.join(self.outdir, filename)
            combined_df.to_csv(filepath, index=False)
            if self.print_results:
                print(f"\nCombined results saved to: {filepath}")
                print(f"Total bunches across all layers: {len(combined_df)}")

        return all_results

    def _ensure_layer_processed(self, layer_id, df=None):
        """
        To make sure layer_id has been processed and we have:
        - image
        - bunch coordinates/results
        If not processed, process it if df is provided.
        """
        already = (
            layer_id in self.all_layers_results
            and self.all_layers_results[layer_id].get("results") is not None
        )
        if already:
            return

        if df is None:
            raise RuntimeError(
                f"Layer {layer_id} is not processed yet. "
                f"Call run_layer(df, {layer_id}) first or pass df to "
                f"visualize_bunch(df=...)."
            )

        # process without saving csv
        self._process_layer(df, layer_id)

    def visualize_extended_peak(
        self,
        layer,
        df,
        mode="all",
        peak_number=None,
        focus_size=20,
    ):
        """
        Visualize bunches for a given layer.

        Parameters
        ----------
        layer : int
            Index of layer to visualize.
        df : pd.DataFrame
            Event data.
        mode : str
            "all" -> plot whole layer with all bunches
            "focus" -> zoom around one bunch (peak_number required)
        peak_number : int or None
            Index of the extended peak to focus on (0-based, based on luminosity-sorted
            results).
        focus_size : int
            Patch size for focus view (extracted_image uses 20x20 by default).
        """
        mode = mode.lower().strip()
        if mode not in {"all", "focus"}:
            raise ValueError('mode must be "all" or "focus"')

        # Ensure we have results for that layer
        self._ensure_layer_processed(layer, df=df)

        image = None

        # If you adopt the "store image per layer" change, use this:
        layer_pack = self.all_layers_results[layer]
        image = layer_pack.get("image", None)

        if image is None:
            if df is None:
                raise RuntimeError(
                    "Image for this layer is not stored. "
                    "Either pass df=... to visualize_bunch or store images per layer."
                )
            layer_df = df[df["layer"] == layer]
            image = df_to_matrix(layer_df)

        results = self.all_layers_results[layer].get("results", [])
        if not results:
            raise RuntimeError(f"No bunch results stored for layer {layer}.")

        # bunch pixel coords are in results dicts
        xs = [r["pixel_x"] for r in results]
        ys = [r["pixel_y"] for r in results]
        sig_x = [r["sigma_x"] for r in results]
        sig_y = [r["sigma_y"] for r in results]

        if mode == "all":
            npt.plot_all_extended_peaks(image, xs, ys, layer)
            return

        # mode == "focus"
        if peak_number is None:
            raise ValueError(
                'For mode="focus", you must provide peak_number (i.e. peak index, '
                "0-based)."
            )

        if not isinstance(peak_number, int):
            raise TypeError("peak_number must be an integer (0-based index).")

        if peak_number < 0 or peak_number >= len(results):
            raise IndexError(
                f"peak_number={peak_number} is out of range. "
                f"Valid range is 0..{len(results)-1} for layer {layer}."
            )

        # Extract patch around that bunch
        sub = extracted_image(image, int(xs[peak_number]), int(ys[peak_number]))

        npt.plot_focus_extended_peak(
            sub,
            sig_x[peak_number],
            sig_y[peak_number],
            sigma_level=3,
            focus_size=focus_size,
        )
