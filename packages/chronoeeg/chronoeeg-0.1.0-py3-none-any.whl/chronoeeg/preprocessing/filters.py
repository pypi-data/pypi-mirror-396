"""Signal filtering utilities."""

from typing import Optional, Tuple

import numpy as np
import pandas as pd
from scipy import signal


class SignalFilter:
    """
    EEG signal filtering utilities.

    Supports bandpass, lowpass, highpass, and notch filtering.

    Parameters
    ----------
    sampling_rate : float
        Sampling rate in Hz

    Examples
    --------
    >>> filter = SignalFilter(sampling_rate=128)
    >>> filtered = filter.bandpass(data, lowcut=0.5, highcut=45)
    >>> filtered = filter.notch(filtered, freq=50)  # Remove power line noise
    """

    def __init__(self, sampling_rate: float):
        """Initialize filter."""
        self.sampling_rate = sampling_rate

    def bandpass(
        self, data: pd.DataFrame, lowcut: float, highcut: float, order: int = 5
    ) -> pd.DataFrame:
        """
        Apply bandpass filter.

        Parameters
        ----------
        data : pd.DataFrame
            Input data
        lowcut : float
            Low cutoff frequency in Hz
        highcut : float
            High cutoff frequency in Hz
        order : int
            Filter order

        Returns
        -------
        pd.DataFrame
            Filtered data
        """
        nyq = 0.5 * self.sampling_rate
        low = lowcut / nyq
        high = highcut / nyq
        b, a = signal.butter(order, [low, high], btype="band")

        filtered = data.apply(lambda col: signal.filtfilt(b, a, col))
        return filtered

    def notch(self, data: pd.DataFrame, freq: float = 50.0, quality: float = 30.0) -> pd.DataFrame:
        """
        Apply notch filter (for power line noise removal).

        Parameters
        ----------
        data : pd.DataFrame
            Input data
        freq : float
            Frequency to remove (50 or 60 Hz typically)
        quality : float
            Quality factor

        Returns
        -------
        pd.DataFrame
            Filtered data
        """
        b, a = signal.iirnotch(freq, quality, self.sampling_rate)
        filtered = data.apply(lambda col: signal.filtfilt(b, a, col))
        return filtered

    def lowpass(self, data: pd.DataFrame, cutoff: float, order: int = 5) -> pd.DataFrame:
        """
        Apply lowpass filter.

        Parameters
        ----------
        data : pd.DataFrame
            Input data
        cutoff : float
            Cutoff frequency in Hz
        order : int
            Filter order

        Returns
        -------
        pd.DataFrame
            Filtered data
        """
        nyq = 0.5 * self.sampling_rate
        normal_cutoff = cutoff / nyq
        b, a = signal.butter(order, normal_cutoff, btype="low")
        filtered = data.apply(lambda col: signal.filtfilt(b, a, col))
        return filtered

    def highpass(self, data: pd.DataFrame, cutoff: float, order: int = 5) -> pd.DataFrame:
        """
        Apply highpass filter.

        Parameters
        ----------
        data : pd.DataFrame
            Input data
        cutoff : float
            Cutoff frequency in Hz
        order : int
            Filter order

        Returns
        -------
        pd.DataFrame
            Filtered data
        """
        nyq = 0.5 * self.sampling_rate
        normal_cutoff = cutoff / nyq
        b, a = signal.butter(order, normal_cutoff, btype="high")
        filtered = data.apply(lambda col: signal.filtfilt(b, a, col))
        return filtered
