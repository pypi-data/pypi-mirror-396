"""
Test Configuration and Fixtures

Common pytest fixtures and configuration for all tests.
"""

from datetime import time

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_eeg_data():
    """Generate sample EEG data for testing."""
    np.random.seed(42)
    n_samples = 38400  # 5 minutes at 128 Hz
    n_channels = 18

    data = pd.DataFrame(
        np.random.randn(n_samples, n_channels), columns=[f"Ch{i+1}" for i in range(n_channels)]
    )
    return data


@pytest.fixture
def sample_metadata():
    """Generate sample metadata for testing."""
    return {
        "Patient ID": "TEST001",
        "Age": "65",
        "Sex": "Male",
        "Start time": "10:00:00",
        "End time": "10:05:00",
        "Hospital": "A",
    }


@pytest.fixture
def sample_epoch():
    """Generate a sample epoch dictionary."""
    np.random.seed(42)
    n_samples = 1280  # 10 seconds at 128 Hz
    n_channels = 18

    data = pd.DataFrame(
        np.random.randn(n_samples, n_channels), columns=[f"Ch{i+1}" for i in range(n_channels)]
    )

    return {
        "data": data,
        "start_time": time(10, 0, 0),
        "end_time": time(10, 0, 10),
        "start_sample": 0,
        "end_sample": 1280,
        "epoch_number": 1,
        "duration_seconds": 10,
    }


@pytest.fixture
def bipolar_pairs():
    """Standard bipolar montage pairs."""
    return [
        ("Fp1", "F3"),
        ("Fp2", "F4"),
        ("F3", "C3"),
        ("F4", "C4"),
        ("C3", "P3"),
        ("C4", "P4"),
        ("P3", "O1"),
        ("P4", "O2"),
    ]
