"""
Advanced validators for data quality and consistency checks.
"""

from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

from chronoeeg.exceptions import ChannelMismatchError, DataValidationError


class AdvancedValidator:
    """
    Advanced validation for EEG data.

    Provides comprehensive checks for data quality, consistency,
    and format compliance.
    """

    @staticmethod
    def validate_sampling_rate(
        data: pd.DataFrame, expected_rate: int, tolerance: float = 0.01
    ) -> bool:
        """
        Validate sampling rate consistency.

        Parameters
        ----------
        data : pd.DataFrame
            Time-series data with datetime index
        expected_rate : int
            Expected sampling rate in Hz
        tolerance : float
            Acceptable deviation (default: 1%)

        Returns
        -------
        bool
            True if sampling rate is consistent

        Raises
        ------
        DataValidationError
            If sampling rate is inconsistent
        """
        if not isinstance(data.index, pd.DatetimeIndex):
            raise DataValidationError("Data must have DatetimeIndex for sampling rate validation")

        # Calculate actual sampling rate
        time_diffs = data.index.to_series().diff().dt.total_seconds()
        actual_rate = 1.0 / time_diffs.median()

        deviation = abs(actual_rate - expected_rate) / expected_rate

        if deviation > tolerance:
            raise DataValidationError(
                f"Sampling rate mismatch: expected {expected_rate} Hz, "
                f"got {actual_rate:.2f} Hz (deviation: {deviation*100:.2f}%)"
            )

        return True

    @staticmethod
    def validate_channels(
        data: pd.DataFrame,
        expected_channels: Optional[List[str]] = None,
        min_channels: int = 1,
        max_channels: Optional[int] = None,
    ) -> bool:
        """
        Validate channel configuration.

        Parameters
        ----------
        data : pd.DataFrame
            EEG data
        expected_channels : list of str, optional
            Expected channel names
        min_channels : int
            Minimum number of channels required
        max_channels : int, optional
            Maximum number of channels allowed

        Returns
        -------
        bool
            True if channels are valid

        Raises
        ------
        ChannelMismatchError
            If channel configuration is invalid
        """
        n_channels = len(data.columns)

        if n_channels < min_channels:
            raise ChannelMismatchError(
                f"Insufficient channels: got {n_channels}, minimum required {min_channels}"
            )

        if max_channels is not None and n_channels > max_channels:
            raise ChannelMismatchError(
                f"Too many channels: got {n_channels}, maximum allowed {max_channels}"
            )

        if expected_channels is not None:
            missing = set(expected_channels) - set(data.columns)
            if missing:
                raise ChannelMismatchError(f"Missing expected channels: {missing}")

            extra = set(data.columns) - set(expected_channels)
            if extra:
                raise ChannelMismatchError(f"Unexpected channels found: {extra}")

        return True

    @staticmethod
    def validate_amplitude_range(
        data: pd.DataFrame,
        min_value: float = -500.0,
        max_value: float = 500.0,
        max_outlier_fraction: float = 0.01,
    ) -> bool:
        """
        Validate amplitude values are within physiological range.

        Parameters
        ----------
        data : pd.DataFrame
            EEG data in microvolts
        min_value : float
            Minimum acceptable value
        max_value : float
            Maximum acceptable value
        max_outlier_fraction : float
            Maximum fraction of outliers allowed

        Returns
        -------
        bool
            True if amplitudes are valid

        Raises
        ------
        DataValidationError
            If too many values are out of range
        """
        outliers = ((data < min_value) | (data > max_value)).sum().sum()
        total = data.size
        outlier_fraction = outliers / total

        if outlier_fraction > max_outlier_fraction:
            raise DataValidationError(
                f"Too many amplitude outliers: {outlier_fraction*100:.2f}% "
                f"(threshold: {max_outlier_fraction*100:.2f}%)"
            )

        return True

    @staticmethod
    def validate_no_constant_channels(
        data: pd.DataFrame,
        tolerance: float = 1e-6,
    ) -> bool:
        """
        Check for constant (flatline) channels.

        Parameters
        ----------
        data : pd.DataFrame
            EEG data
        tolerance : float
            Variance threshold below which channel is considered constant

        Returns
        -------
        bool
            True if no constant channels found

        Raises
        ------
        DataValidationError
            If constant channels are detected
        """
        variances = data.var()
        constant_channels = variances[variances < tolerance].index.tolist()

        if constant_channels:
            raise DataValidationError(f"Constant channels detected: {constant_channels}")

        return True

    @staticmethod
    def validate_no_missing_segments(
        data: pd.DataFrame,
        max_gap_seconds: float = 1.0,
    ) -> bool:
        """
        Check for missing time segments.

        Parameters
        ----------
        data : pd.DataFrame
            Time-series data with datetime index
        max_gap_seconds : float
            Maximum acceptable gap in seconds

        Returns
        -------
        bool
            True if no large gaps found

        Raises
        ------
        DataValidationError
            If large time gaps are detected
        """
        if not isinstance(data.index, pd.DatetimeIndex):
            raise DataValidationError("Data must have DatetimeIndex for gap validation")

        time_diffs = data.index.to_series().diff().dt.total_seconds()
        large_gaps = time_diffs[time_diffs > max_gap_seconds]

        if not large_gaps.empty:
            raise DataValidationError(
                f"Found {len(large_gaps)} time gaps larger than {max_gap_seconds}s. "
                f"Largest gap: {large_gaps.max():.2f}s"
            )

        return True

    @staticmethod
    def validate_epoch_quality(
        epochs: pd.DataFrame,
        epoch_column: str = "epoch_id",
        min_valid_fraction: float = 0.8,
    ) -> bool:
        """
        Validate that most epochs have sufficient valid data.

        Parameters
        ----------
        epochs : pd.DataFrame
            Epoched data
        epoch_column : str
            Name of epoch identifier column
        min_valid_fraction : float
            Minimum fraction of valid (non-NaN) data per epoch

        Returns
        -------
        bool
            True if epochs are valid

        Raises
        ------
        DataValidationError
            If too many epochs have insufficient data
        """
        data_columns = [col for col in epochs.columns if col != epoch_column]

        epoch_validity = []
        for epoch_id in epochs[epoch_column].unique():
            epoch_data = epochs[epochs[epoch_column] == epoch_id][data_columns]
            valid_fraction = (~epoch_data.isna()).mean().mean()
            epoch_validity.append(valid_fraction)

        low_quality_epochs = sum(1 for v in epoch_validity if v < min_valid_fraction)
        total_epochs = len(epoch_validity)

        if low_quality_epochs > total_epochs * 0.2:  # More than 20% bad epochs
            raise DataValidationError(
                f"{low_quality_epochs}/{total_epochs} epochs have insufficient valid data "
                f"(< {min_valid_fraction*100:.0f}%)"
            )

        return True

    @classmethod
    def validate_all(
        cls,
        data: pd.DataFrame,
        sampling_rate: Optional[int] = None,
        expected_channels: Optional[List[str]] = None,
    ) -> bool:
        """
        Run all validation checks.

        Parameters
        ----------
        data : pd.DataFrame
            EEG data to validate
        sampling_rate : int, optional
            Expected sampling rate
        expected_channels : list of str, optional
            Expected channel names

        Returns
        -------
        bool
            True if all validations pass

        Raises
        ------
        DataValidationError, ChannelMismatchError
            If any validation fails
        """
        # Channel validation
        cls.validate_channels(data, expected_channels=expected_channels)

        # Amplitude validation
        cls.validate_amplitude_range(data)

        # Constant channel check
        cls.validate_no_constant_channels(data)

        # Sampling rate validation (if datetime index available)
        if isinstance(data.index, pd.DatetimeIndex) and sampling_rate is not None:
            cls.validate_sampling_rate(data, sampling_rate)
            cls.validate_no_missing_segments(data)

        return True
