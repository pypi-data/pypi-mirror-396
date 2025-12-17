"""
Individual Quality Metrics

This module contains functions for calculating specific EEG quality metrics.
"""

import numpy as np
import pandas as pd
from scipy.signal import hilbert


def calculate_nan_quality(data: pd.DataFrame) -> float:
    """
    Calculate quality based on missing (NaN) values.

    Parameters
    ----------
    data : pd.DataFrame
        EEG data

    Returns
    -------
    float
        Quality score (0-100), where 100 = no missing values
    """
    total_values = data.size
    missing_values = data.isna().sum().sum()
    quality = (1 - missing_values / total_values) * 100
    return quality


def calculate_gap_quality(data: pd.DataFrame) -> float:
    """
    Calculate quality based on longest continuous valid segment.

    Parameters
    ----------
    data : pd.DataFrame
        EEG data

    Returns
    -------
    float
        Quality score (0-100), based on longest gap-free segment
    """
    # Find channel with fewest missing values
    missing_percentages = data.isna().mean()
    best_channel = missing_percentages.idxmin()
    best_channel_data = data[best_channel].values

    # Find longest valid subsequence
    mask = ~np.isnan(best_channel_data)
    diff = np.diff(np.concatenate(([0], mask.astype(int), [0])))
    starts = np.where(diff == 1)[0]
    ends = np.where(diff == -1)[0]

    longest_segment = np.max(ends - starts) if starts.size > 0 else 0
    quality = (longest_segment / len(data)) * 100

    return quality


def calculate_outlier_quality(data: pd.DataFrame, threshold: float = 2.0) -> float:
    """
    Calculate quality based on outlier detection.

    Parameters
    ----------
    data : pd.DataFrame
        EEG data
    threshold : float
        Number of standard deviations for outlier detection

    Returns
    -------
    float
        Quality score (0-100), where 100 = no outliers
    """
    std_all = data.values.std()
    anomalies = np.abs(data) > (threshold * std_all)
    quality = 100 * (1 - anomalies.sum().sum() / data.size)

    return quality


def calculate_flatline_quality(
    data: pd.DataFrame,
    sampling_rate: int,
    flat_duration_sec: float = 5.0,
    cv_threshold: float = 0.01,
) -> float:
    """
    Calculate quality based on flatline detection.

    Parameters
    ----------
    data : pd.DataFrame
        EEG data
    sampling_rate : int
        Sampling frequency in Hz
    flat_duration_sec : float
        Minimum duration (seconds) to consider as flatline
    cv_threshold : float
        Coefficient of variation threshold for flatline detection

    Returns
    -------
    float
        Quality score (0-100), where 100 = no flatlines
    """
    window_size = int(round(flat_duration_sec * sampling_rate))

    rolling = data.rolling(window=window_size, min_periods=1)
    rolling_mean = rolling.mean()
    rolling_std = rolling.std()

    rolling_mean[rolling_mean == 0] = np.nan
    rolling_cv = rolling_std / rolling_mean

    flat_mask = rolling_cv <= cv_threshold
    flat_percentage = flat_mask.mean(axis=0, skipna=True).mean() * 100
    quality = 100 - flat_percentage

    return quality


def calculate_sharpness_quality(data: pd.DataFrame, amplitude_threshold: float = 0.05) -> float:
    """
    Calculate quality based on sharp transitions/artifacts.

    Parameters
    ----------
    data : pd.DataFrame
        EEG data
    amplitude_threshold : float
        Threshold relative to 95th percentile for sharp transition detection

    Returns
    -------
    float
        Quality score (0-100), where 100 = no sharp artifacts
    """
    diff_signal = data.diff().abs()
    signal_percentile = data.abs().quantile(0.95, axis=0)

    large_changes = diff_signal >= amplitude_threshold * signal_percentile
    large_changes = large_changes.where(~diff_signal.isna(), np.nan)

    num_large_changes = large_changes.sum(axis=0, skipna=True)
    valid_samples = large_changes.notna().sum(axis=0)

    prop_large_changes = (num_large_changes / valid_samples).mean()
    quality = 100 * (1 - prop_large_changes)

    return quality


def calculate_cohesion_quality(data: pd.DataFrame) -> float:
    """
    Calculate quality based on phase-locking between channels.

    Uses Phase-Locking Value (PLV) to assess signal coherence across channels.

    Parameters
    ----------
    data : pd.DataFrame
        EEG data

    Returns
    -------
    float
        Quality score (0-100), based on average PLV
    """
    # Fill NaN for Hilbert transform
    eeg_data = data.fillna(0).values.T

    # Compute phases via Hilbert transform
    phases = np.angle(hilbert(eeg_data, axis=1))

    # Compute PLV matrix
    plv_matrix = np.abs(
        np.exp(1j * (phases[:, np.newaxis, :] - phases[np.newaxis, :, :])).mean(axis=2)
    )

    # Get upper triangle (unique pairs)
    upper_tri = np.triu_indices_from(plv_matrix, k=1)
    cohesion_score = 100 * np.nanmean(plv_matrix[upper_tri])

    return cohesion_score
