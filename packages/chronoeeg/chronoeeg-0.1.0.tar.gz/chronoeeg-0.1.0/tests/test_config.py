"""
Tests for configuration module.
"""

from pathlib import Path

import pytest

from chronoeeg.config import (
    ChronoEEGConfig,
    FeatureConfig,
    PreprocessingConfig,
    QualityConfig,
    get_config,
    set_config,
)
from chronoeeg.exceptions import ConfigurationError


class TestQualityConfig:
    """Test quality configuration."""

    def test_default_values(self):
        """Test default quality thresholds."""
        config = QualityConfig()
        assert config.nan_threshold == 0.15
        assert config.gap_threshold == 0.10
        assert 0 <= config.cohesion_threshold <= 1

    def test_invalid_threshold(self):
        """Test validation of invalid thresholds."""
        with pytest.raises(ValueError):
            QualityConfig(nan_threshold=1.5)  # > 1

        with pytest.raises(ValueError):
            QualityConfig(gap_threshold=-0.1)  # < 0

    def test_custom_values(self):
        """Test custom threshold values."""
        config = QualityConfig(
            nan_threshold=0.20,
            gap_threshold=0.15,
        )
        assert config.nan_threshold == 0.20
        assert config.gap_threshold == 0.15


class TestPreprocessingConfig:
    """Test preprocessing configuration."""

    def test_default_values(self):
        """Test default preprocessing parameters."""
        config = PreprocessingConfig()
        assert config.epoch_duration == 300
        assert config.sampling_rate == 128
        assert config.overlap == 0.0

    def test_filter_parameters(self):
        """Test filter configuration."""
        config = PreprocessingConfig(
            lowcut=0.5,
            highcut=40.0,
            notch_freq=50.0,
        )
        assert config.lowcut == 0.5
        assert config.highcut == 40.0
        assert config.notch_freq == 50.0

    def test_invalid_epoch_duration(self):
        """Test invalid epoch duration."""
        with pytest.raises(ValueError):
            PreprocessingConfig(epoch_duration=0)

        with pytest.raises(ValueError):
            PreprocessingConfig(epoch_duration=-10)

    def test_invalid_overlap(self):
        """Test invalid overlap value."""
        with pytest.raises(ValueError):
            PreprocessingConfig(overlap=1.5)

        with pytest.raises(ValueError):
            PreprocessingConfig(overlap=-0.1)

    def test_invalid_filter_range(self):
        """Test invalid filter frequency range."""
        with pytest.raises(ValueError):
            PreprocessingConfig(lowcut=40.0, highcut=0.5)  # lowcut > highcut


class TestFeatureConfig:
    """Test feature extraction configuration."""

    def test_default_values(self):
        """Test default feature parameters."""
        config = FeatureConfig()
        assert config.n_components == 10
        assert config.extract_entropy is True
        assert config.extract_fmm is True

    def test_frequency_bands(self):
        """Test frequency band configuration."""
        config = FeatureConfig()
        assert "delta" in config.freq_bands
        assert "alpha" in config.freq_bands
        assert config.freq_bands["delta"] == (0.5, 4.0)

    def test_custom_frequency_bands(self):
        """Test custom frequency bands."""
        custom_bands = {
            "slow": (0.5, 10.0),
            "fast": (10.0, 40.0),
        }
        config = FeatureConfig(freq_bands=custom_bands)
        assert config.freq_bands == custom_bands

    def test_invalid_components(self):
        """Test invalid number of components."""
        with pytest.raises(ValueError):
            FeatureConfig(n_components=0)

        with pytest.raises(ValueError):
            FeatureConfig(n_components=-5)


class TestChronoEEGConfig:
    """Test main configuration class."""

    def test_default_config(self):
        """Test default configuration creation."""
        config = ChronoEEGConfig()
        assert config.preprocessing.sampling_rate == 128
        assert config.quality.nan_threshold == 0.15
        assert config.features.n_components == 10

    def test_nested_config(self):
        """Test nested configuration access."""
        config = ChronoEEGConfig()
        assert hasattr(config, "quality")
        assert hasattr(config, "preprocessing")
        assert hasattr(config, "features")

    def test_directory_creation(self):
        """Test that directories are created."""
        config = ChronoEEGConfig()
        assert config.data_dir.exists()
        assert config.output_dir.exists()
        assert config.cache_dir.exists()

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = ChronoEEGConfig()
        config_dict = config.to_dict()

        assert "quality" in config_dict
        assert "preprocessing" in config_dict
        assert "features" in config_dict
        assert "random_seed" in config_dict

    def test_from_dict(self):
        """Test creation from dictionary."""
        config_dict = {
            "quality": {"nan_threshold": 0.20},
            "preprocessing": {"sampling_rate": 256},
            "features": {"n_components": 15},
            "random_seed": 123,
        }

        config = ChronoEEGConfig.from_dict(config_dict)
        assert config.quality.nan_threshold == 0.20
        assert config.preprocessing.sampling_rate == 256
        assert config.features.n_components == 15
        assert config.random_seed == 123

    def test_get_set_config(self):
        """Test global config getter/setter."""
        original_config = get_config()

        new_config = ChronoEEGConfig()
        new_config.preprocessing.sampling_rate = 256

        set_config(new_config)
        retrieved_config = get_config()

        assert retrieved_config.preprocessing.sampling_rate == 256

        # Restore original
        set_config(original_config)


class TestConfigSerialization:
    """Test configuration serialization."""

    def test_save_load_yaml(self, tmp_path):
        """Test saving and loading YAML configuration."""
        pytest.importorskip("yaml")  # Skip if PyYAML not installed

        config = ChronoEEGConfig()
        config.preprocessing.sampling_rate = 256
        config.quality.nan_threshold = 0.25

        yaml_file = tmp_path / "config.yaml"
        config.save_to_yaml(yaml_file)

        assert yaml_file.exists()

        loaded_config = ChronoEEGConfig.load_from_yaml(yaml_file)
        assert loaded_config.preprocessing.sampling_rate == 256
        assert loaded_config.quality.nan_threshold == 0.25
