"""
ChronoEEG: Advanced Multidimensional EEG Analysis Toolkit

A professional, modular Python library for comprehensive multidimensional EEG
signal analysis, featuring advanced quality assessment, feature extraction
(including Frequency Modulated Möbius decomposition), and machine learning
capabilities.
"""

__version__ = "0.1.0"
__author__ = "ChronoEEG Contributors"
__email__ = "chronoeeg@example.com"
__url__ = "https://github.com/yourusername/chronoeeg"
__license__ = "MIT"

# Configuration and logging
from chronoeeg.config import ChronoEEGConfig, get_config, set_config

# Exceptions
from chronoeeg.exceptions import (
    ChannelMismatchError,
    ChronoEEGError,
    ConfigurationError,
    DataLoadError,
    DataValidationError,
    EpochError,
    FeatureExtractionError,
    FMMConvergenceError,
    InsufficientDataError,
    PreprocessingError,
    QualityAssessmentError,
    SamplingRateMismatchError,
)
from chronoeeg.features.classical import ClassicalFeatureExtractor
from chronoeeg.features.fmm import FMMFeatureExtractor

# Core components
from chronoeeg.io.loaders import EEGDataLoader, MultiDatasetLoader
from chronoeeg.logging_config import get_logger, setup_logger
from chronoeeg.pipeline.pipeline import EEGAnalysisPipeline
from chronoeeg.preprocessing.epoching import EpochExtractor
from chronoeeg.preprocessing.filters import SignalFilter
from chronoeeg.quality.assessors import QualityAssessor

__all__ = [
    # Core components
    "EEGDataLoader",
    "MultiDatasetLoader",
    "EpochExtractor",
    "SignalFilter",
    "QualityAssessor",
    "ClassicalFeatureExtractor",
    "FMMFeatureExtractor",
    "EEGAnalysisPipeline",
    # Configuration
    "ChronoEEGConfig",
    "get_config",
    "set_config",
    # Logging
    "setup_logger",
    "get_logger",
    # Exceptions
    "ChronoEEGError",
    "DataLoadError",
    "DataValidationError",
    "PreprocessingError",
    "QualityAssessmentError",
    "FeatureExtractionError",
    "ConfigurationError",
    "InsufficientDataError",
    "SamplingRateMismatchError",
    "ChannelMismatchError",
    "EpochError",
    "FMMConvergenceError",
]
