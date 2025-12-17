"""
Frequency Modulated Möbius (FMM) Feature Extraction

This module implements the Frequency Modulated Möbius (FMM) decomposition
for EEG signals, extracting oscillatory components via Möbius transformations
in the complex plane.
"""

from math import pi
from typing import Tuple, Union

import numpy as np
import pandas as pd
from numpy.fft import fft, ifft
from scipy import signal as sp_signal
from sklearn.linear_model import LinearRegression

from chronoeeg.features.base import BaseFeatureExtractor


class FMMFeatureExtractor(BaseFeatureExtractor):
    """
    Extract Frequency Modulated Möbius (FMM) features from EEG data.

    The FMM decomposition represents EEG signals as a sum of oscillatory
    components with time-varying frequency modulation, computed via Möbius
    transformations in the complex plane.

    Parameters
    ----------
    n_components : int
        Number of oscillatory components to extract (default: 10)
    sampling_rate : int
        Sampling frequency in Hz (default: 128)

    Attributes
    ----------
    n_components : int
        Number of FMM components

    Examples
    --------
    >>> extractor = FMMFeatureExtractor(n_components=10, sampling_rate=128)
    >>> features = extractor.extract(eeg_data)
    >>> print(f"Extracted {len(features)} FMM components")

    Notes
    -----
    The FMM decomposition provides:
    - R²: Variance explained by each component
    - α (alpha): Phase parameters
    - ω (omega): Frequency modulation parameters
    - A (amplitudes): Per-channel amplitudes for each component

    References
    ----------
    Frequency Modulated Möbius model for multi-channel EEG decomposition.
    """

    def __init__(self, n_components: int = 10, sampling_rate: int = 128):
        """Initialize FMM feature extractor."""
        super().__init__(sampling_rate)
        self.n_components = n_components
        self._counter = None

    def extract(self, data: Union[pd.DataFrame, np.ndarray]) -> pd.DataFrame:
        """
        Extract FMM parameters from EEG data.

        Parameters
        ----------
        data : pd.DataFrame or np.ndarray
            EEG data with shape (n_samples, n_channels)

        Returns
        -------
        pd.DataFrame
            FMM parameters with columns:
            - Wave: Component number (1 to n_components)
            - FMM_R2: Variance explained
            - FMM_α: Phase parameter
            - FMM_ω: Frequency modulation parameter
            - FMM_A_{channel}: Amplitude for each channel
        """
        # Validate and convert input
        df = self._validate_input(data)

        # Transpose for internal processing (channels x samples)
        data_array = df.T.to_numpy()
        channels = df.columns

        # Estimate FMM parameters
        fmm_params = self._estimate_parameters(data_array, channels)

        return fmm_params

    def _estimate_parameters(self, data: np.ndarray, channels: pd.Index) -> pd.DataFrame:
        """
        Estimate FMM parameters using Möbius transformation.

        Parameters
        ----------
        data : np.ndarray
            EEG data with shape (n_channels, n_samples)
        channels : pd.Index
            Channel names

        Returns
        -------
        pd.DataFrame
            Estimated FMM parameters
        """
        # Compute analytic signal via Hilbert transform
        analytic_signal = sp_signal.hilbert(data)
        n_channels, n_obs = analytic_signal.shape
        t = np.expand_dims(np.arange(0, n_obs) / n_obs * 2 * pi, axis=0)

        # Generate search spaces in the unit disk
        dic_an = self._generate_circle_disk(1, n_obs, 0)
        dic_an_search = self._generate_circle_disk(1, n_obs, 2 * pi - 2 * pi / n_obs)
        _, an_search_len = dic_an_search.shape

        # Precompute FFT bases
        base = np.zeros((an_search_len, n_obs), dtype=complex)
        self._counter = -1
        base = np.apply_along_axis(lambda row: self._get_fft_base(dic_an, t, n_obs), 1, base)
        base = base.reshape((an_search_len, n_obs))

        # Initialize parameters
        an = np.zeros((self.n_components + 1), dtype=complex)
        coefficients = np.zeros((n_channels, self.n_components + 1), dtype=complex)
        residuals = analytic_signal.copy()

        # Extract DC component
        self._update_channel(n_channels, n_obs, coefficients, residuals, an, t, 0)

        # Extract oscillatory components
        for component in range(1, self.n_components + 1):
            S1_tmp = np.zeros((an_search_len, n_obs))

            for ch in range(n_channels):
                fft_residual = fft(residuals[ch, :], n_obs)
                fft_repeated = np.repeat(fft_residual[np.newaxis, :], an_search_len, axis=0)
                S1_tmp += np.abs(ifft(fft_repeated * base, n_obs, 1))

            S1_tmp = S1_tmp.T
            max_loc_tmp = np.argwhere(S1_tmp == np.amax(S1_tmp))
            an[component] = dic_an_search[max_loc_tmp[0, 0], max_loc_tmp[0, 1]]

            self._update_channel(n_channels, n_obs, coefficients, residuals, an, t, component)

        # Compute phase and frequency parameters
        alphas = np.angle(an)
        alphas = np.unwrap(alphas)[1:]
        omegas = (1 - np.abs(an)) / (1 + np.abs(an))
        omegas = omegas[1:]

        alphas2 = np.mod(alphas + np.pi, 2 * np.pi)

        # Compute amplitudes and phase shifts
        amplitudes, betas = self._calculate_amplitudes_betas(
            n_channels, self.n_components, t, alphas2, omegas, data
        )

        # Compute R² (variance explained)
        residuals_fresh = data.copy()
        R2comp = self._calculate_r2_index(
            n_channels, self.n_components, t, alphas2, omegas, betas, residuals_fresh, data
        )

        # Sort by time order
        time_order = np.argsort(alphas)
        alphas = alphas[time_order]
        alphas2 = alphas2[time_order]
        omegas = omegas[time_order]
        amplitudes = amplitudes[:, time_order].T
        betas = betas[:, time_order]
        R2comp = R2comp[time_order]

        # Create output DataFrame
        column_names = ["R2", "α", "ω"] + [f"A_{c}" for c in channels]
        column_names = [f"FMM_{x}" for x in column_names]

        fmm_params = pd.DataFrame(
            np.column_stack((R2comp, alphas2, omegas, amplitudes)),
            columns=column_names,
        )
        fmm_params.insert(0, "Wave", np.arange(1, self.n_components + 1))

        return fmm_params

    @staticmethod
    def _complex_transform(x: complex, t: np.ndarray) -> np.ndarray:
        """
        Compute Möbius transformation.

        Parameters
        ----------
        x : complex
            Point in the unit disk
        t : np.ndarray
            Time array

        Returns
        -------
        np.ndarray
            Transformed complex values
        """
        return ((1 - np.abs(x) ** 2) ** 0.5) / (1 - np.conj(x) * np.exp(1j * t))

    @staticmethod
    def _calculate_coefficient(a: complex, t: np.ndarray, G: np.ndarray, n_obs: int) -> complex:
        """Calculate FMM coefficient."""
        denominator = (1 - np.conj(a) * np.exp(1j * t)).dot(G.conj().T)
        if denominator == 0:
            denominator = 0.000001 + 0.000001j
        return np.conj(((1 - np.abs(a) ** 2) ** 0.5) / denominator) / n_obs

    def _generate_circle_disk(
        self, max_magnitude: float, n_obs: int, max_phase: float
    ) -> np.ndarray:
        """
        Generate search grid in the unit disk.

        Parameters
        ----------
        max_magnitude : float
            Maximum magnitude (typically 1.0)
        n_obs : int
            Number of observations
        max_phase : float
            Maximum phase angle

        Returns
        -------
        np.ndarray
            Complex grid points in the unit disk
        """
        phase = np.arange(0.0, max_phase + 2 * np.pi / n_obs, 2 * np.pi / n_obs)[np.newaxis, :]
        magnitude = np.sort(
            -np.arange(np.sqrt(0.01), np.sqrt(0.6), ((np.sqrt(0.6) - np.sqrt(0.01)) / 24)) ** 2 + 1
        )[np.newaxis, :]

        n_phase = phase.shape[1]
        n_magnitude = magnitude.shape[1]
        magnitude = np.repeat(magnitude, n_phase, axis=0)
        phase = np.repeat(phase.T, n_magnitude, axis=1)

        disk = magnitude * np.exp(1j * phase)
        disk[np.abs(disk) - max_magnitude >= -1e-15] = np.nan

        disk = disk[~np.isnan(disk).all(axis=1)]
        disk = disk[:, ~np.isnan(disk).all(axis=0)]

        return disk

    def _update_channel(
        self,
        n_channels: int,
        n_obs: int,
        coefficients: np.ndarray,
        residuals: np.ndarray,
        an: np.ndarray,
        t: np.ndarray,
        component: int,
    ):
        """Update channel residuals after extracting a component."""
        for ch in range(n_channels):
            coefficients[ch, component] = self._calculate_coefficient(
                an[component], t, residuals[ch, :], n_obs
            )[0]
            residuals[ch, :] = (
                (
                    residuals[ch, :]
                    - coefficients[ch, component] * self._complex_transform(an[component], t)
                )
                * (1 - np.conj(an[component]) * np.exp(1j * t))
                / (np.exp(1j * t) - an[component])
            )

    def _get_fft_base(self, dic_an: np.ndarray, t: np.ndarray, n_obs: int) -> np.ndarray:
        """Compute FFT base for search."""
        self._counter += 1
        return fft(self._complex_transform(dic_an[0, self._counter], t), n_obs)

    def _calculate_amplitudes_betas(
        self,
        n_channels: int,
        n_components: int,
        t: np.ndarray,
        alphas2: np.ndarray,
        omegas: np.ndarray,
        data: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate amplitudes and phase shifts for each component."""
        amplitudes = np.zeros((n_channels, n_components))
        betas = np.zeros((n_channels, n_components))

        mm = np.zeros((len(t[0]), 2 * n_components + 1))
        mm[:, 0] = np.ones(len(t[0]))

        for i in range(n_components):
            t_star = 2 * np.arctan(omegas[i] * np.tan((t - alphas2[i]) / 2))
            mm[:, 2 * (i + 1) - 1] = np.cos(t_star)
            mm[:, 2 * (i + 1)] = np.sin(t_star)

        mm = np.linalg.pinv(mm.T @ mm) @ mm.T

        for ch in range(n_channels):
            coefs = mm @ data[ch, :]
            for i in range(n_components):
                amplitudes[ch, i] = np.sqrt(coefs[2 * i + 1] ** 2 + coefs[2 * i + 2] ** 2)
                betas[ch, i] = np.arctan2(-coefs[2 * i + 2], coefs[2 * i + 1])

        betas = np.mod(betas, 2 * np.pi)
        return amplitudes, betas

    def _calculate_r2_index(
        self,
        n_channels: int,
        n_components: int,
        t: np.ndarray,
        alphas2: np.ndarray,
        omegas: np.ndarray,
        betas: np.ndarray,
        residuals: np.ndarray,
        data: np.ndarray,
    ) -> np.ndarray:
        """Calculate R² (variance explained) for each component."""
        R2comp = np.zeros((n_channels, n_components + 1))

        for component in range(n_components):
            for ch in range(n_channels):
                cos_phi = np.cos(
                    betas[ch, component]
                    + 2 * np.arctan(omegas[component] * np.tan((t - alphas2[component]) / 2))
                )

                model = LinearRegression(n_jobs=1)
                model.fit(cos_phi.reshape(-1, 1), residuals[ch, :].reshape(-1, 1))

                intercept = model.intercept_[0]
                coef = model.coef_[0, 0]

                residuals[ch, :] -= (intercept + coef * cos_phi).flatten()

                variance = np.var(data[ch, :])
                if variance == 0:
                    variance = 0.00001
                R2comp[ch, component + 1] = 1 - np.var(residuals[ch, :]) / variance

        R2comp = np.mean(np.diff(R2comp, axis=1), axis=0)
        R2comp = R2comp / np.sum(R2comp)

        return R2comp


# Backwards compatibility alias
estimate_parameters = FMMFeatureExtractor.extract
