"""
Tests for Preprocessing Functionality

Tests for signal filtering, epoching, and transformations.
"""

import numpy as np
import pandas as pd
import pytest

from chronoeeg.preprocessing import BipolarMontage, EpochExtractor, SignalFilter


class TestSignalFilter:
    """Tests for SignalFilter class."""

    def test_initialization(self):
        """Test filter initialization."""
        filt = SignalFilter(sampling_rate=128)
        assert filt.sampling_rate == 128

    def test_bandpass_filter(self, sample_eeg_data):
        """Test bandpass filtering."""
        filt = SignalFilter(sampling_rate=128)
        filtered = filt.bandpass(sample_eeg_data, lowcut=0.5, highcut=40.0)

        assert filtered.shape == sample_eeg_data.shape
        assert isinstance(filtered, pd.DataFrame)

    def test_notch_filter(self, sample_eeg_data):
        """Test notch filtering."""
        filt = SignalFilter(sampling_rate=128)
        filtered = filt.notch(sample_eeg_data, freq=50.0)

        assert filtered.shape == sample_eeg_data.shape
        assert isinstance(filtered, pd.DataFrame)

    def test_lowpass_filter(self, sample_eeg_data):
        """Test lowpass filtering."""
        filt = SignalFilter(sampling_rate=128)
        filtered = filt.lowpass(sample_eeg_data, cutoff=40.0)

        assert filtered.shape == sample_eeg_data.shape

    def test_highpass_filter(self, sample_eeg_data):
        """Test highpass filtering."""
        filt = SignalFilter(sampling_rate=128)
        filtered = filt.highpass(sample_eeg_data, cutoff=0.5)

        assert filtered.shape == sample_eeg_data.shape


class TestEpochExtractor:
    """Tests for EpochExtractor class."""

    def test_initialization(self):
        """Test epoch extractor initialization."""
        extractor = EpochExtractor(epoch_duration=300, sampling_rate=128)

        assert extractor.epoch_duration == 300
        assert extractor.sampling_rate == 128
        assert extractor.samples_per_epoch == 300 * 128

    def test_extract_with_metadata(self, sample_eeg_data, sample_metadata):
        """Test epoch extraction with metadata."""
        extractor = EpochExtractor(epoch_duration=60, sampling_rate=128)
        epochs = extractor.extract(sample_eeg_data, sample_metadata)

        assert isinstance(epochs, list)
        if len(epochs) > 0:
            assert "data" in epochs[0]
            assert isinstance(epochs[0]["data"], pd.DataFrame)

    def test_extract_without_metadata(self, sample_eeg_data):
        """Test epoch extraction without metadata."""
        extractor = EpochExtractor(epoch_duration=60, sampling_rate=128)
        epochs = extractor.extract(sample_eeg_data, metadata=None)

        assert isinstance(epochs, list)


class TestBipolarMontage:
    """Tests for BipolarMontage class."""

    def test_initialization(self):
        """Test bipolar montage initialization."""
        pairs = [("Fp1", "F3"), ("Fp2", "F4")]
        montage = BipolarMontage(pairs)

        assert montage.pairs == pairs

    def test_apply_montage(self):
        """Test applying bipolar montage."""
        # Create sample data with named channels
        np.random.seed(42)
        data = pd.DataFrame(
            {
                "Fp1": np.random.randn(1000),
                "Fp2": np.random.randn(1000),
                "F3": np.random.randn(1000),
                "F4": np.random.randn(1000),
            }
        )

        pairs = [("Fp1", "F3"), ("Fp2", "F4")]
        montage = BipolarMontage(pairs)

        result = montage.apply(data)

        assert isinstance(result, pd.DataFrame)
        assert len(result.columns) == 2
        assert "Fp1-F3" in result.columns
        assert "Fp2-F4" in result.columns
