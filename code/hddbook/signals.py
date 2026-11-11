"""Signal and channel models used by the book experiments.

The models are deliberately simple, textbook-level building blocks:
PMR/LMR isolated pulses, dibit responses, transition jitter, AWGN and
oversampled readback waveforms.  They are used to generate the figures of
chapters 5-8 and to drive the detector experiments of chapters 6-8.
"""

from __future__ import annotations

import numpy as np

LN2 = np.log(2.0)


def prbs(n: int, seed: int | None = None, *, rng: np.random.Generator | None = None) -> np.ndarray:
    """Return ``n`` random bits (0/1) with a fixed seed."""
    g = rng if rng is not None else np.random.default_rng(20261111 if seed is None else seed)
    return g.integers(0, 2, size=n, dtype=np.int8)


def longitudinal_pulse(t: np.ndarray, pw50: float) -> np.ndarray:
    """Lorentzian isolated pulse for longitudinal recording (peak normalized to 1).

    ``pw50`` is the full width at half maximum in the same unit as ``t``.
    """
    t = np.asarray(t, dtype=float)
    return 1.0 / (1.0 + (2.0 * t / pw50) ** 2)


def perpendicular_pulse(t: np.ndarray, pw50: float) -> np.ndarray:
    """Gaussian isolated pulse for perpendicular recording (peak normalized to 1)."""
    t = np.asarray(t, dtype=float)
    return np.exp(-4.0 * LN2 * (t / pw50) ** 2)


def isolated_pulse(t: np.ndarray, pw50: float, kind: str = "longitudinal") -> np.ndarray:
    """Dispatch to the longitudinal or perpendicular isolated-pulse model."""
    if kind == "longitudinal":
        return longitudinal_pulse(t, pw50)
    if kind == "perpendicular":
        return perpendicular_pulse(t, pw50)
    raise ValueError(f"unknown pulse kind: {kind!r}")


def dibit_response(t: np.ndarray, pw50: float, tsep: float, kind: str = "longitudinal") -> np.ndarray:
    """Dibit response: two opposite transitions separated by ``tsep``.

    This is a first-order approximation used to illustrate ISI growth as the
    transition spacing shrinks; real dibit responses include read-head
    geometry and media effects (chapter 5).
    """
    return isolated_pulse(t, pw50, kind) - isolated_pulse(t - tsep, pw50, kind)


def pulse_spectrum(freq: np.ndarray, pw50: float, kind: str = "longitudinal") -> np.ndarray:
    """Magnitude spectrum of the isolated pulse (normalized to 1 at DC).

    Longitudinal: Lorentzian -> exp(-pi*pw50*|f|/2); perpendicular: Gaussian.
    """
    f = np.abs(np.asarray(freq, dtype=float))
    if kind == "longitudinal":
        return np.exp(-np.pi * pw50 * f / 2.0)
    if kind == "perpendicular":
        return np.exp(-(np.pi * pw50 * f) ** 2 / (16.0 * LN2))
    raise ValueError(f"unknown pulse kind: {kind!r}")


def transition_positions(bits: np.ndarray, t: float, sigma_j: float, rng: np.random.Generator) -> np.ndarray:
    """Return jittered transition times for a bit sequence.

    A transition is placed at every bit boundary where the bit value changes;
    each transition time is perturbed by zero-mean Gaussian jitter ``sigma_j``.
    """
    bits = np.asarray(bits, dtype=np.int8)
    edges = np.flatnonzero(np.diff(bits) != 0) + 1
    jitter = rng.normal(0.0, sigma_j, size=edges.size)
    return edges.astype(float) * t + jitter


def readback_waveform(
    bits: np.ndarray,
    *,
    pw50: float,
    t: float,
    osr: int = 8,
    sigma_j: float = 0.0,
    kind: str = "longitudinal",
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate a noise-free oversampled readback waveform from a bit sequence.

    Returns ``(time, signal)`` where ``signal`` is the superposition of
    isolated pulses at (optionally jittered) transition positions, sampled at
    ``t / osr``.  Add noise separately with :func:`add_awgn`.
    """
    g = rng if rng is not None else np.random.default_rng(20261111)
    n = bits.size
    dt = t / osr
    time = np.arange(-2 * osr, (n + 2) * osr) * dt
    if sigma_j > 0:
        pos = transition_positions(bits, t, sigma_j, g)
    else:
        pos = (np.flatnonzero(np.diff(np.asarray(bits, dtype=np.int8)) != 0) + 1).astype(float) * t
    signal = np.zeros_like(time)
    for p in pos:
        signal += isolated_pulse(time - p, pw50, kind)
    return time, signal


def add_awgn(x: np.ndarray, snr_db: float, rng: np.random.Generator, *, signal_power: float | None = None) -> np.ndarray:
    """Add white Gaussian noise at the requested SNR (signal power / noise power)."""
    x = np.asarray(x, dtype=float)
    p_sig = float(np.mean(x**2)) if signal_power is None else float(signal_power)
    p_noise = p_sig / (10.0 ** (snr_db / 10.0))
    return x + rng.normal(0.0, np.sqrt(p_noise), size=x.shape)
