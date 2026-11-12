"""例 5-6：信道仿真器流程与 M0-α 梯度标定回路。

对应第 5 章 5.6.3 节，生成图 5-9（仿真器流程：直接法/间接法分支与梯度标定
回路，含标定收敛轨迹）。参数取正文例 5-6：目标 α=50%、λ=0.9（抖动/展宽功率
比）、初始 σj=0.05PW50 量级、梯度步长 λ_iter=2；要求 <20 次收敛、M0 标定
误差 <1%。

用法::

    python code/experiments/ch05_snr_calib.py --out figures/ch05
    python code/experiments/ch05_snr_calib.py --out figures/ch05 --quick
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hddbook import config, io, plotting  # noqa: E402

ALPHA_TARGET = 0.50
SIGMA_TARGET_REL = 0.05     # 目标 σj/PW50（对应 α=50%）
SIGMA_INIT_REL = 0.08       # 初始估计（偏高 60%）
LAMBDA_ITER = 2.0           # 梯度步长（正文例 5-6）
LAMBDA_POWER = 0.9          # 抖动/展宽功率比 λ
MAX_ITER = 40


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default=str(config.FIG_DIR / "ch05"), help="图件输出目录（也接受单个 .png 路径）")
    p.add_argument("--csv", default=str(config.REPO_ROOT / "code" / "results" / "ch05_snr_calib.csv"))
    p.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    p.add_argument("--quick", action="store_true", help="减少迭代上限，供 pytest 冒烟测试")
    return p


def _resolve_outdir(out: str, primary_name: str) -> tuple[Path, Path]:
    p = Path(out)
    if p.suffix.lower() == ".png":
        return p.parent, p
    return p, p / primary_name


def _box(ax, x, y, w, h, text, fc="#dbe5f1", fs=6.2):
    from matplotlib.patches import FancyBboxPatch

    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=fc, ec="k", lw=0.9))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def _diamond(ax, cx, cy, w, h, text, fc="#fff2cc", fs=6.0):
    from matplotlib.patches import Polygon

    pts = [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)]
    ax.add_patch(Polygon(pts, closed=True, fc=fc, ec="k", lw=0.9))
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs)


def _arrow(ax, p0, p1, color="k", ls="-", lw=1.0, rad=0.0):
    ax.annotate("", xy=p1, xytext=p0,
                arrowprops=dict(arrowstyle="-|>", lw=lw, color=color, ls=ls,
                                connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


def calibrate(*, quick: bool = False):
    """M0-α 梯度标定：乘性步长保证 σj>0，返回迭代轨迹。"""
    x_t = SIGMA_TARGET_REL**2  # α=0.5 时 M0/Et=1
    u = SIGMA_INIT_REL
    trace = []
    max_iter = 12 if quick else MAX_ITER
    for it in range(max_iter):
        alpha = u**2 / (u**2 + x_t)
        m0_err = abs(u**2 - x_t) / x_t
        trace.append((it, u, alpha, m0_err))
        if m0_err < 1e-3:
            break
        # 乘性梯度更新：u <- u * exp(-λ_iter*(α-α_t))
        u = u * np.exp(-LAMBDA_ITER * (alpha - ALPHA_TARGET))
        u = float(np.clip(u, 1e-3, 1.0))
    return np.array(trace)


def draw_simulator_flow(out_path: Path, *, quick: bool = False) -> Path:
    """图 5-9：仿真器流程（直接法/间接法分支与梯度标定回路）。"""
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 4.0), constrained_layout=True)

    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis("off")
    ax1.set_title("(a) 仿真器流程：直接法/间接法与梯度标定回路", fontsize=8.5)

    _box(ax1, 3.1, 8.9, 3.8, 0.75, "参数集：Ds、α、OSR、σj/PW50、码率", fc="#e2efda", fs=5.8)
    _diamond(ax1, 5.0, 7.55, 2.4, 1.0, "仿真方法？", fs=5.8)
    _arrow(ax1, (5.0, 8.88), (5.0, 8.06))
    _box(ax1, 0.9, 6.05, 2.9, 0.85, "直接法\nΔtk~N(0,σj^2)，含饱和效应", fc="#fde0c4", fs=5.4)
    _box(ax1, 6.1, 6.05, 3.0, 0.85, "间接法\nM0-α 标定 + 梯度迭代", fc="#fde0c4", fs=5.4)
    _arrow(ax1, (4.35, 7.35), (2.35, 6.91), rad=0.1)
    _arrow(ax1, (5.65, 7.35), (7.6, 6.91), rad=-0.1)

    _box(ax1, 2.9, 4.85, 4.2, 0.75, "波形合成 z(t)=Σbk h(t-kT)", fs=5.6)
    _arrow(ax1, (2.35, 6.04), (3.6, 5.61), rad=0.1)
    _arrow(ax1, (7.6, 6.04), (6.4, 5.61), rad=-0.1)
    _box(ax1, 2.9, 3.75, 4.2, 0.75, "噪声叠加 σe^2=OSR·10^(-z/10)EiDs/2", fs=5.4)
    _arrow(ax1, (5.0, 4.84), (5.0, 4.51))
    _box(ax1, 2.9, 2.65, 4.2, 0.75, "BER / SNR 评估", fs=5.8)
    _arrow(ax1, (5.0, 3.74), (5.0, 3.41))
    _diamond(ax1, 5.0, 1.55, 2.8, 1.1, "α 达到目标？", fs=5.8)
    _arrow(ax1, (5.0, 2.64), (5.0, 2.11))
    _box(ax1, 7.2, 1.15, 2.4, 0.8, "输出 BER-SNR\n曲线族", fc="#e2efda", fs=5.4)
    _arrow(ax1, (6.4, 1.55), (7.19, 1.55))
    ax1.text(6.5, 1.72, "是", fontsize=6)
    _box(ax1, 0.35, 1.15, 2.6, 0.8, "梯度更新 λ_iter\n(dM0/dσj)", fc="#f8cbad", fs=5.4)
    _arrow(ax1, (3.6, 1.55), (2.96, 1.55))
    ax1.text(3.2, 1.72, "否", fontsize=6)
    # 标定回路：梯度更新回到间接法
    _arrow(ax1, (1.65, 1.96), (7.6, 6.04), color="#b2182b", ls="--", lw=1.0, rad=-0.35)
    ax1.text(2.0, 2.55, "梯度标定回路（<20 次）", fontsize=5.6, color="#b2182b", rotation=18)
    ax1.text(0.2, 0.35, "注：λ_iter=2；直接法用于验证饱和效应，间接法用于 M0 与 α 的定量标定。",
             fontsize=5.4, color="#444444")

    # (b) 收敛轨迹
    tr = calibrate(quick=quick)
    it = tr[:, 0]
    u = tr[:, 1]
    alpha = tr[:, 2]
    m0_err = tr[:, 3]
    ax2.semilogy(it, np.maximum(u, 1e-4), "o-", color="#1f77b4", ms=3, lw=1.4, label=r"$\sigma_j/\mathrm{PW}_{50}$")
    ax2.semilogy(it, np.maximum(m0_err, 1e-6), "s--", color="#d95f02", ms=3, lw=1.3, label="M0 标定误差")
    ax2.axhline(SIGMA_TARGET_REL, color="#1f77b4", ls=":", lw=0.8)
    ax2.axhline(1e-2, color="#d95f02", ls=":", lw=0.8)
    ax2.set_xlabel("迭代次数")
    ax2.set_ylabel("归一化数值（对数刻度）")
    ax2.set_title("(b) 梯度标定收敛轨迹（例 5-6）", fontsize=8.5)
    ax2.legend(fontsize=6.5, loc="lower left")
    ax2.grid(alpha=0.3, which="both")
    plotting.plain_log_axis(ax2, axis="y")
    n_conv = int(np.flatnonzero(m0_err < 1e-2)[0]) + 1 if np.any(m0_err < 1e-2) else len(it)
    ax2.text(0.55 * len(it), SIGMA_TARGET_REL * 0.45,
             rf"目标 $\sigma_j/\mathrm{{PW}}_{{50}}={SIGMA_TARGET_REL}$" "\n"
             rf"{n_conv} 次收敛（<20）" "\n"
             rf"$\alpha$ 终值={alpha[-1]:.3f}",
             fontsize=6.5, bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#1f77b4", alpha=0.9))

    return plotting.save_figure(fig, out_path), tr


def main(argv: list[str] | None = None) -> Path:
    args = build_parser().parse_args(argv)
    plotting.apply_style()
    config.rng(args.seed)

    outdir, primary = _resolve_outdir(args.out, "fig05-09-simulator-flow.png")
    config.ensure_dir(outdir)

    fig_path, tr = draw_simulator_flow(primary, quick=args.quick)
    rows = [[int(a), float(b), float(c), float(d)] for a, b, c, d in tr]
    csv_path = io.write_csv(args.csv, ["iteration", "sigma_j_over_pw50", "alpha_est", "m0_error"], rows)

    rel = io.repo_relative
    io.record_figure(
        "fig:5-9",
        chapter=5,
        section="5.6.3",
        title="仿真器流程：直接法/间接法分支与梯度标定回路",
        script="code/experiments/ch05_snr_calib.py",
        command=f"python code/experiments/ch05_snr_calib.py --out {rel(outdir)}",
        output=fig_path,
        source="原创重绘（改编自编码书 Ch6 图6.9/6.13 的仿真流程与式 6.42–6.46）",
        license="CC BY 4.0（原创）",
    )
    print(f"figure: {fig_path}")
    print(f"csv:    {csv_path}")
    print(f"iter:   {len(tr)} (target <20), final sigma={tr[-1,1]:.4f}, alpha={tr[-1,2]:.3f}, "
          f"m0_err={tr[-1,3]:.2e}")
    return fig_path


if __name__ == "__main__":
    main()
