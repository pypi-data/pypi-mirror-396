"""
Data Validators

Validation utilities for EEG data quality and format checking.
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class DataValidator:
    """
    Validator for EEG data integrity and format compliance.

    Examples
    --------
    >>> validator = DataValidator()
    >>> is_valid, issues = validator.validate_dataframe(eeg_data)
    >>> if not is_valid:
    ...     print(f"Validation issues: {issues}")
    """

    def __init__(self, sampling_rate: Optional[float] = None):
        """
        Initialize validator.

        Parameters
        ----------
        sampling_rate : float, optional
            Expected sampling rate in Hz
        """
        self.sampling_rate = sampling_rate

    def validate_dataframe(
        self, data: pd.DataFrame, expected_channels: Optional[List[str]] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate EEG DataFrame format and quality.

        Parameters
        ----------
        data : pd.DataFrame
            EEG data to validate
        expected_channels : List[str], optional
            Expected channel names

        Returns
        -------
        is_valid : bool
            Whether the data passes all validation checks
        issues : List[str]
            List of validation issues found
        """
        issues = []

        # Check if empty
        if data.empty:
            issues.append("DataFrame is empty")
            return False, issues

        # Check for NaN values
        nan_ratio = data.isna().sum().sum() / data.size
        if nan_ratio > 0.5:
            issues.append(f"High ratio of NaN values: {nan_ratio:.2%}")

        # Check for infinite values
        if np.isinf(data.select_dtypes(include=[np.number])).any().any():
            issues.append("DataFrame contains infinite values")

        # Check channel names
        if expected_channels is not None:
            missing_channels = set(expected_channels) - set(data.columns)
            if missing_channels:
                issues.append(f"Missing expected channels: {missing_channels}")

        # Check data types
        non_numeric = [col for col in data.columns if not pd.api.types.is_numeric_dtype(data[col])]
        if non_numeric:
            issues.append(f"Non-numeric columns found: {non_numeric}")

        # Check for constant channels
        constant_channels = [col for col in data.columns if data[col].nunique() <= 1]
        if constant_channels:
            issues.append(f"Constant channels detected: {constant_channels}")

        is_valid = len(issues) == 0
        return is_valid, issues

    def check_sampling_rate(
        self, data: pd.DataFrame, time_column: Optional[str] = None
    ) -> Tuple[bool, float]:
        """
        Verify sampling rate consistency.

        Parameters
        ----------
        data : pd.DataFrame
            EEG data
        time_column : str, optional
            Name of time column if present

        Returns
        -------
        is_consistent : bool
            Whether sampling rate is consistent
        detected_rate : float
            Detected sampling rate
        """
        if time_column and time_column in data.columns:
            time_diffs = data[time_column].diff().dropna()
            detected_rate = 1.0 / time_diffs.median()
        elif self.sampling_rate:
            detected_rate = self.sampling_rate
        else:
            # Cannot determine without time information
            return True, 0.0

        is_consistent = True
        if self.sampling_rate:
            tolerance = 0.01  # 1% tolerance
            if abs(detected_rate - self.sampling_rate) / self.sampling_rate > tolerance:
                is_consistent = False

        return is_consistent, detected_rate
