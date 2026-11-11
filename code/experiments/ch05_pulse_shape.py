"""Chapter 5 demo experiment: isolated pulse shape and its spectrum.

This is the reference implementation behind the pulse-shape discussion in
chapter 5 (section 5.3).  It plots the longitudinal (Lorentzian) and
perpendicular (Gaussian) isolated pulses for several PW50 values, together
with their normalized magnitude spectra, and writes the sampled curves to CSV.

Usage::

    python code/experiments/ch05_pulse_shape.py --out figures/ch05/fig05-05-pulse-shape.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hddbook import config, io, plotting, signals  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default=str(config.FIG_DIR / "ch05" / "fig05-05-pulse-shape.png"))
    p.add_argument("--csv", default=str(config.REPO_ROOT / "code" / "results" / "ch05_pulse_shape.csv"))
    p.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    p.add_argument("--quick", action="store_true", help="fewer points for smoke tests")
    return p


def main(argv: list[str] | None = None) -> Path:
    args = build_parser().parse_args(argv)
    plotting.apply_style()
    n = 400 if args.quick else 2000
    t = np.linspace(-300.0, 300.0, n)  # nm
    pw50_values = (40.0, 60.0, 80.0)
    freq = np.linspace(0.0, 0.06, n // 2)  # 1/nm

    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.0))
    rows: list[list[float]] = []

    for pw50 in pw50_values:
        lmr = signals.longitudinal_pulse(t, pw50)
        pmr = signals.perpendicular_pulse(t, pw50)
        axes[0].plot(t, lmr, label=f"LMR PW50={pw50:.0f} nm")
        axes[0].plot(t, pmr, linestyle="--", label=f"PMR PW50={pw50:.0f} nm")
        axes[1].plot(freq, signals.pulse_spectrum(freq, pw50, "longitudinal"), label=f"LMR PW50={pw50:.0f} nm")
        axes[1].plot(
            freq,
            signals.pulse_spectrum(freq, pw50, "perpendicular"),
            linestyle="--",
            label=f"PMR PW50={pw50:.0f} nm",
        )
        for tt, ll, pp in zip(t[:: max(1, n // 200)], lmr[:: max(1, n // 200)], pmr[:: max(1, n // 200)]):
            rows.append([float(pw50), float(tt), float(ll), float(pp)])

    axes[0].set_xlabel("时间 t / nm")
    axes[0].set_ylabel("归一化幅度")
    axes[0].set_title("(a) 孤立重放脉冲")
    axes[0].legend(fontsize=7, ncol=1)
    axes[1].set_xlabel("空间频率 f / nm$^{-1}$")
    axes[1].set_ylabel("归一化幅度谱")
    axes[1].set_title("(b) 脉冲幅度谱")
    axes[1].legend(fontsize=7, ncol=1)
    axes[1].set_yscale("log")

    out = plotting.save_figure(fig, args.out)
    io.write_csv(args.csv, ["pw50_nm", "t_nm", "lmr_amp", "pmr_amp"], rows)
    io.record_figure(
        "fig:5-5",
        chapter=5,
        section="5.3",
        title="纵向/垂直孤立重放脉冲及其幅度谱（PW50 依赖）",
        script="code/experiments/ch05_pulse_shape.py",
        command=f"python code/experiments/ch05_pulse_shape.py --out {Path(args.out).relative_to(config.REPO_ROOT)}",
        output=out,
        source="原创（Lorentz/Gaussian 教科书模型；参考编码书 Ch2 图2.5 的重绘思路）",
        license="CC BY 4.0（原创）",
        status="draft",
    )
    print(f"figure: {out}")
    print(f"csv:     {args.csv}")
    return out


if __name__ == "__main__":
    main()
