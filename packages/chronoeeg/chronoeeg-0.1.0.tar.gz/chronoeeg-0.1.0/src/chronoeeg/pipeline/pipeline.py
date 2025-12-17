"""
End-to-End EEG Analysis Pipeline

Provides high-level interfaces for complete EEG analysis workflows.
"""

from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
from tqdm import tqdm

from chronoeeg.features import ClassicalFeatureExtractor, FMMFeatureExtractor
from chronoeeg.io import EEGDataLoader
from chronoeeg.preprocessing import EpochExtractor
from chronoeeg.quality import QualityAssessor


class EEGAnalysisPipeline:
    """
    End-to-end pipeline for EEG analysis.

    Combines data loading, preprocessing, quality assessment, and feature
    extraction into a single cohesive workflow.

    Parameters
    ----------
    epoch_duration : int
        Duration of epochs in seconds (default: 300). Alias: epoch_length.
    sampling_rate : int
        Sampling frequency in Hz (default: 128)
    quality_threshold : float
        Minimum quality score to include epoch (0-1, default: 0.7)
    extract_classical : bool
        Whether to extract classical features (default: True)
    extract_fmm : bool
        Whether to extract FMM features (default: True)
    n_fmm_components : int
        Number of FMM components (default: 10)
    n_jobs : int
        Number of parallel jobs (default: 1)

    Examples
    --------
    >>> pipeline = EEGAnalysisPipeline(
    ...     epoch_duration=300,
    ...     quality_threshold=0.7,
    ...     extract_classical=True,
    ...     extract_fmm=True
    ... )
    >>> results = pipeline.process(eeg_data)
    >>> print(f"Features: {results['features'].shape}")
    """

    def __init__(
        self,
        epoch_duration: int = 300,
        epoch_length: Optional[int] = None,  # Backward compatibility
        sampling_rate: int = 128,
        quality_threshold: float = 0.7,
        extract_classical: bool = True,
        extract_fmm: bool = True,
        feature_types: Optional[List[str]] = None,  # Backward compatibility
        n_fmm_components: int = 10,
        n_jobs: int = 1,
    ):
        """Initialize analysis pipeline."""
        # Handle both epoch_duration and epoch_length
        if epoch_length is not None:
            epoch_duration = epoch_length

        self.epoch_duration = epoch_duration
        self.epoch_length = epoch_duration  # Backward compatibility
        self.sampling_rate = sampling_rate
        self.quality_threshold = quality_threshold
        self.n_fmm_components = n_fmm_components
        self.n_jobs = n_jobs

        # Handle feature types
        if feature_types is not None:
            extract_classical = "classical" in feature_types
            extract_fmm = "fmm" in feature_types

        self.extract_classical = extract_classical
        self.extract_fmm = extract_fmm

        # Initialize components
        self.loader = None
        self.epoch_extractor = EpochExtractor(
            epoch_duration=epoch_duration, sampling_rate=sampling_rate
        )
        self.quality_assessor = QualityAssessor(sampling_rate=sampling_rate)

        # Initialize feature extractors
        self.extractors = {}
        if extract_classical:
            self.extractors["classical"] = ClassicalFeatureExtractor(sampling_rate)
        if extract_fmm:
            self.extractors["fmm"] = FMMFeatureExtractor(
                n_components=n_fmm_components, sampling_rate=sampling_rate
            )

    def fit_transform(self, data_folder: str, labels_file: Optional[str] = None) -> Dict:
        """
        Run complete analysis pipeline on dataset.

        Parameters
        ----------
        data_folder : str
            Path to folder containing EEG data
        labels_file : str, optional
            Path to CSV file with labels

        Returns
        -------
        Dict
            Results dictionary containing:
            - 'features': pd.DataFrame of extracted features
            - 'labels': pd.Series of labels (if provided)
            - 'quality': pd.DataFrame of quality scores
            - 'metadata': pd.DataFrame of epoch metadata
        """
        # Initialize loader
        self.loader = EEGDataLoader(data_folder=data_folder)

        # Find all patients
        patient_ids = self.loader.find_patients()

        print(f"Processing {len(patient_ids)} patients...")

        all_features = []
        all_quality = []
        all_metadata = []

        for patient_id in tqdm(patient_ids, desc="Processing patients"):
            # Load patient data
            eeg_data, metadata = self.loader.load_patient(patient_id)

            # Extract epochs
            epochs = self.epoch_extractor.extract(eeg_data, metadata)

            # Process each epoch
            for epoch in epochs:
                # Assess quality
                quality = self.quality_assessor.assess(
                    epoch["data"],
                    patient_id=patient_id,
                    start_time=epoch["start_time"],
                    end_time=epoch["end_time"],
                )

                # Skip low-quality epochs
                if quality["overall_quality"] < self.quality_threshold:
                    continue

                # Extract features
                features = self._extract_features(epoch["data"])

                # Add metadata
                features["patient_id"] = patient_id
                features["epoch_number"] = epoch["epoch_number"]

                all_features.append(features)
                all_quality.append(quality)
                all_metadata.append(
                    {
                        "patient_id": patient_id,
                        "epoch_number": epoch["epoch_number"],
                        "start_time": epoch["start_time"],
                        "end_time": epoch["end_time"],
                    }
                )

        # Combine results
        features_df = pd.concat(all_features, ignore_index=True)
        quality_df = pd.DataFrame(all_quality)
        metadata_df = pd.DataFrame(all_metadata)

        # Load labels if provided
        labels = None
        if labels_file:
            labels_data = pd.read_csv(labels_file)
            labels = features_df["patient_id"].map(labels_data.set_index("patient_id")["label"])

        return {
            "features": features_df,
            "labels": labels,
            "quality": quality_df,
            "metadata": metadata_df,
        }

    def process(self, data: pd.DataFrame) -> Dict:
        """
        Process EEG data through the complete pipeline.

        Parameters
        ----------
        data : pd.DataFrame
            Continuous EEG data with shape (n_samples, n_channels)

        Returns
        -------
        Dict
            Results dictionary containing:
            - 'epochs': pd.DataFrame of epoched data
            - 'quality': pd.DataFrame of quality scores per epoch
            - 'features': pd.DataFrame of extracted features per epoch

        Examples
        --------
        >>> import pandas as pd
        >>> import numpy as np
        >>> data = pd.DataFrame(np.random.randn(38400, 6))  # 5 min at 128 Hz
        >>> pipeline = EEGAnalysisPipeline(epoch_duration=300)
        >>> results = pipeline.process(data)
        >>> print(results['features'].shape)
        """
        # Step 1: Extract epochs
        epochs = self.epoch_extractor.fit_transform(data)

        # Step 2: Assess quality
        quality = self.quality_assessor.assess(epochs, epoch_column="epoch_id")

        # Step 3: Extract features from each good epoch
        all_features = []

        for epoch_id in quality["epoch_id"]:
            # Get epoch data
            epoch_data = epochs[epochs["epoch_id"] == epoch_id]
            epoch_data = epoch_data.drop(columns=["epoch_id"])

            # Extract features
            epoch_features = self._extract_features(epoch_data)
            epoch_features["epoch_id"] = epoch_id

            all_features.append(epoch_features)

        # Combine features
        if all_features:
            features_df = pd.concat(all_features, ignore_index=True)
        else:
            features_df = pd.DataFrame()

        return {"epochs": epochs, "quality": quality, "features": features_df}

    def _extract_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract all configured features from an epoch."""
        features = pd.DataFrame()

        for feature_type, extractor in self.extractors.items():
            extracted = extractor.extract(data)

            # Prefix column names with feature type
            if feature_type != "classical":  # Classical already has prefixes
                extracted = extracted.add_prefix(f"{feature_type}_")

            features = pd.concat([features, extracted], axis=1)

        return features
