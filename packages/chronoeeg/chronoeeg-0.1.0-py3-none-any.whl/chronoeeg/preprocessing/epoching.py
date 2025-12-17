"""
Epoch Extraction and Segmentation

This module handles the extraction of fixed-length epochs from continuous
EEG recordings, with support for overlapping windows and temporal metadata.
"""

from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class EpochExtractor:
    """
    Extract fixed-length epochs from continuous EEG data.

    Parameters
    ----------
    epoch_duration : int
        Duration of each epoch in seconds (default: 300 for 5 minutes)
    overlap : float
        Overlap between consecutive epochs as fraction (0.0 to 1.0)
    sampling_rate : int
        Sampling rate in Hz
    align_to_clock : bool
        Whether to align epochs to clock times (e.g., :00, :05, :10).
        Only works for epoch durations >= 60 seconds that divide evenly into 60 minutes.
        Useful for clinical protocols requiring specific time alignment.
        Default: False (sequential epochs starting from sample 0)
    start_time : datetime, optional
        Reference start time for epoch alignment

    Examples
    --------
    >>> # Standard sequential epochs (most common)
    >>> extractor = EpochExtractor(epoch_duration=300, sampling_rate=128)
    >>> epochs = extractor.fit_transform(eeg_data)
    >>>
    >>> # Clock-aligned epochs for multi-day analysis
    >>> extractor = EpochExtractor(epoch_duration=300, sampling_rate=128, align_to_clock=True)
    >>> epochs = extractor.fit_transform(eeg_data, metadata)
    """

    def __init__(
        self,
        epoch_duration: int = 300,
        overlap: float = 0.0,
        sampling_rate: int = 128,
        align_to_clock: bool = False,
        start_time: Optional[datetime] = None,
    ):
        """Initialize epoch extractor."""
        self.epoch_duration = epoch_duration
        self.epoch_length = epoch_duration  # Backward compatibility
        self.overlap = overlap
        self.sampling_rate = sampling_rate
        self.align_to_clock = align_to_clock
        self.start_time = start_time

        self.samples_per_epoch = epoch_duration * sampling_rate
        self.step_size = int(self.samples_per_epoch * (1 - overlap))

    def extract(self, data: pd.DataFrame, metadata: Optional[Dict] = None) -> List[Dict]:
        """
        Extract epochs from continuous EEG data.

        Parameters
        ----------
        data : pd.DataFrame
            Continuous EEG data
        metadata : Dict, optional
            Metadata including start_time, end_time

        Returns
        -------
        List[Dict]
            List of epoch dictionaries, each containing:
            - 'data': pd.DataFrame (epoch data)
            - 'start_time': time object
            - 'end_time': time object
            - 'start_sample': int
            - 'end_sample': int
            - 'epoch_number': int
        """
        epochs = []

        # Extract timing information from metadata
        if metadata:
            start_time = self._parse_time(metadata.get("Start time"))
            end_time = self._parse_time(metadata.get("End time"))
        else:
            start_time = time(0, 0, 0)
            end_time = None

        # Calculate temporal boundaries
        if self.align_to_clock and start_time:
            time_segments = self._calculate_aligned_segments(start_time, end_time, data)
        else:
            time_segments = self._calculate_sequential_segments(data, start_time)

        # Extract epochs
        for idx, (seg_start, seg_end) in enumerate(time_segments):
            start_sample, end_sample = self._time_to_samples(data, seg_start, seg_end, start_time)

            # Check if we have enough samples
            if end_sample - start_sample < self.samples_per_epoch:
                continue

            # Ensure we don't exceed data bounds
            if end_sample > len(data):
                end_sample = len(data)
                start_sample = max(0, end_sample - self.samples_per_epoch)

            if start_sample >= 0 and end_sample <= len(data):
                epoch_data = data.iloc[start_sample:end_sample].copy()

                epochs.append(
                    {
                        "data": epoch_data,
                        "start_time": seg_start,
                        "end_time": seg_end,
                        "start_sample": start_sample,
                        "end_sample": end_sample,
                        "epoch_number": idx + 1,
                        "duration_seconds": self.epoch_length,
                    }
                )

        return epochs

    def _calculate_aligned_segments(
        self, start_time: time, end_time: Optional[time], data: pd.DataFrame
    ) -> List[Tuple[time, time]]:
        """
        Calculate epoch segments aligned to clock times.

        For 5-minute epochs, aligns to :00, :05, :10, etc.
        Falls back to sequential segmentation for sub-minute epochs.
        """
        # Clock alignment only works for epochs >= 60 seconds
        epoch_minutes = self.epoch_length // 60
        if epoch_minutes == 0:
            # For sub-minute epochs, use sequential segmentation instead
            return self._calculate_sequential_segments(data, start_time)

        # Convert to datetime for easier manipulation
        start_dt = datetime(2000, 1, 1, start_time.hour, start_time.minute, start_time.second)

        if end_time:
            end_dt = datetime(2000, 1, 1, end_time.hour, end_time.minute, end_time.second)
        else:
            # If no end time, create segments for 24 hours
            end_dt = start_dt + timedelta(days=1)

        # Align start to next multiple of epoch_length
        start_min = (start_dt.minute // epoch_minutes) * epoch_minutes

        if start_dt.minute % epoch_minutes != 0 or start_dt.second > 0:
            start_min += epoch_minutes

        if start_min >= 60:
            start_segment = datetime(2000, 1, 1, start_dt.hour + 1, 0, 0)
        else:
            start_segment = datetime(2000, 1, 1, start_dt.hour, start_min, 0)

        # Generate segments
        segments = []
        current = start_segment

        while current + timedelta(seconds=self.epoch_length) - timedelta(seconds=1) <= end_dt:
            seg_end = current + timedelta(seconds=self.epoch_length) - timedelta(seconds=1)
            segments.append(
                (
                    time(current.hour, current.minute, current.second),
                    time(seg_end.hour, seg_end.minute, seg_end.second),
                )
            )
            current += timedelta(seconds=self.epoch_length)

        return segments

    def _calculate_sequential_segments(
        self, data: pd.DataFrame, start_time: time
    ) -> List[Tuple[time, time]]:
        """Calculate non-aligned sequential segments."""
        segments = []
        total_samples = len(data)

        for start_sample in range(0, total_samples - self.samples_per_epoch + 1, self.step_size):
            end_sample = start_sample + self.samples_per_epoch

            # Calculate corresponding times
            start_seconds = start_sample / self.sampling_rate
            end_seconds = end_sample / self.sampling_rate

            seg_start = self._add_seconds_to_time(start_time, start_seconds)
            seg_end = self._add_seconds_to_time(start_time, end_seconds)

            segments.append((seg_start, seg_end))

        return segments

    def _time_to_samples(
        self, data: pd.DataFrame, seg_start: time, seg_end: time, recording_start: time
    ) -> Tuple[int, int]:
        """Convert time segment to sample indices."""
        start_seconds = self._time_diff_seconds(recording_start, seg_start)
        end_seconds = self._time_diff_seconds(recording_start, seg_end)

        start_sample = int(start_seconds * self.sampling_rate)
        end_sample = int(end_seconds * self.sampling_rate) + 1

        return start_sample, end_sample

    @staticmethod
    def _parse_time(time_str: Optional[str]) -> Optional[time]:
        """Parse time string in HH:MM:SS format."""
        if not time_str:
            return None

        try:
            hours, minutes, seconds = (int(x) for x in time_str.split(":"))
            return time(hours, minutes, seconds)
        except:
            return None

    @staticmethod
    def _time_diff_seconds(start: time, end: time) -> float:
        """Calculate difference between two time objects in seconds."""
        start_dt = datetime(2000, 1, 1, start.hour, start.minute, start.second)
        end_dt = datetime(2000, 1, 1, end.hour, end.minute, end.second)
        return (end_dt - start_dt).total_seconds()

    @staticmethod
    def _add_seconds_to_time(t: time, seconds: float) -> time:
        """Add seconds to a time object."""
        dt = datetime(2000, 1, 1, t.hour, t.minute, t.second)
        dt += timedelta(seconds=seconds)
        return time(dt.hour, dt.minute, dt.second)

    def fit_transform(self, X, y=None):
        """
        Extract epochs from continuous EEG data (sklearn compatible).

        Parameters
        ----------
        X : pd.DataFrame
            Continuous EEG data with shape (n_samples, n_channels)
        y : array-like, optional
            Target values (ignored)

        Returns
        -------
        pd.DataFrame
            Epoched data with columns: [channel1, channel2, ..., epoch_id]

        Examples
        --------
        >>> import pandas as pd
        >>> import numpy as np
        >>> data = pd.DataFrame(np.random.randn(12800, 4), columns=['C1', 'C2', 'C3', 'C4'])
        >>> epocher = EpochExtractor(epoch_duration=100, sampling_rate=128)
        >>> epochs = epocher.fit_transform(data)
        >>> print(epochs['epoch_id'].nunique())
        """
        if not isinstance(X, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")

        if X.empty:
            raise ValueError("Input DataFrame is empty")

        n_samples = len(X)
        epochs_list = []
        epoch_id = 0

        # Calculate number of epochs
        n_epochs = (n_samples - self.samples_per_epoch) // self.step_size + 1

        for i in range(n_epochs):
            start_idx = i * self.step_size
            end_idx = start_idx + self.samples_per_epoch

            if end_idx > n_samples:
                break

            # Extract epoch data
            epoch_data = X.iloc[start_idx:end_idx].copy()
            epoch_data["epoch_id"] = epoch_id

            epochs_list.append(epoch_data)
            epoch_id += 1

        if not epochs_list:
            raise ValueError(
                f"No epochs could be extracted. Data has {n_samples} samples, "
                f"need at least {self.samples_per_epoch} samples per epoch."
            )

        # Concatenate all epochs
        result = pd.concat(epochs_list, ignore_index=True)

        return result

    def fit(self, X, y=None):
        """
        Fit method for sklearn compatibility (no-op).

        Parameters
        ----------
        X : array-like
            Input data
        y : array-like, optional
            Target values (ignored)

        Returns
        -------
        self
            Returns self for method chaining
        """
        return self

    def transform(self, X):
        """
        Transform continuous data into epochs (sklearn compatible).

        Parameters
        ----------
        X : pd.DataFrame
            Continuous EEG data

        Returns
        -------
        pd.DataFrame
            Epoched data with epoch_id column
        """
        return self.fit_transform(X)


class EpochValidator:
    """
    Validate extracted epochs for quality and consistency.

    Parameters
    ----------
    min_valid_ratio : float
        Minimum ratio of valid (non-NaN) samples required
    """

    def __init__(self, min_valid_ratio: float = 0.5):
        """Initialize validator."""
        self.min_valid_ratio = min_valid_ratio

    def validate_epoch(self, epoch: Dict) -> Tuple[bool, str]:
        """
        Validate a single epoch.

        Returns
        -------
        is_valid : bool
            Whether epoch passes validation
        message : str
            Validation message
        """
        data = epoch["data"]

        # Check for empty data
        if data.empty:
            return False, "Empty epoch data"

        # Check valid data ratio
        valid_ratio = 1 - (data.isna().sum().sum() / data.size)
        if valid_ratio < self.min_valid_ratio:
            return False, f"Insufficient valid data: {valid_ratio:.2%}"

        return True, "Valid"
