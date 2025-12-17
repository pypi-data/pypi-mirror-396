"""
EEG Data Loaders

This module provides loaders for various EEG data formats, with primary support
for WFDB format used in the I-CARE challenge dataset.
"""

import os
from typing import Dict, List, Optional, Tuple

import pandas as pd


class EEGDataLoader:
    """
    Loader for EEG data in various formats.

    Primary support for WFDB format with extensibility for other formats.

    Parameters
    ----------
    data_folder : str
        Path to the root folder containing EEG data
    format : str, optional
        Data format ('wfdb', 'edf', 'bdf'). Default is 'wfdb'

    Examples
    --------
    >>> loader = EEGDataLoader(data_folder="path/to/data")
    >>> eeg_data, metadata = loader.load_patient("patient_001")
    >>> print(f"Loaded {eeg_data.shape[0]} samples from {eeg_data.shape[1]} channels")
    """

    def __init__(self, data_folder: str, file_format: str = "wfdb"):
        """Initialize the EEG data loader."""
        self.data_folder = data_folder
        self.file_format = file_format

        if not os.path.exists(data_folder):
            raise FileNotFoundError(f"Data folder not found: {data_folder}")

    def find_patients(self) -> List[str]:
        """
        Find all patient IDs in the data folder.

        Returns
        -------
        List[str]
            List of patient identifiers
        """
        patient_ids = []
        for item in sorted(os.listdir(self.data_folder)):
            patient_folder = os.path.join(self.data_folder, item)
            if os.path.isdir(patient_folder) and not item.startswith("."):
                # Check if folder contains patient data (metadata file or .hea files)
                metadata_file = os.path.join(patient_folder, f"{item}.txt")
                has_metadata = os.path.isfile(metadata_file)
                has_recordings = any(f.endswith(".hea") for f in os.listdir(patient_folder))
                if has_metadata or has_recordings:
                    patient_ids.append(item)
        return patient_ids

    def list_recordings(self, patient_id: str) -> List[str]:
        """
        List all available recordings for a patient.

        Parameters
        ----------
        patient_id : str
            Patient identifier

        Returns
        -------
        List[str]
            List of recording names (without path or extension)

        Examples
        --------
        >>> loader = EEGDataLoader(data_folder="path/to/data")
        >>> recordings = loader.list_recordings("0284")
        >>> print(recordings)  # ['0284_001_004_ECG']
        """
        patient_folder = os.path.join(self.data_folder, patient_id)

        if not os.path.exists(patient_folder):
            raise FileNotFoundError(f"Patient folder not found: {patient_folder}")

        recordings = []
        for file_name in os.listdir(patient_folder):
            if file_name.endswith(".hea"):
                # Get base name without extension
                recording_name = os.path.splitext(file_name)[0]
                recordings.append(recording_name)

        return sorted(recordings)

    def load_patient(
        self, patient_id: str, recording_names: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Load EEG data and metadata for a specific patient.

        Parameters
        ----------
        patient_id : str
            Patient identifier
        recording_names : List[str], optional
            Specific recording names to load. If None, loads all recordings.
            Use list_recordings() to see available recordings.

        Returns
        -------
        eeg_data : pd.DataFrame
            EEG signal data with channels as columns
        metadata : Dict
            Patient metadata including demographics and recording info

        Raises
        ------
        FileNotFoundError
            If patient data is not found

        Examples
        --------
        >>> # Load all recordings
        >>> loader = EEGDataLoader(data_folder="path/to/data")
        >>> data, meta = loader.load_patient("0284")
        >>>
        >>> # Load specific recordings only
        >>> data, meta = loader.load_patient("0284", recording_names=["0284_001_004_ECG"])
        """
        patient_folder = os.path.join(self.data_folder, patient_id)

        if not os.path.exists(patient_folder):
            raise FileNotFoundError(f"Patient folder not found: {patient_folder}")

        # Load metadata
        metadata = self._load_metadata(patient_folder, patient_id)

        # Load recording data
        recording_files = self._find_recording_files(patient_folder, recording_names)
        eeg_data, recording_metadata = self._load_recordings(recording_files)

        # Merge recording metadata into patient metadata
        metadata.update(recording_metadata)

        # Add recording info to metadata
        metadata["num_recordings"] = len(recording_files)
        metadata["loaded_recordings"] = [os.path.basename(f) for f in recording_files]

        # Add default start time if not present (needed for epoch extraction)
        if "Start time" not in metadata and "start_time" not in metadata:
            from datetime import time

            metadata["start_time"] = time(0, 0, 0)

        return eeg_data, metadata

    def load_recording(self, record_path: str) -> Tuple[pd.DataFrame, Dict]:
        """
        Load a specific EEG recording file.

        Parameters
        ----------
        record_path : str
            Path to the recording file (without extension)

        Returns
        -------
        data : pd.DataFrame
            EEG signal data
        recording_metadata : Dict
            Recording-specific metadata (sampling rate, channels, etc.)
        """
        from chronoeeg.io.wfdb_reader import load_recording_data

        # Load WFDB data
        recording_data = load_recording_data(record_path)

        # Convert to DataFrame
        signals = recording_data["signals"]
        channels = recording_data["channels"]

        df = pd.DataFrame(signals, columns=channels)

        metadata = {
            "sampling_frequency": recording_data["sampling_frequency"],
            "num_samples": recording_data["num_samples"],
            "channels": channels,
            "record_name": recording_data["record_name"],
        }

        # Add timing information if available
        if recording_data.get("start_time"):
            metadata["Start time"] = recording_data["start_time"]
        if recording_data.get("end_time"):
            metadata["End time"] = recording_data["end_time"]
        if recording_data.get("utility_frequency"):
            metadata["utility_frequency"] = recording_data["utility_frequency"]

        return df, metadata

    def _load_metadata(self, patient_folder: str, patient_id: str) -> Dict:
        """Load patient metadata from text file."""
        metadata_file = os.path.join(patient_folder, f"{patient_id}.txt")

        metadata = {"patient_id": patient_id}

        if not os.path.exists(metadata_file):
            return metadata

        with open(metadata_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if ":" in line:
                    # Handle both "# Key: Value" and "Key: Value" formats
                    if line.startswith("#"):
                        line = line.lstrip("#").strip()
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    metadata[key] = value

        return metadata

    def _find_recording_files(
        self, patient_folder: str, recording_names: Optional[List[str]] = None
    ) -> List[str]:
        """Find recording files for a patient.

        Parameters
        ----------
        patient_folder : str
            Path to patient folder
        recording_names : List[str], optional
            Specific recording names to find. If None, finds all recordings.

        Returns
        -------
        List[str]
            List of full paths to recording files (without extension)
        """
        available_recordings = {}

        # Find all .hea files
        for file_name in os.listdir(patient_folder):
            if file_name.endswith(".hea"):
                # Get base name without extension (e.g., '0284_001_004_ECG')
                record_name = os.path.splitext(file_name)[0]
                record_path = os.path.join(patient_folder, record_name)
                available_recordings[record_name] = record_path

        # Filter by requested recording names if specified
        if recording_names:
            selected_recordings = []
            for rec_name in recording_names:
                if rec_name in available_recordings:
                    selected_recordings.append(available_recordings[rec_name])
                else:
                    # Try partial match (user might provide short name)
                    matches = [
                        path for name, path in available_recordings.items() if rec_name in name
                    ]
                    if matches:
                        selected_recordings.extend(matches)
                    else:
                        raise ValueError(
                            f"Recording '{rec_name}' not found. Available: {list(available_recordings.keys())}"
                        )
            return sorted(selected_recordings)
        else:
            return sorted(list(available_recordings.values()))

    def _load_recordings(self, recording_files: List[str]) -> Tuple[pd.DataFrame, Dict]:
        """Load multiple recording files and concatenate.

        Returns
        -------
        Tuple[pd.DataFrame, Dict]
            Concatenated data and merged recording metadata
        """
        all_data = []
        recording_metadata = {}

        for record_file in recording_files:
            data, rec_meta = self.load_recording(record_file)
            all_data.append(data)
            # Merge metadata from first recording (for timing info)
            if not recording_metadata:
                recording_metadata = rec_meta

        if all_data:
            return pd.concat(all_data, ignore_index=True), recording_metadata
        else:
            return pd.DataFrame(), {}


class MultiDatasetLoader:
    """
    Loader that can handle multiple EEG datasets with different formats.

    This loader provides a unified interface for loading from different
    EEG databases (I-CARE, TUH, CHBMIT, etc.)

    Parameters
    ----------
    dataset_type : str
        Type of dataset ('icare', 'tuh', 'chbmit', 'custom')
    config : Dict, optional
        Dataset-specific configuration

    Examples
    --------
    >>> loader = MultiDatasetLoader(dataset_type='icare', config={'data_path': 'data/'})
    >>> patients = loader.get_patient_list()
    """

    def __init__(self, dataset_type: str, config: Optional[Dict] = None):
        """Initialize multi-dataset loader."""
        self.dataset_type = dataset_type
        self.config = config or {}

        # Initialize appropriate loader based on dataset type
        if dataset_type == "icare":
            self.loader = EEGDataLoader(
                data_folder=self.config.get("data_path", "./data"), file_format="wfdb"
            )
        else:
            raise NotImplementedError(f"Dataset type '{dataset_type}' not yet supported")

    def load(self, identifier: str) -> Tuple[pd.DataFrame, Dict]:
        """
        Load data using dataset-specific identifier.

        Parameters
        ----------
        identifier : str
            Dataset-specific identifier (patient ID, record ID, etc.)

        Returns
        -------
        data : pd.DataFrame
            EEG signal data
        metadata : Dict
            Associated metadata
        """
        return self.loader.load_patient(identifier)

    def get_patient_list(self) -> List[str]:
        """Get list of all available patients/records."""
        return self.loader.find_patients()
