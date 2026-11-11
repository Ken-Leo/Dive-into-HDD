"""Performance metrics used across the book experiments."""

from __future__ import annotations

import numpy as np


def db_to_linear(db: float) -> float:
    """Convert a power ratio in dB to a linear scale."""
    return 10.0 ** (db / 10.0)


def linear_to_db(x: float) -> float:
    """Convert a linear power ratio to dB."""
    return 10.0 * np.log10(x)


def ber(reference: np.ndarray, estimate: np.ndarray) -> float:
    """Bit error rate between two equal-length bit sequences."""
    ref = np.asarray(reference).ravel()
    est = np.asarray(estimate).ravel()
    if ref.shape != est.shape:
        raise ValueError(f"shape mismatch: {ref.shape} vs {est.shape}")
    if ref.size == 0:
        return float("nan")
    return float(np.mean(ref != est))


def ser(reference: np.ndarray, estimate: np.ndarray) -> float:
    """Symbol error rate for integer symbol sequences."""
    ref = np.asarray(reference).ravel()
    est = np.asarray(estimate).ravel()
    if ref.shape != est.shape:
        raise ValueError(f"shape mismatch: {ref.shape} vs {est.shape}")
    if ref.size == 0:
        return float("nan")
    return float(np.mean(ref != est))


def snr_db(signal: np.ndarray, noise: np.ndarray) -> float:
    """Empirical SNR in dB between a clean signal and the additive noise."""
    p_sig = float(np.mean(np.asarray(signal, dtype=float) ** 2))
    p_noise = float(np.mean(np.asarray(noise, dtype=float) ** 2))
    if p_noise == 0.0:
        return float("inf")
    return float(linear_to_db(p_sig / p_noise))
