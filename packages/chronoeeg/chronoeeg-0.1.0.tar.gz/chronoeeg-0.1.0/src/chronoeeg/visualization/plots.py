"""
Plotting utilities for EEG data visualization.

Provides functions for visualizing signals, quality metrics, features,
and FMM decompositions.
"""

from typing import List, Optional, Tuple, Union

import numpy as np
import pandas as pd

try:
    import matplotlib.gridspec as gridspec
    import matplotlib.pyplot as plt
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import seaborn as sns

    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False


def _check_matplotlib():
    """Check if matplotlib is available."""
    if not HAS_MATPLOTLIB:
        raise ImportError(
            "Matplotlib is required for plotting. " "Install with: pip install chronoeeg[viz]"
        )


def plot_signal(
    data: Union[pd.DataFrame, np.ndarray],
    sampling_rate: int = 128,
    channels: Optional[List[str]] = None,
    start_time: float = 0.0,
    duration: Optional[float] = None,
    figsize: Tuple[int, int] = (15, 8),
    title: str = "EEG Signal",
) -> Figure:
    """
    Plot multi-channel EEG signal.

    Parameters
    ----------
    data : pd.DataFrame or np.ndarray
        EEG data with shape (n_samples, n_channels)
    sampling_rate : int
        Sampling frequency in Hz
    channels : list of str, optional
        Channel names to plot (default: all)
    start_time : float
        Start time in seconds
    duration : float, optional
        Duration to plot in seconds (default: all)
    figsize : tuple
        Figure size (width, height)
    title : str
        Plot title

    Returns
    -------
    Figure
        Matplotlib figure object
    """
    _check_matplotlib()

    if isinstance(data, np.ndarray):
        df = pd.DataFrame(data)
        if channels is None:
            channels = [f"Ch{i+1}" for i in range(data.shape[1])]
        df.columns = channels
    else:
        df = data
        if channels is None:
            channels = df.columns.tolist()
        else:
            df = df[channels]

    # Time vector
    n_samples = len(df)
    time = np.arange(n_samples) / sampling_rate + start_time

    # Apply duration filter
    if duration is not None:
        end_time = start_time + duration
        mask = (time >= start_time) & (time <= end_time)
        time = time[mask]
        df = df.iloc[mask]

    # Create figure
    fig, axes = plt.subplots(len(channels), 1, figsize=figsize, sharex=True)
    if len(channels) == 1:
        axes = [axes]

    for i, (ax, channel) in enumerate(zip(axes, channels)):
        ax.plot(time, df[channel], linewidth=0.5, color="navy")
        ax.set_ylabel(channel, fontsize=10, fontweight="bold")
        ax.grid(True, alpha=0.3)

        # Remove x-axis ticks for all but bottom subplot
        if i < len(channels) - 1:
            ax.set_xticklabels([])

    axes[-1].set_xlabel("Time (s)", fontsize=12, fontweight="bold")
    fig.suptitle(title, fontsize=14, fontweight="bold")
    plt.tight_layout()

    return fig


def plot_epochs(
    epochs: pd.DataFrame,
    epoch_column: str = "epoch_id",
    max_epochs: int = 10,
    sampling_rate: int = 128,
    figsize: Tuple[int, int] = (15, 10),
) -> Figure:
    """
    Plot multiple epochs from epoched data.

    Parameters
    ----------
    epochs : pd.DataFrame
        Epoched EEG data with epoch_id column
    epoch_column : str
        Name of epoch identifier column
    max_epochs : int
        Maximum number of epochs to plot
    sampling_rate : int
        Sampling frequency in Hz
    figsize : tuple
        Figure size

    Returns
    -------
    Figure
        Matplotlib figure object
    """
    _check_matplotlib()

    epoch_ids = epochs[epoch_column].unique()[:max_epochs]
    channels = [col for col in epochs.columns if col != epoch_column]

    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(len(epoch_ids), len(channels), hspace=0.3, wspace=0.3)

    for i, epoch_id in enumerate(epoch_ids):
        epoch_data = epochs[epochs[epoch_column] == epoch_id]
        time = np.arange(len(epoch_data)) / sampling_rate

        for j, channel in enumerate(channels):
            ax = fig.add_subplot(gs[i, j])
            ax.plot(time, epoch_data[channel], linewidth=0.5)

            if i == 0:
                ax.set_title(channel, fontsize=10, fontweight="bold")
            if j == 0:
                ax.set_ylabel(f"Epoch {epoch_id}", fontsize=9)
            if i == len(epoch_ids) - 1:
                ax.set_xlabel("Time (s)", fontsize=9)

            ax.grid(True, alpha=0.3)

    fig.suptitle("EEG Epochs", fontsize=14, fontweight="bold")

    return fig


def plot_quality_metrics(
    quality_scores: pd.DataFrame,
    figsize: Tuple[int, int] = (12, 6),
) -> Figure:
    """
    Plot quality assessment metrics.

    Parameters
    ----------
    quality_scores : pd.DataFrame
        Quality metrics with columns for each metric
    figsize : tuple
        Figure size

    Returns
    -------
    Figure
        Matplotlib figure object
    """
    _check_matplotlib()

    metric_cols = [
        col
        for col in quality_scores.columns
        if col not in ["epoch_id", "overall_quality", "passes_threshold"]
    ]

    fig, axes = plt.subplots(2, 3, figsize=figsize)
    axes = axes.flatten()

    for i, metric in enumerate(metric_cols[:6]):
        ax = axes[i]
        ax.hist(quality_scores[metric], bins=30, edgecolor="black", alpha=0.7)
        ax.set_title(metric.replace("_", " ").title(), fontweight="bold")
        ax.set_xlabel("Score")
        ax.set_ylabel("Frequency")
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.suptitle("Quality Metrics Distribution", fontsize=14, fontweight="bold", y=1.02)

    return fig


def plot_feature_importance(
    features: pd.DataFrame,
    importance: np.ndarray,
    top_n: int = 20,
    figsize: Tuple[int, int] = (10, 8),
) -> Figure:
    """
    Plot feature importance scores.

    Parameters
    ----------
    features : pd.DataFrame
        Feature matrix
    importance : np.ndarray
        Feature importance scores
    top_n : int
        Number of top features to display
    figsize : tuple
        Figure size

    Returns
    -------
    Figure
        Matplotlib figure object
    """
    _check_matplotlib()

    # Sort by importance
    indices = np.argsort(importance)[::-1][:top_n]
    feature_names = features.columns[indices]
    scores = importance[indices]

    fig, ax = plt.subplots(figsize=figsize)
    y_pos = np.arange(len(feature_names))

    ax.barh(y_pos, scores, align="center", alpha=0.7, edgecolor="black")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(feature_names)
    ax.invert_yaxis()
    ax.set_xlabel("Importance Score", fontweight="bold")
    ax.set_title(f"Top {top_n} Feature Importance", fontsize=14, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")

    plt.tight_layout()

    return fig


def plot_fmm_components(
    fmm_params: pd.DataFrame,
    figsize: Tuple[int, int] = (14, 10),
) -> Figure:
    """
    Visualize FMM decomposition components.

    Parameters
    ----------
    fmm_params : pd.DataFrame
        FMM parameters with Wave, R2, alpha, omega columns
    figsize : tuple
        Figure size

    Returns
    -------
    Figure
        Matplotlib figure object
    """
    _check_matplotlib()

    fig, axes = plt.subplots(2, 2, figsize=figsize)

    # R² values
    axes[0, 0].bar(fmm_params["Wave"], fmm_params["FMM_R2"], alpha=0.7, edgecolor="black")
    axes[0, 0].set_xlabel("Component", fontweight="bold")
    axes[0, 0].set_ylabel("R² (Variance Explained)", fontweight="bold")
    axes[0, 0].set_title("Component Variance", fontweight="bold")
    axes[0, 0].grid(True, alpha=0.3)

    # Alpha (phase)
    axes[0, 1].scatter(fmm_params["Wave"], fmm_params["FMM_α"], alpha=0.7, s=100, edgecolor="black")
    axes[0, 1].set_xlabel("Component", fontweight="bold")
    axes[0, 1].set_ylabel("α (Phase)", fontweight="bold")
    axes[0, 1].set_title("Phase Parameters", fontweight="bold")
    axes[0, 1].grid(True, alpha=0.3)

    # Omega (frequency)
    axes[1, 0].scatter(
        fmm_params["Wave"], fmm_params["FMM_ω"], alpha=0.7, s=100, edgecolor="black", color="orange"
    )
    axes[1, 0].set_xlabel("Component", fontweight="bold")
    axes[1, 0].set_ylabel("ω (Frequency)", fontweight="bold")
    axes[1, 0].set_title("Frequency Modulation", fontweight="bold")
    axes[1, 0].grid(True, alpha=0.3)

    # Amplitude columns
    amp_cols = [col for col in fmm_params.columns if col.startswith("FMM_A_")]
    if amp_cols:
        amp_data = fmm_params[amp_cols].values
        im = axes[1, 1].imshow(amp_data.T, aspect="auto", cmap="viridis")
        axes[1, 1].set_xlabel("Component", fontweight="bold")
        axes[1, 1].set_ylabel("Channel", fontweight="bold")
        axes[1, 1].set_title("Amplitudes", fontweight="bold")
        plt.colorbar(im, ax=axes[1, 1])

    plt.tight_layout()
    fig.suptitle("FMM Decomposition", fontsize=14, fontweight="bold", y=1.02)

    return fig


def plot_spectrogram(
    data: Union[pd.DataFrame, np.ndarray],
    sampling_rate: int = 128,
    channel: Union[int, str] = 0,
    nperseg: int = 256,
    figsize: Tuple[int, int] = (12, 6),
) -> Figure:
    """
    Plot spectrogram of EEG signal.

    Parameters
    ----------
    data : pd.DataFrame or np.ndarray
        EEG data
    sampling_rate : int
        Sampling frequency in Hz
    channel : int or str
        Channel to plot (index or name)
    nperseg : int
        Length of each segment for STFT
    figsize : tuple
        Figure size

    Returns
    -------
    Figure
        Matplotlib figure object
    """
    _check_matplotlib()

    from scipy import signal as sp_signal

    if isinstance(data, pd.DataFrame):
        if isinstance(channel, str):
            signal_data = data[channel].values
        else:
            signal_data = data.iloc[:, channel].values
            channel = data.columns[channel]
    else:
        signal_data = data[:, channel] if data.ndim > 1 else data

    # Compute spectrogram
    f, t, Sxx = sp_signal.spectrogram(
        signal_data,
        fs=sampling_rate,
        nperseg=nperseg,
        noverlap=nperseg // 2,
    )

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.pcolormesh(t, f, 10 * np.log10(Sxx), shading="gouraud", cmap="viridis")
    ax.set_ylabel("Frequency (Hz)", fontweight="bold")
    ax.set_xlabel("Time (s)", fontweight="bold")
    ax.set_title(f"Spectrogram - {channel}", fontsize=14, fontweight="bold")
    ax.set_ylim([0, 40])  # Focus on relevant EEG frequencies

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Power (dB)", fontweight="bold")

    plt.tight_layout()

    return fig
