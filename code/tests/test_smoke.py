"""Smoke tests for the shared hddbook library (fast, no network)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hddbook import config, metrics, signals  # noqa: E402


def test_prbs_is_deterministic_and_binary():
    a = signals.prbs(64, seed=7)
    b = signals.prbs(64, seed=7)
    assert np.array_equal(a, b)
    assert set(np.unique(a)).issubset({0, 1})


def test_pulse_peak_and_half_width():
    t = np.linspace(-100.0, 100.0, 4001)
    pw50 = 50.0
    lmr = signals.longitudinal_pulse(t, pw50)
    pmr = signals.perpendicular_pulse(t, pw50)
    assert lmr.max() == pytest.approx(1.0, abs=1e-6)
    assert pmr.max() == pytest.approx(1.0, abs=1e-6)
    # half maximum at +/- pw50/2
    assert signals.longitudinal_pulse(np.array([pw50 / 2]), pw50)[0] == pytest.approx(0.5, abs=1e-6)
    assert signals.perpendicular_pulse(np.array([pw50 / 2]), pw50)[0] == pytest.approx(0.5, abs=1e-6)


def test_readback_waveform_shape():
    bits = signals.prbs(200, seed=3)
    t, x = signals.readback_waveform(bits, pw50=40.0, t=10.0, osr=8, sigma_j=0.5, rng=config.rng(3))
    assert x.shape == t.shape
    assert np.isfinite(x).all()


def test_awgn_snr_is_close_to_requested():
    g = config.rng(11)
    x = np.sin(np.linspace(0, 20 * np.pi, 20000))
    noise = signals.add_awgn(np.zeros_like(x), 10.0, g, signal_power=float(np.mean(x**2))) - np.zeros_like(x)
    assert metrics.snr_db(x, noise) == pytest.approx(10.0, abs=0.5)


def test_ber():
    ref = np.array([0, 1, 1, 0, 1])
    est = np.array([0, 1, 0, 0, 1])
    assert metrics.ber(ref, est) == pytest.approx(0.2)
