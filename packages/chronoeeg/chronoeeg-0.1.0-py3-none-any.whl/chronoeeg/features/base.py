"""
Base Feature Extractor Interface

Defines the common interface for all feature extractors.
"""

from abc import ABC, abstractmethod
from typing import Union

import numpy as np
import pandas as pd


class BaseFeatureExtractor(ABC):
    """
    Abstract base class for feature extractors.

    All feature extractors should inherit from this class and implement
    the extract() method.

    Parameters
    ----------
    sampling_rate : int
        Sampling frequency in Hz
    """

    def __init__(self, sampling_rate: int = 128):
        """Initialize base feature extractor."""
        self.sampling_rate = sampling_rate

    @abstractmethod
    def extract(self, data: Union[pd.DataFrame, np.ndarray]) -> pd.DataFrame:
        """
        Extract features from EEG data.

        Parameters
        ----------
        data : pd.DataFrame or np.ndarray
            EEG data with shape (n_samples, n_channels)

        Returns
        -------
        pd.DataFrame
            Extracted features
        """
        pass

    def _validate_input(self, data: Union[pd.DataFrame, np.ndarray]) -> pd.DataFrame:
        """
        Validate and convert input data to DataFrame.

        Parameters
        ----------
        data : pd.DataFrame or np.ndarray
            Input data

        Returns
        -------
        pd.DataFrame
            Validated DataFrame
        """
        if isinstance(data, np.ndarray):
            n_channels = data.shape[1] if len(data.shape) > 1 else 1
            data = pd.DataFrame(data, columns=[f"Ch{i+1}" for i in range(n_channels)])
        elif not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be pandas DataFrame or numpy array")

        if data.empty:
            raise ValueError("Input data is empty")

        return data

    def fit(self, X, y=None):
        """Scikit-learn compatible fit method (no-op for feature extractors)."""
        return self

    def transform(self, X: Union[pd.DataFrame, np.ndarray]) -> pd.DataFrame:
        """Scikit-learn compatible transform method."""
        return self.extract(X)

    def fit_transform(self, X: Union[pd.DataFrame, np.ndarray], y=None) -> pd.DataFrame:
        """Scikit-learn compatible fit_transform method."""
        return self.fit(X, y).transform(X)
