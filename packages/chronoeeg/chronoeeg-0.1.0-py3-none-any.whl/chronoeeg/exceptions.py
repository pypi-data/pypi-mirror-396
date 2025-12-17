"""
Custom Exceptions for ChronoEEG

Defines domain-specific exceptions for better error handling and debugging.
"""


class ChronoEEGError(Exception):
    """Base exception for all ChronoEEG errors."""

    pass


class DataLoadError(ChronoEEGError):
    """Raised when data loading fails."""

    pass


class DataValidationError(ChronoEEGError):
    """Raised when data validation fails."""

    pass


class PreprocessingError(ChronoEEGError):
    """Raised when preprocessing operations fail."""

    pass


class QualityAssessmentError(ChronoEEGError):
    """Raised when quality assessment fails."""

    pass


class FeatureExtractionError(ChronoEEGError):
    """Raised when feature extraction fails."""

    pass


class ConfigurationError(ChronoEEGError):
    """Raised when configuration is invalid."""

    pass


class InsufficientDataError(ChronoEEGError):
    """Raised when there's not enough data to perform an operation."""

    pass


class SamplingRateMismatchError(ChronoEEGError):
    """Raised when sampling rates don't match across datasets."""

    pass


class ChannelMismatchError(ChronoEEGError):
    """Raised when channel configurations don't match."""

    pass


class EpochError(ChronoEEGError):
    """Raised when epoch extraction or processing fails."""

    pass


class FMMConvergenceError(ChronoEEGError):
    """Raised when FMM decomposition fails to converge."""

    pass
