"""
Tests for visualization module.
"""

import numpy as np
import pandas as pd
import pytest

# Check if visualization dependencies are available
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-interactive backend
    import matplotlib.pyplot as plt

    from chronoeeg.visualization.plots import (
        plot_epochs,
        plot_fmm_components,
        plot_quality_metrics,
        plot_signal,
    )

    HAS_VIZ = True
except ImportError:
    HAS_VIZ = False


@pytest.mark.skipif(not HAS_VIZ, reason="Visualization dependencies not installed")
class TestVisualization:
    """Test visualization functions."""

    @pytest.fixture
    def sample_signal(self):
        """Create sample EEG signal."""
        np.random.seed(42)
        n_samples = 1280  # 10 seconds at 128 Hz
        n_channels = 4
        data = np.random.randn(n_samples, n_channels) * 50
        channels = ["Fp1", "Fp2", "F3", "F4"]
        return pd.DataFrame(data, columns=channels)

    @pytest.fixture
    def sample_epochs(self):
        """Create sample epoched data."""
        np.random.seed(42)
        epochs_list = []
        for epoch_id in range(3):
            data = np.random.randn(100, 4) * 50
            df = pd.DataFrame(data, columns=["Fp1", "Fp2", "F3", "F4"])
            df["epoch_id"] = epoch_id
            epochs_list.append(df)
        return pd.concat(epochs_list, ignore_index=True)

    @pytest.fixture
    def sample_quality(self):
        """Create sample quality scores."""
        return pd.DataFrame(
            {
                "epoch_id": [0, 1, 2],
                "nan_score": [0.95, 0.88, 0.92],
                "gap_score": [0.98, 0.85, 0.90],
                "outlier_score": [0.93, 0.89, 0.95],
                "flatline_score": [0.97, 0.91, 0.94],
                "sharpness_score": [0.96, 0.87, 0.93],
                "cohesion_score": [0.85, 0.78, 0.82],
            }
        )

    @pytest.fixture
    def sample_fmm(self):
        """Create sample FMM parameters."""
        return pd.DataFrame(
            {
                "Wave": range(1, 6),
                "FMM_R2": [0.25, 0.18, 0.15, 0.12, 0.08],
                "FMM_α": [0.5, 0.3, 0.7, 0.4, 0.6],
                "FMM_ω": [8.5, 10.2, 6.8, 12.1, 9.3],
                "FMM_A_Fp1": [45, 38, 32, 28, 22],
                "FMM_A_Fp2": [42, 35, 30, 25, 20],
            }
        )

    def test_plot_signal(self, sample_signal):
        """Test signal plotting."""
        fig = plot_signal(sample_signal, sampling_rate=128)
        assert fig is not None
        plt.close(fig)

    def test_plot_signal_subset(self, sample_signal):
        """Test plotting signal subset."""
        fig = plot_signal(sample_signal, sampling_rate=128, channels=["Fp1", "Fp2"], duration=5.0)
        assert fig is not None
        plt.close(fig)

    def test_plot_epochs(self, sample_epochs):
        """Test epoch plotting."""
        fig = plot_epochs(sample_epochs, sampling_rate=128)
        assert fig is not None
        plt.close(fig)

    def test_plot_quality_metrics(self, sample_quality):
        """Test quality metrics plotting."""
        fig = plot_quality_metrics(sample_quality)
        assert fig is not None
        plt.close(fig)

    def test_plot_fmm_components(self, sample_fmm):
        """Test FMM components plotting."""
        fig = plot_fmm_components(sample_fmm)
        assert fig is not None
        plt.close(fig)

    def test_plot_with_array(self):
        """Test plotting with numpy array input."""
        data = np.random.randn(1000, 3) * 50
        fig = plot_signal(data, sampling_rate=128)
        assert fig is not None
        plt.close(fig)
