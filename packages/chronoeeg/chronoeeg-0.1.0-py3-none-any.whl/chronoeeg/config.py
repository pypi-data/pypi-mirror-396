"""
Configuration Module for ChronoEEG

Centralized configuration management with environment variable support,
validation, and defaults.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class QualityConfig:
    """Quality assessment configuration."""

    nan_threshold: float = 0.15
    gap_threshold: float = 0.10
    outlier_threshold: float = 0.05
    flatline_threshold: float = 0.05
    sharpness_threshold: float = 0.10
    cohesion_threshold: float = 0.70

    def __post_init__(self):
        """Validate quality thresholds."""
        thresholds = [
            self.nan_threshold,
            self.gap_threshold,
            self.outlier_threshold,
            self.flatline_threshold,
            self.sharpness_threshold,
        ]
        for threshold in thresholds:
            if not 0 <= threshold <= 1:
                raise ValueError(f"Quality thresholds must be between 0 and 1, got {threshold}")

        if not 0 <= self.cohesion_threshold <= 1:
            raise ValueError(
                f"Cohesion threshold must be between 0 and 1, got {self.cohesion_threshold}"
            )


@dataclass
class PreprocessingConfig:
    """Preprocessing configuration."""

    epoch_duration: int = 300  # seconds
    overlap: float = 0.0  # fraction
    sampling_rate: int = 128  # Hz

    # Filtering
    lowcut: Optional[float] = 0.5  # Hz
    highcut: Optional[float] = 40.0  # Hz
    notch_freq: Optional[float] = 50.0  # Hz (power line noise)
    filter_order: int = 5

    def __post_init__(self):
        """Validate preprocessing parameters."""
        if self.epoch_duration <= 0:
            raise ValueError(f"Epoch duration must be positive, got {self.epoch_duration}")

        if not 0 <= self.overlap < 1:
            raise ValueError(f"Overlap must be in [0, 1), got {self.overlap}")

        if self.sampling_rate <= 0:
            raise ValueError(f"Sampling rate must be positive, got {self.sampling_rate}")

        if self.lowcut is not None and self.highcut is not None:
            if self.lowcut >= self.highcut:
                raise ValueError(f"lowcut ({self.lowcut}) must be < highcut ({self.highcut})")

        if self.filter_order <= 0:
            raise ValueError(f"Filter order must be positive, got {self.filter_order}")


@dataclass
class FeatureConfig:
    """Feature extraction configuration."""

    # Classical features
    extract_entropy: bool = True
    extract_fractal: bool = True
    extract_spectral: bool = True
    extract_statistical: bool = True

    # FMM features
    extract_fmm: bool = True
    n_components: int = 10
    max_iterations: int = 1000
    tolerance: float = 1e-6

    # Frequency bands (Hz)
    freq_bands: Dict[str, Tuple[float, float]] = field(
        default_factory=lambda: {
            "delta": (0.5, 4.0),
            "theta": (4.0, 8.0),
            "alpha": (8.0, 13.0),
            "beta": (13.0, 30.0),
            "gamma": (30.0, 40.0),
        }
    )

    def __post_init__(self):
        """Validate feature extraction parameters."""
        if self.n_components <= 0:
            raise ValueError(f"Number of components must be positive, got {self.n_components}")

        if self.max_iterations <= 0:
            raise ValueError(f"Max iterations must be positive, got {self.max_iterations}")

        if self.tolerance <= 0:
            raise ValueError(f"Tolerance must be positive, got {self.tolerance}")

        # Validate frequency bands
        for band_name, (low, high) in self.freq_bands.items():
            if low >= high:
                raise ValueError(f"Invalid frequency band '{band_name}': {low} >= {high}")


@dataclass
class ParallelConfig:
    """Parallel processing configuration."""

    n_jobs: int = -1  # Use all available cores
    backend: str = "loky"
    verbose: int = 0
    prefer: str = "threads"  # or "processes"

    def __post_init__(self):
        """Validate parallel processing parameters."""
        if self.backend not in ["loky", "threading", "multiprocessing"]:
            raise ValueError(f"Invalid backend: {self.backend}")

        if self.prefer not in ["threads", "processes"]:
            raise ValueError(f"Invalid prefer: {self.prefer}")

        if self.verbose < 0:
            raise ValueError(f"Verbose must be non-negative, got {self.verbose}")


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    log_to_file: bool = False
    log_file: Optional[Path] = None

    def __post_init__(self):
        """Validate logging parameters."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level not in valid_levels:
            raise ValueError(f"Invalid log level: {self.level}. Must be one of {valid_levels}")

        if self.log_to_file and self.log_file is None:
            raise ValueError("log_file must be specified when log_to_file is True")


@dataclass
class ChronoEEGConfig:
    """
    Main configuration class for ChronoEEG.

    Centralizes all configuration parameters with validation and
    environment variable support.

    Examples
    --------
    >>> config = ChronoEEGConfig()
    >>> config.preprocessing.sampling_rate
    128
    >>> config.quality.nan_threshold = 0.20
    >>> config.save_to_yaml('my_config.yaml')
    """

    quality: QualityConfig = field(default_factory=QualityConfig)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)
    features: FeatureConfig = field(default_factory=FeatureConfig)
    parallel: ParallelConfig = field(default_factory=ParallelConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Project directories
    data_dir: Path = field(default_factory=lambda: Path.cwd() / "data")
    output_dir: Path = field(default_factory=lambda: Path.cwd() / "output")
    cache_dir: Path = field(default_factory=lambda: Path.cwd() / ".cache")

    # Reproducibility
    random_seed: int = 42

    def __post_init__(self):
        """Create directories and apply environment variables."""
        # Create directories if they don't exist
        for dir_path in [self.data_dir, self.output_dir, self.cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Apply environment variables
        self._apply_env_vars()

    def _apply_env_vars(self):
        """Apply environment variable overrides."""
        # Example: CHRONOEEG_SAMPLING_RATE=256
        if env_sr := os.getenv("CHRONOEEG_SAMPLING_RATE"):
            self.preprocessing.sampling_rate = int(env_sr)

        if env_jobs := os.getenv("CHRONOEEG_N_JOBS"):
            self.parallel.n_jobs = int(env_jobs)

        if env_log_level := os.getenv("CHRONOEEG_LOG_LEVEL"):
            self.logging.level = env_log_level.upper()

        if env_seed := os.getenv("CHRONOEEG_RANDOM_SEED"):
            self.random_seed = int(env_seed)

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            "quality": self.quality.__dict__,
            "preprocessing": self.preprocessing.__dict__,
            "features": {
                **self.features.__dict__,
                "freq_bands": {
                    k: list(v) for k, v in self.features.freq_bands.items()
                },  # Convert tuples to lists for YAML
            },
            "parallel": self.parallel.__dict__,
            "logging": self.logging.__dict__,
            "data_dir": str(self.data_dir),
            "output_dir": str(self.output_dir),
            "cache_dir": str(self.cache_dir),
            "random_seed": self.random_seed,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict) -> "ChronoEEGConfig":
        """Create configuration from dictionary."""
        # Handle freq_bands conversion from list to tuple
        features_dict = config_dict.get("features", {})
        if "freq_bands" in features_dict:
            features_dict["freq_bands"] = {
                k: tuple(v) for k, v in features_dict["freq_bands"].items()
            }

        return cls(
            quality=QualityConfig(**config_dict.get("quality", {})),
            preprocessing=PreprocessingConfig(**config_dict.get("preprocessing", {})),
            features=FeatureConfig(**features_dict),
            parallel=ParallelConfig(**config_dict.get("parallel", {})),
            logging=LoggingConfig(**config_dict.get("logging", {})),
            data_dir=Path(config_dict.get("data_dir", Path.cwd() / "data")),
            output_dir=Path(config_dict.get("output_dir", Path.cwd() / "output")),
            cache_dir=Path(config_dict.get("cache_dir", Path.cwd() / ".cache")),
            random_seed=config_dict.get("random_seed", 42),
        )

    def save_to_yaml(self, filepath: Path):
        """Save configuration to YAML file."""
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML required for saving config. Install with: pip install pyyaml")

        with open(filepath, "w") as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False)

    @classmethod
    def load_from_yaml(cls, filepath: Path) -> "ChronoEEGConfig":
        """Load configuration from YAML file."""
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML required for loading config. Install with: pip install pyyaml"
            )

        with open(filepath, "r") as f:
            config_dict = yaml.safe_load(f)

        return cls.from_dict(config_dict)


# Global default configuration instance
DEFAULT_CONFIG = ChronoEEGConfig()


def get_config() -> ChronoEEGConfig:
    """
    Get the default configuration instance.

    Returns
    -------
    ChronoEEGConfig
        Default configuration object

    Examples
    --------
    >>> config = get_config()
    >>> config.preprocessing.sampling_rate
    128
    """
    return DEFAULT_CONFIG


def set_config(config: ChronoEEGConfig):
    """
    Set the global default configuration.

    Parameters
    ----------
    config : ChronoEEGConfig
        New configuration to set as default

    Examples
    --------
    >>> new_config = ChronoEEGConfig()
    >>> new_config.preprocessing.sampling_rate = 256
    >>> set_config(new_config)
    """
    global DEFAULT_CONFIG
    DEFAULT_CONFIG = config
