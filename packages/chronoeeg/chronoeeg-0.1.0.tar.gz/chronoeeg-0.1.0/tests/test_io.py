"""
Tests for Data Loading Functionality

Ensures that data loaders correctly read and validate EEG data.
"""

import numpy as np
import pandas as pd
import pytest

from chronoeeg.io import DataValidator, EEGDataLoader


class TestDataValidator:
    """Tests for DataValidator class."""

    def test_validate_empty_dataframe(self):
        """Test validation of empty DataFrame."""
        validator = DataValidator()
        empty_df = pd.DataFrame()

        is_valid, issues = validator.validate_dataframe(empty_df)

        assert not is_valid
        assert "empty" in issues[0].lower()

    def test_validate_valid_dataframe(self, sample_eeg_data):
        """Test validation of valid DataFrame."""
        validator = DataValidator()

        is_valid, issues = validator.validate_dataframe(sample_eeg_data)

        assert is_valid
        assert len(issues) == 0

    def test_validate_high_nan_ratio(self, sample_eeg_data):
        """Test validation with high NaN ratio."""
        validator = DataValidator()

        # Introduce many NaNs
        data_with_nans = sample_eeg_data.copy()
        mask = np.random.rand(*data_with_nans.shape) < 0.6
        data_with_nans = data_with_nans.mask(mask)

        is_valid, issues = validator.validate_dataframe(data_with_nans)

        assert not is_valid
        assert any("NaN" in issue for issue in issues)

    def test_validate_constant_channels(self):
        """Test detection of constant channels."""
        validator = DataValidator()

        data = pd.DataFrame(
            {
                "Ch1": np.random.randn(100),
                "Ch2": np.ones(100),  # Constant channel
                "Ch3": np.random.randn(100),
            }
        )

        is_valid, issues = validator.validate_dataframe(data)

        assert not is_valid
        assert any("constant" in issue.lower() for issue in issues)


class TestEEGDataLoader:
    """Tests for EEGDataLoader class."""

    def test_initialization_invalid_folder(self):
        """Test initialization with non-existent folder."""
        with pytest.raises(FileNotFoundError):
            EEGDataLoader(data_folder="/nonexistent/path")

    def test_validate_input_conversion(self):
        """Test input validation and conversion."""
        from chronoeeg.features.base import BaseFeatureExtractor

        class DummyExtractor(BaseFeatureExtractor):
            def extract(self, data):
                return self._validate_input(data)

        extractor = DummyExtractor()

        # Test numpy array conversion
        np_data = np.random.randn(100, 5)
        df = extractor._validate_input(np_data)

        assert isinstance(df, pd.DataFrame)
        assert df.shape == np_data.shape

    def test_validate_input_empty(self):
        """Test validation of empty input."""
        from chronoeeg.features.base import BaseFeatureExtractor

        class DummyExtractor(BaseFeatureExtractor):
            def extract(self, data):
                return self._validate_input(data)

        extractor = DummyExtractor()

        with pytest.raises(ValueError, match="empty"):
            extractor._validate_input(pd.DataFrame())
