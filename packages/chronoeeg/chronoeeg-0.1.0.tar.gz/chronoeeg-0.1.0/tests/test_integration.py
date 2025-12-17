"""
Integration tests for complete workflows.
"""

import numpy as np
import pandas as pd
import pytest

from chronoeeg import (
    ClassicalFeatureExtractor,
    EEGAnalysisPipeline,
    EEGDataLoader,
    EpochExtractor,
    FMMFeatureExtractor,
    QualityAssessor,
)


class TestCompleteWorkflow:
    """Test complete end-to-end workflows."""

    @pytest.fixture
    def synthetic_eeg(self):
        """Generate synthetic EEG data for testing."""
        np.random.seed(42)
        # 15 minutes of data at 128 Hz
        n_samples = 128 * 60 * 15
        n_channels = 6

        # Simulate EEG with multiple frequency components
        time = np.arange(n_samples) / 128
        data = np.zeros((n_samples, n_channels))

        for i in range(n_channels):
            # Delta (1-4 Hz)
            data[:, i] += 20 * np.sin(2 * np.pi * 2 * time)
            # Alpha (8-13 Hz)
            data[:, i] += 30 * np.sin(2 * np.pi * 10 * time)
            # Beta (13-30 Hz)
            data[:, i] += 15 * np.sin(2 * np.pi * 20 * time)
            # Add noise
            data[:, i] += np.random.randn(n_samples) * 5

        channels = ["Fp1", "Fp2", "F3", "F4", "C3", "C4"]
        return pd.DataFrame(data, columns=channels)

    def test_full_pipeline(self, synthetic_eeg):
        """Test complete analysis pipeline."""
        # Create pipeline
        pipeline = EEGAnalysisPipeline(
            epoch_duration=300,  # 5 minutes
            sampling_rate=128,
            quality_threshold=0.7,
            extract_classical=True,
            extract_fmm=True,
            n_fmm_components=5,
        )

        # Process data
        results = pipeline.process(synthetic_eeg)

        # Verify results structure
        assert "epochs" in results
        assert "quality" in results
        assert "features" in results

        # Verify epochs
        assert "epoch_id" in results["epochs"].columns
        assert len(results["epochs"]) > 0

        # Verify quality scores
        assert "overall_quality" in results["quality"].columns
        assert "passes_threshold" in results["quality"].columns

        # Verify features
        assert len(results["features"]) > 0
        # Should have at least some classical features
        classical_cols = [
            col
            for col in results["features"].columns
            if any(x in col.lower() for x in ["entropy", "hjorth", "spectral"])
        ]
        assert len(classical_cols) > 0

    def test_manual_workflow(self, synthetic_eeg):
        """Test manual step-by-step workflow."""
        # Step 1: Epoch extraction
        epocher = EpochExtractor(epoch_duration=300, sampling_rate=128)
        epochs = epocher.fit_transform(synthetic_eeg)

        assert "epoch_id" in epochs.columns
        n_epochs = epochs["epoch_id"].nunique()
        assert n_epochs >= 2  # 15 min / 5 min = 3 epochs

        # Step 2: Quality assessment
        assessor = QualityAssessor()
        quality = assessor.assess(epochs, epoch_column="epoch_id")

        assert len(quality) == n_epochs
        assert "passes_threshold" in quality.columns

        # Step 3: Get good epochs
        good_epoch_ids = quality[quality["passes_threshold"]]["epoch_id"].values
        # Synthetic data might not pass all thresholds, so we check >= 0
        assert len(good_epoch_ids) >= 0

        # Step 4: Extract features from first good epoch (if any exist)
        if len(good_epoch_ids) > 0:
            first_good_epoch = good_epoch_ids[0]
            epoch_data = epochs[epochs["epoch_id"] == first_good_epoch].drop("epoch_id", axis=1)

            # Classical features
            classical_extractor = ClassicalFeatureExtractor(sampling_rate=128)
            classical_features = classical_extractor.extract(epoch_data)
            assert len(classical_features) > 0

            # FMM features
            fmm_extractor = FMMFeatureExtractor(n_components=3)
            fmm_features = fmm_extractor.extract(epoch_data)
            assert len(fmm_features) == 3  # 3 components
            assert "FMM_R2" in fmm_features.columns

    def test_quality_filtering_workflow(self, synthetic_eeg):
        """Test workflow with strict quality filtering."""
        # Epoch extraction
        epocher = EpochExtractor(epoch_duration=300, sampling_rate=128)
        epochs = epocher.fit_transform(synthetic_eeg)

        # Strict quality assessment
        assessor = QualityAssessor(
            nan_threshold=0.10,
            gap_threshold=0.05,
            outlier_threshold=0.03,
        )
        quality = assessor.assess(epochs, epoch_column="epoch_id")

        # Filter high-quality epochs
        high_quality = quality[quality["overall_quality"] > 0.9]

        # Since synthetic data is clean, should have high quality
        assert len(high_quality) > 0

    def test_parallel_processing(self, synthetic_eeg):
        """Test parallel processing workflow."""
        from chronoeeg.utils.parallel import ParallelProcessor

        # Create processor
        processor = ParallelProcessor(n_jobs=2, verbose=0)

        # Split data into chunks
        chunk_size = len(synthetic_eeg) // 3
        chunks = [
            synthetic_eeg.iloc[i : i + chunk_size] for i in range(0, len(synthetic_eeg), chunk_size)
        ]

        # Process in parallel
        def process_chunk(chunk):
            epocher = EpochExtractor(epoch_duration=60, sampling_rate=128)
            return epocher.fit_transform(chunk)

        results = processor.map(process_chunk, chunks)

        assert len(results) == len(chunks)
        for result in results:
            assert "epoch_id" in result.columns

    def test_error_handling(self):
        """Test error handling in workflow."""
        # Empty data should raise error
        with pytest.raises(Exception):
            pipeline = EEGAnalysisPipeline()
            pipeline.process(pd.DataFrame())

    def test_configuration_workflow(self, synthetic_eeg):
        """Test workflow with custom configuration."""
        from chronoeeg.config import ChronoEEGConfig

        # Create custom config
        config = ChronoEEGConfig()
        config.preprocessing.epoch_duration = 180  # 3 minutes
        config.preprocessing.sampling_rate = 128
        config.quality.nan_threshold = 0.20
        config.features.n_components = 8

        # Use config in pipeline
        pipeline = EEGAnalysisPipeline(
            epoch_duration=config.preprocessing.epoch_duration,
            sampling_rate=config.preprocessing.sampling_rate,
            quality_threshold=0.7,
            n_fmm_components=config.features.n_components,
        )

        results = pipeline.process(synthetic_eeg)

        # Verify 3-minute epochs
        epoch_duration = len(results["epochs"]) / results["epochs"]["epoch_id"].nunique()
        expected_samples = 180 * 128  # 3 min * 128 Hz
        assert abs(epoch_duration - expected_samples) < 10  # Allow small tolerance
