"""
Classical EEG Feature Extraction

This module extracts classical EEG features including entropy measures,
fractal dimensions, and spectral band powers.
"""

from typing import Dict, Union

import antropy as ant
import numpy as np
import pandas as pd
from scipy.integrate import simpson
from scipy.signal import welch

from chronoeeg.features.base import BaseFeatureExtractor


class ClassicalFeatureExtractor(BaseFeatureExtractor):
    """
    Extract classical EEG features from multi-channel data.

    Computes entropy measures, fractal dimensions, and spectral features
    for each channel, plus aggregate statistics across channels.

    Parameters
    ----------
    sampling_rate : int
        Sampling frequency in Hz (default: 128)

    Attributes
    ----------
    FREQ_BANDS : Dict[str, Tuple[float, float]]
        Frequency bands for spectral analysis (delta, theta, alpha, beta, gamma)

    Examples
    --------
    >>> extractor = ClassicalFeatureExtractor(sampling_rate=128)
    >>> features = extractor.extract(eeg_data)
    >>> print(f"Extracted {features.shape[1]} features")

    Notes
    -----
    Features are organized as:
    - Per-channel features: {feature}_{channel}
    - Summary statistics: {feature}_{mean|std}
    """

    FREQ_BANDS = {
        "delta": (0.5, 4),
        "theta": (4, 8),
        "alpha": (8, 13),
        "beta": (13, 30),
        "gamma": (30, 45),
    }

    def __init__(self, sampling_rate: int = 128):
        """Initialize classical feature extractor."""
        super().__init__(sampling_rate)

    def extract(self, data: Union[pd.DataFrame, np.ndarray]) -> pd.DataFrame:
        """
        Extract all classical features from EEG data.

        Parameters
        ----------
        data : pd.DataFrame or np.ndarray
            EEG data with shape (n_samples, n_channels)

        Returns
        -------
        pd.DataFrame
            Feature DataFrame with shape (1, n_features)
            Contains per-channel features and summary statistics
        """
        # Validate and convert input
        df = self._validate_input(data)

        # Extract features per channel
        feature_list = df.apply(
            lambda col: {
                **self._compute_entropy_features(col.values),
                **self._compute_fractal_features(col.values),
                **self._compute_spectral_features(col.values),
            },
            axis=0,
        )

        # Convert to DataFrame
        feature_df = pd.DataFrame(feature_list.tolist(), index=df.columns)

        # Flatten per-channel features
        feature_flat = feature_df.stack().to_frame().T
        feature_flat.columns = [f"{feature}_{channel}" for channel, feature in feature_flat.columns]

        # Compute summary statistics across channels
        summary_stats = feature_df.aggregate(["mean", "std"])
        summary_stats_flat = summary_stats.unstack().to_frame().T
        summary_stats_flat.columns = [
            f"{feature}_{stat}" for feature, stat in summary_stats_flat.columns
        ]

        # Combine all features
        final_df = pd.concat([feature_flat, summary_stats_flat], axis=1)

        return final_df

    def _compute_entropy_features(self, data: np.ndarray) -> Dict[str, float]:
        """
        Compute entropy-based features.

        Parameters
        ----------
        data : np.ndarray
            Single-channel EEG data

        Returns
        -------
        Dict[str, float]
            Dictionary of entropy features:
            - ENT_perm: Permutation entropy
            - ENT_spectral: Spectral entropy
            - ENT_svd: SVD entropy
        """
        try:
            entropy_values = {
                "ENT_perm": ant.perm_entropy(data, normalize=True),
                "ENT_spectral": ant.spectral_entropy(
                    data, sf=self.sampling_rate, method="welch", normalize=True
                ),
                "ENT_svd": ant.svd_entropy(data, normalize=True),
            }
        except Exception as e:
            # Return -1 for failed computations
            entropy_values = {
                "ENT_perm": -1.0,
                "ENT_spectral": -1.0,
                "ENT_svd": -1.0,
            }

        return entropy_values

    def _compute_fractal_features(self, data: np.ndarray) -> Dict[str, float]:
        """
        Compute fractal dimension features.

        Parameters
        ----------
        data : np.ndarray
            Single-channel EEG data

        Returns
        -------
        Dict[str, float]
            Dictionary of fractal features:
            - FRC_higuchi: Higuchi fractal dimension
            - FRC_petrosian: Petrosian fractal dimension
            - FRC_katz: Katz fractal dimension
        """
        try:
            fractal_values = {
                "FRC_higuchi": ant.higuchi_fd(data),
                "FRC_petrosian": ant.petrosian_fd(data),
                "FRC_katz": ant.katz_fd(data),
            }
        except Exception as e:
            fractal_values = {
                "FRC_higuchi": -1.0,
                "FRC_petrosian": -1.0,
                "FRC_katz": -1.0,
            }

        return fractal_values

    def _compute_spectral_features(self, data: np.ndarray) -> Dict[str, float]:
        """
        Compute spectral power features.

        Computes relative power in delta, theta, alpha, beta, and gamma bands.

        Parameters
        ----------
        data : np.ndarray
            Single-channel EEG data

        Returns
        -------
        Dict[str, float]
            Dictionary of spectral features:
            - SPC_delta: Relative power in delta band
            - SPC_theta: Relative power in theta band
            - SPC_alpha: Relative power in alpha band
            - SPC_beta: Relative power in beta band
            - SPC_gamma: Relative power in gamma band
        """
        # Compute power spectral density
        f, Pxx = welch(data, fs=self.sampling_rate, nperseg=4 * self.sampling_rate)

        # Compute power in each frequency band
        power = {}
        for band, (low, high) in self.FREQ_BANDS.items():
            band_mask = (f >= low) & (f < high)
            power[band] = simpson(Pxx[band_mask], f[band_mask])

        # Compute total power and normalize
        total_power = sum(power.values())
        total_power = max(total_power, 1e-10)  # Avoid division by zero

        rel_power = {f"SPC_{band}": pwr / total_power for band, pwr in power.items()}

        return rel_power


# Backwards compatibility alias
extract_all_features = ClassicalFeatureExtractor.extract
