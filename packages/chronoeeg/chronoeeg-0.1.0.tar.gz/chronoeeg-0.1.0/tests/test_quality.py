"""
Tests for Quality Assessment

Tests for quality metrics and assessors.
"""

import numpy as np
import pandas as pd
import pytest

from chronoeeg.quality import QualityAssessor, metrics


class TestQualityMetrics:
    """Tests for individual quality metrics."""

    def test_nan_quality(self):
        """Test NaN quality metric."""
        # Data with no NaNs
        data_clean = pd.DataFrame(np.random.randn(1000, 4))
        quality = metrics.calculate_nan_quality(data_clean)
        assert quality == 100.0  # 0-100 scale

        # Data with some NaNs
        data_nans = data_clean.copy()
        data_nans.iloc[:100, 0] = np.nan
        quality = metrics.calculate_nan_quality(data_nans)
        assert 0 < quality < 100.0  # 0-100 scale

    def test_gap_quality(self):
        """Test gap quality metric."""
        data = pd.DataFrame(np.random.randn(1000, 4))
        quality = metrics.calculate_gap_quality(data)
        assert 0 <= quality <= 100.0  # 0-100 scale

    def test_outlier_quality(self):
        """Test outlier quality metric."""
        data = pd.DataFrame(np.random.randn(1000, 4))
        quality = metrics.calculate_outlier_quality(data, threshold=3.0)
        assert 0 <= quality <= 100.0  # 0-100 scale

    def test_flatline_quality(self):
        """Test flatline quality metric."""
        data = pd.DataFrame(np.random.randn(1000, 4))
        quality = metrics.calculate_flatline_quality(data, sampling_rate=128)
        assert 0 <= quality <= 100.0  # 0-100 scale

    def test_cohesion_quality(self):
        """Test cohesion quality metric."""
        data = pd.DataFrame(np.random.randn(1000, 4))
        quality = metrics.calculate_cohesion_quality(data)
        assert quality >= 0  # Cohesion can vary widely


class TestQualityAssessor:
    """Tests for QualityAssessor class."""

    def test_initialization(self):
        """Test quality assessor initialization."""
        qa = QualityAssessor(sampling_rate=128)
        assert qa.sampling_rate == 128

    def test_assess_clean_data(self, sample_eeg_data):
        """Test quality assessment of clean data."""
        qa = QualityAssessor(sampling_rate=128)
        quality = qa.assess(sample_eeg_data)

        assert isinstance(quality, dict)
        assert "overall_quality" in quality
        assert 0 <= quality["overall_quality"] <= 100.0

    def test_assess_with_nans(self):
        """Test quality assessment with NaN values."""
        data = pd.DataFrame(np.random.randn(1000, 4))
        data.iloc[:500, 0] = np.nan

        qa = QualityAssessor(sampling_rate=128)
        quality = qa.assess(data)

        assert isinstance(quality, dict)
        assert quality["overall_quality"] < 100.0

    def test_quality_metrics_present(self, sample_eeg_data):
        """Test that all expected metrics are present."""
        qa = QualityAssessor(sampling_rate=128)
        quality = qa.assess(sample_eeg_data)

        expected_metrics = [
            "overall_quality",
            "nan_score",
            "gap_score",
            "outlier_score",
            "flatline_score",
            "sharpness_score",
            "cohesion_score",
        ]

        for metric in expected_metrics:
            assert metric in quality, f"Missing metric: {metric}"
