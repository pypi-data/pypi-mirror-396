"""
Quality Assessment

Main interface for EEG signal quality assessment.
"""

from datetime import time
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from chronoeeg.quality import metrics


class QualityAssessor:
    """
    Assess EEG signal quality across multiple dimensions.

    Evaluates signal quality using multiple metrics:
    - NaN ratio: Proportion of missing data
    - Gap quality: Longest continuous valid segment
    - Outlier quality: Presence of extreme values
    - Flatline quality: Detection of constant segments
    - Sharpness quality: Detection of sharp transitions/artifacts
    - Cohesion quality: Phase-locking across channels

    Parameters
    ----------
    sampling_rate : int
        Sampling frequency in Hz (default: 128)
    nan_threshold : float
        Threshold for NaN quality (default: 0.15)
    gap_threshold : float
        Threshold for gap quality (default: 0.10)
    outlier_threshold : float
        Threshold for outlier quality (default: 0.05)
    flatline_threshold : float
        Threshold for flatline quality (default: 0.05)
    sharpness_threshold : float
        Threshold for sharpness quality (default: 0.10)
    cohesion_threshold : float
        Threshold for cohesion quality (default: 0.70)

    Examples
    --------
    >>> assessor = QualityAssessor(sampling_rate=128)
    >>> epochs_df = pd.DataFrame(...)  # Epoched data with 'epoch_id' column
    >>> quality = assessor.assess(epochs_df, epoch_column='epoch_id')
    >>> print(f"Good epochs: {quality['passes_threshold'].sum()}/{len(quality)}")
    """

    def __init__(
        self,
        sampling_rate: int = 128,
        nan_threshold: float = 0.15,
        gap_threshold: float = 0.10,
        outlier_threshold: float = 0.05,
        flatline_threshold: float = 0.05,
        sharpness_threshold: float = 0.10,
        cohesion_threshold: float = 0.70,
    ):
        """Initialize quality assessor."""
        self.sampling_rate = sampling_rate
        self.nan_threshold = nan_threshold
        self.gap_threshold = gap_threshold
        self.outlier_threshold = outlier_threshold
        self.flatline_threshold = flatline_threshold
        self.sharpness_threshold = sharpness_threshold
        self.cohesion_threshold = cohesion_threshold

    def assess(
        self,
        data: pd.DataFrame,
        patient_id: Optional[str] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
        epoch_column: Optional[str] = None,
    ):
        """
        Assess quality of EEG data or epoched data.

        Parameters
        ----------
        data : pd.DataFrame
            EEG data to assess. Can be continuous or epoched data.
        patient_id : str, optional
            Patient identifier
        start_time : time, optional
            Start time of segment
        end_time : time, optional
            End time of segment
        epoch_column : str, optional
            If provided, treats data as epoched and assesses each epoch separately.
            Returns a DataFrame with one row per epoch.

        Returns
        -------
        Dict or pd.DataFrame
            If epoch_column is None: Returns quality metrics dictionary
            If epoch_column is specified: Returns DataFrame with quality metrics per epoch

        Examples
        --------
        >>> # Assess single segment
        >>> assessor = QualityAssessor()
        >>> quality = assessor.assess(eeg_data)
        >>>
        >>> # Assess epoched data
        >>> epochs = pd.DataFrame(...)  # with 'epoch_id' column
        >>> quality_df = assessor.assess(epochs, epoch_column='epoch_id')
        """
        if epoch_column is not None:
            # Assess each epoch separately
            return self.assess_epochs_df(data, epoch_column)
        else:
            # Assess single segment
            return self.assess_single_segment(data, patient_id, start_time, end_time)

    def assess_single_segment(
        self,
        data: pd.DataFrame,
        patient_id: Optional[str] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None,
    ) -> Dict:
        """
        Assess quality of a single EEG segment.

        Parameters
        ----------
        data : pd.DataFrame
            EEG data to assess
        patient_id : str, optional
            Patient identifier
        start_time : time, optional
            Start time of segment
        end_time : time, optional
            End time of segment

        Returns
        -------
        Dict
            Quality metrics dictionary
        """
        quality_scores = {
            "patient_id": patient_id,
            "start_time": start_time,
            "end_time": end_time,
        }

        # Calculate individual quality metrics
        quality_scores["nan_score"] = metrics.calculate_nan_quality(data)
        quality_scores["gap_score"] = metrics.calculate_gap_quality(data)
        quality_scores["outlier_score"] = metrics.calculate_outlier_quality(data, threshold=2.0)
        quality_scores["flatline_score"] = metrics.calculate_flatline_quality(
            data, self.sampling_rate
        )
        quality_scores["sharpness_score"] = metrics.calculate_sharpness_quality(
            data, amplitude_threshold=0.05
        )
        quality_scores["cohesion_score"] = metrics.calculate_cohesion_quality(data)

        # Calculate overall quality (weighted average)
        quality_scores["overall_quality"] = self._calculate_overall_quality(quality_scores)

        # Determine if passes threshold
        quality_scores["passes_threshold"] = self._passes_thresholds(quality_scores)

        return quality_scores

    def assess_epochs_df(
        self, epochs: pd.DataFrame, epoch_column: str = "epoch_id"
    ) -> pd.DataFrame:
        """
        Assess quality of epoched data.

        Parameters
        ----------
        epochs : pd.DataFrame
            Epoched EEG data with epoch identifier column
        epoch_column : str
            Name of column containing epoch identifiers

        Returns
        -------
        pd.DataFrame
            Quality metrics for each epoch
        """
        epoch_ids = epochs[epoch_column].unique()
        quality_results = []

        for epoch_id in epoch_ids:
            # Get data for this epoch
            epoch_data = epochs[epochs[epoch_column] == epoch_id]
            epoch_data = epoch_data.drop(columns=[epoch_column])

            # Assess quality
            quality = self.assess_single_segment(epoch_data)
            quality["epoch_id"] = epoch_id
            quality_results.append(quality)

        return pd.DataFrame(quality_results)

    def _passes_thresholds(self, quality_scores: Dict) -> bool:
        """Check if quality scores pass all thresholds."""
        return (
            quality_scores["nan_score"] >= (1 - self.nan_threshold) * 100
            and quality_scores["gap_score"] >= (1 - self.gap_threshold) * 100
            and quality_scores["outlier_score"] >= (1 - self.outlier_threshold) * 100
            and quality_scores["flatline_score"] >= (1 - self.flatline_threshold) * 100
            and quality_scores["sharpness_score"] >= (1 - self.sharpness_threshold) * 100
            and quality_scores["cohesion_score"] >= self.cohesion_threshold * 100
        )

    def assess_epochs(self, epochs: List[Dict]) -> List[Dict]:
        """
        Assess quality of multiple epochs.

        Parameters
        ----------
        epochs : List[Dict]
            List of epoch dictionaries from EpochExtractor

        Returns
        -------
        List[Dict]
            List of quality assessment dictionaries
        """
        results = []

        for epoch in epochs:
            quality = self.assess(
                data=epoch["data"],
                patient_id=epoch.get("patient_id"),
                start_time=epoch.get("start_time"),
                end_time=epoch.get("end_time"),
            )
            results.append(quality)

        return results

    @staticmethod
    def _calculate_overall_quality(quality_scores: Dict) -> float:
        """
        Calculate overall quality score as weighted average.

        Parameters
        ----------
        quality_scores : Dict
            Individual quality metrics

        Returns
        -------
        float
            Overall quality score (0-100)
        """
        weights = {
            "nan_score": 0.25,
            "gap_score": 0.15,
            "outlier_score": 0.20,
            "flatline_score": 0.15,
            "sharpness_score": 0.15,
            "cohesion_score": 0.10,
        }

        overall = sum(quality_scores.get(metric, 0) * weight for metric, weight in weights.items())

        return overall
