"""例 5-4：介质噪声谱分解（DC 剩磁 / 翻转 / 总噪声）。

对应第 5 章 5.4 节，生成图 5-7（介质噪声谱分解与方形度依赖）。DC 剩磁噪声
按源书式 2.57、翻转噪声按式 2.60，方形度通过式 2.56 的磁化方差与式 2.62 的
σj/σa 关联；垂直介质方形度=1 时 DC 分量消失（图 5-7(b) 的端点）。

参数取正文例 5-4：S_cross=0.68–2.5⟨D⟩、Mr/Ms=0.6–1.0、σV/⟨V⟩=0.1–0.3。

用法::

    python code/experiments/ch05_media_noise.py --out figures/ch05
    python code/experiments/ch05_media_noise.py --out figures/ch05 --quick
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hddbook import config, io, plotting, recording  # noqa: E402

# ---- 例 5-4 默认参数 ----
PW50_NM = 74.0
G_NM = 50.0
DELTA_NM = 5.0
A_NM = 5.0
GAMMA_NM = 15.0
GRAIN_NM = 10.0
MR_OVER_MS = 0.8
SIGMA_V = 0.2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default=str(config.FIG_DIR / "ch05"), help="图件输出目录（也接受单个 .png 路径）")
    p.add_argument("--csv", default=str(config.REPO_ROOT / "code" / "results" / "ch05_media_noise.csv"))
    p.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    p.add_argument("--quick", action="store_true", help="降低采样点，供 pytest 冒烟测试")
    return p


def _resolve_outdir(out: str, primary_name: str) -> tuple[Path, Path]:
    p = Path(out)
    if p.suffix.lower() == ".png":
        return p.parent, p
    return p, p / primary_name


def draw_media_noise(out_path: Path, *, quick: bool = False) -> Path:
    """图 5-7：介质噪声谱分解（DC 剩磁/翻转/总噪声）与方形度依赖。"""
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.2), constrained_layout=True)

    # (a) 噪声谱分解：横轴用归一化波数 k·PW50
    n = 120 if quick else 400
    k = np.linspace(2e-3, 0.12, n)  # 1/nm
    kx = k * PW50_NM
    dc = recording.dc_noise_psd(
        k, pw50_nm=PW50_NM, mr_over_ms=MR_OVER_MS, sigma_v_over_v=SIGMA_V,
        s_cross_nm=1.0 * GRAIN_NM, s_down_nm=1.0 * GRAIN_NM, w_read_nm=200.0,
    )
    tr = recording.transition_noise_psd(
        k, g_nm=G_NM, delta_nm=DELTA_NM, a_nm=A_NM, gamma_nm=GAMMA_NM,
        sigma_v_over_v=SIGMA_V, s_cross_nm=1.5 * GRAIN_NM, w_read_nm=200.0,
    )
    total = dc + tr
    norm = np.max(total)
    ax1.loglog(kx, np.maximum(dc / norm, 1e-6), color="#1f77b4", lw=1.5, label=r"DC 剩磁分量（式 5-11）")
    ax1.loglog(kx, np.maximum(tr / norm, 1e-6), color="#d95f02", lw=1.5, label=r"翻转分量（式 5-12）")
    ax1.loglog(kx, np.maximum(total / norm, 1e-6), color="k", lw=1.8, label="总噪声")
    ax1.axvline(np.pi, color="gray", ls=":", lw=0.8)
    ax1.text(np.pi * 1.04, 0.02, r"$k=\pi/\mathrm{PW}_{50}$", fontsize=6.5, color="gray", rotation=90, va="bottom")
    ax1.set_xlabel(r"归一化波数 $k\cdot\mathrm{PW}_{50}$")
    ax1.set_ylabel("归一化噪声 PSD / (a.u.)")
    ax1.set_title("(a) 介质噪声谱分解（纵向，$M_r/M_s=0.8$）", fontsize=9)
    ax1.set_ylim(1e-5, 2.0)
    ax1.legend(fontsize=6.5, loc="lower left")
    ax1.grid(alpha=0.3, which="both")
    plotting.plain_log_axis(ax1)

    # (b) DC 噪声随方形度变化：方形度=1 时消失
    mr = np.linspace(0.6, 1.0, 80 if quick else 200)
    var = np.array([recording.magnetization_variance(x) for x in mr])
    ax2.plot(mr, var, color="#1f77b4", lw=1.8, label=r"$\langle M^2\rangle-M_r^2$（式 5-11）")
    ax2.plot([1.0], [0.0], "o", color="#b2182b", ms=6)
    ax2.annotate("垂直方形度=1\nDC 分量消失", xy=(0.995, 0.002), xytext=(0.76, 0.072),
                 fontsize=7, color="#b2182b",
                 arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#b2182b"))
    ax2.set_xlabel(r"剩磁方形度 $M_r/M_s$")
    ax2.set_ylabel(r"归一化磁化方差 $\langle M^2\rangle-M_r^2$")
    ax2.set_title("(b) DC 剩磁噪声随方形度的变化", fontsize=9)
    ax2.set_xlim(0.58, 1.02)
    ax2.set_ylim(-0.005, 0.09)
    ax2.grid(alpha=0.3)
    ax2.legend(fontsize=6.5, loc="upper right")

    rows = [[float(a), float(b), float(c), float(d), float(e)] for a, b, c, d, e in zip(kx, dc / norm, tr / norm, total / norm, k)]
    return plotting.save_figure(fig, out_path), rows, var


def main(argv: list[str] | None = None) -> Path:
    args = build_parser().parse_args(argv)
    plotting.apply_style()
    config.rng(args.seed)

    outdir, primary = _resolve_outdir(args.out, "fig05-07-media-noise.png")
    config.ensure_dir(outdir)

    fig_path, rows, var = draw_media_noise(primary, quick=args.quick)
    csv_path = io.write_csv(
        args.csv,
        ["k_pw50", "psd_dc_norm", "psd_tr_norm", "psd_total_norm", "k_nm_inv"],
        rows,
    )
    # 方形度扫描单独落盘，便于正文引用具体数值
    sq_rows = [[float(m), float(recording.magnetization_variance(m))] for m in np.linspace(0.6, 1.0, 9)]
    sq_csv = io.write_csv(Path(args.csv).with_name(Path(args.csv).stem + "_squareness.csv"),
                          ["mr_over_ms", "magnetization_variance"], sq_rows)

    rel = io.repo_relative
    io.record_figure(
        "fig:5-7",
        chapter=5,
        section="5.4.1",
        title="介质噪声谱分解（DC 剩磁/翻转/总噪声）",
        script="code/experiments/ch05_media_noise.py",
        command=f"python code/experiments/ch05_media_noise.py --out {rel(outdir)}",
        output=fig_path,
        source="原创计算（式 5-11/5-12；据编码书 Ch2 §2.4.1 的噪声谱分解）",
        license="CC BY 4.0（原创）",
    )
    print(f"figure: {fig_path}")
    print(f"csv:    {csv_path}")
    print(f"csv:    {sq_csv}")
    return fig_path


if __name__ == "__main__":
    main()
