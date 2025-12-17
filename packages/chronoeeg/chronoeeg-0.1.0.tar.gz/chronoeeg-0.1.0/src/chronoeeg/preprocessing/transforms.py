"""Signal transformations and montage calculations."""

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


class BipolarMontage:
    """
    Calculate bipolar montage from monopolar EEG channels.

    Bipolar montage computes differences between adjacent electrode pairs,
    which can reduce common-mode noise and improve spatial localization.

    Parameters
    ----------
    bipolar_pairs : List[Tuple[str, str]]
        List of channel pairs (channel1, channel2) to compute differences

    Examples
    --------
    >>> pairs = [('Fp1', 'F3'), ('F3', 'C3'), ('C3', 'P3')]
    >>> montage = BipolarMontage(bipolar_pairs=pairs)
    >>> bipolar_data = montage.transform(monopolar_data)
    """

    # Standard 10-20 bipolar montages
    STANDARD_PAIRS = [
        ("Fp1", "F3"),
        ("Fp2", "F4"),
        ("F3", "C3"),
        ("F4", "C4"),
        ("C3", "P3"),
        ("C4", "P4"),
        ("P3", "O1"),
        ("P4", "O2"),
        ("F7", "T7"),
        ("F8", "T8"),
        ("T7", "P7"),
        ("T8", "P8"),
        ("Fz", "Cz"),
        ("Cz", "Pz"),
    ]

    def __init__(self, bipolar_pairs: List[Tuple[str, str]] = None):
        """Initialize bipolar montage calculator."""
        self.bipolar_pairs = bipolar_pairs or self.STANDARD_PAIRS
        self.pairs = self.bipolar_pairs  # Alias for backward compatibility

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform monopolar data to bipolar montage.

        Parameters
        ----------
        data : pd.DataFrame
            Monopolar EEG data

        Returns
        -------
        pd.DataFrame
            Bipolar montage data with channels named as "Ch1-Ch2"
        """
        bipolar_data = {}

        for ch1, ch2 in self.bipolar_pairs:
            if ch1 in data.columns and ch2 in data.columns:
                channel_name = f"{ch1}-{ch2}"
                bipolar_data[channel_name] = data[ch1] - data[ch2]

        return pd.DataFrame(bipolar_data)

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """Alias for transform method for backward compatibility."""
        return self.transform(data)

    def get_available_pairs(self, data: pd.DataFrame) -> List[Tuple[str, str]]:
        """
        Get list of bipolar pairs available in the data.

        Parameters
        ----------
        data : pd.DataFrame
            Monopolar EEG data

        Returns
        -------
        List[Tuple[str, str]]
            List of available channel pairs
        """
        available = []
        for ch1, ch2 in self.bipolar_pairs:
            if ch1 in data.columns and ch2 in data.columns:
                available.append((ch1, ch2))
        return available
