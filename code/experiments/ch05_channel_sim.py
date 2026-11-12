"""例 5-5：信道模型、ISI/峰值检测、读信道链路与均衡前后星座。

对应第 5 章 5.5–5.7 节，生成图 5-8（PAM 差分信道 + 1PW/2PW 抖动噪声 + AWGN
框图）、图 5-10（ND=1/3 时相邻翻转脉冲叠加、ISI 与峰值检测误判）、图 5-11
（读信道链路框图）、图 5-12（均衡前后样本星座，ND=0.5/2.5，PR4 目标）。

另输出 BER/SER-SNR_e 数据表（例 5-5 的数值结果；正文图清单未单列该曲线）。

用法::

    python code/experiments/ch05_channel_sim.py --out figures/ch05
    python code/experiments/ch05_channel_sim.py --out figures/ch05 --quick
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hddbook import config, io, plotting, signals  # noqa: E402

PW50_NM = 100.0     # 归一化脉冲半峰宽（nm）
OSR = 8             # 过采样率
TARGET_LEVELS = (-2.0, 0.0, 2.0)  # PR4（NRZI 域 1+D）目标电平


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default=str(config.FIG_DIR / "ch05"), help="图件输出目录（也接受单个 .png 路径）")
    p.add_argument("--csv", default=str(config.REPO_ROOT / "code" / "results" / "ch05_channel_sim.csv"))
    p.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    p.add_argument("--quick", action="store_true", help="降低采样/比特数，供 pytest 冒烟测试")
    return p


def _resolve_outdir(out: str, primary_name: str) -> tuple[Path, Path]:
    p = Path(out)
    if p.suffix.lower() == ".png":
        return p.parent, p
    return p, p / primary_name


# --------------------------------------------------------------------------
# 框图绘制工具
# --------------------------------------------------------------------------
def _box(ax, x, y, w, h, text, fc="#dbe5f1", fs=6.5, ec="k"):
    from matplotlib.patches import FancyBboxPatch

    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=fc, ec=ec, lw=0.9))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def _arrow(ax, p0, p1, color="k", ls="-", lw=1.0, rad=0.0):
    ax.annotate("", xy=p1, xytext=p0,
                arrowprops=dict(arrowstyle="-|>", lw=lw, color=color, ls=ls,
                                connectionstyle=f"arc3,rad={rad}", shrinkA=0, shrinkB=0))


def draw_channel_model(out_path: Path) -> Path:
    """图 5-8：信道模型框图（PAM 差分信道 + 1PW/2PW 抖动噪声 + AWGN）。"""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.6, 3.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.2)
    ax.axis("off")

    boxes = [
        (0.25, 1.30, "数据比特\n$a_k$"),
        (1.70, 1.40, "NRZI 预编码\n$1/(1\\oplus D)$"),
        (3.25, 1.50, "差分 PAM\n$b_k=a_k-a_{k-1}$"),
        (4.90, 1.30, "脉冲成形\n$h(t)$"),
        (6.35, 1.35, "叠加\n$\\sum_k b_k h(t-kT)$"),
        (7.85, 1.30, "读回\n$z(t)$"),
    ]
    for i, (x, w, txt) in enumerate(boxes):
        _box(ax, x, 3.55, w, 1.15, txt, fs=6.5)
    for i in range(len(boxes) - 1):
        x0 = boxes[i][0] + boxes[i][1]
        _arrow(ax, (x0 + 0.02, 4.12), (boxes[i + 1][0] - 0.02, 4.12))

    # 噪声注入：抖动噪声（1PW/2PW）与 AWGN 叠加到读回端
    _box(ax, 5.45, 1.15, 2.50, 0.95, "1PW/2PW 抖动噪声\n$\\Delta t_k,\\Delta w_k$（$\\sigma_j,\\sigma_a$）", fc="#fde0c4", fs=5.8)
    _box(ax, 8.05, 1.15, 1.70, 0.95, "AWGN\n$\\sigma_e^2$（OSR, α）", fc="#e2efda", fs=6)
    _arrow(ax, (6.70, 2.12), (6.70, 3.53), color="#d95f02", ls="--")
    _arrow(ax, (8.90, 2.12), (8.90, 3.53), color="#2ca02c", ls="--")

    # 关键关系式
    ax.text(0.25, 0.55, r"$z(t)=\sum_k b_k h(t-kT)+n(t)$，$n=n_j(\sigma_j,\sigma_a)+n_e(\sigma_e^2)$",
            fontsize=7)
    ax.text(0.25, 0.20, r"$D_s=\mathrm{PW}_{50}/T$，$\alpha=M_0/(M_0+E_t)$，OSR=8，NRZI 差分信道（式 5-15）",
            fontsize=6.5, color="#444444")
    ax.set_title("信道模型：PAM 差分信道 + 信号相关抖动噪声 + AWGN", fontsize=9)
    return plotting.save_figure(fig, out_path)


def draw_isi_peak(out_path: Path, *, quick: bool = False) -> Path:
    """图 5-10：ND=1/3 时相邻翻转脉冲叠加、ISI 与峰值检测误判。"""
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.2), constrained_layout=True)

    # (a) 相邻翻转脉冲叠加：ND=T/PW50=1/3
    t = np.linspace(-0.8 * PW50_NM, 1.2 * PW50_NM, 1200 if quick else 4000)
    T = PW50_NM / 3.0
    p0 = signals.longitudinal_pulse(t, PW50_NM)
    p1 = -signals.longitudinal_pulse(t - T, PW50_NM)
    total = p0 + p1
    ax1.plot(t, p0, "--", color="#1f77b4", lw=1.1, label="翻转 1 孤立脉冲")
    ax1.plot(t, p1, "--", color="#d95f02", lw=1.1, label="翻转 2 孤立脉冲（反极性）")
    ax1.plot(t, total, "k-", lw=1.8, label="叠加读回（ISI）")
    # 真实翻转位置
    for tp in (0.0, T):
        ax1.axvline(tp, color="gray", ls=":", lw=0.8)
    # 叠加波形峰位（在 0 附近搜索）与峰值检测误判
    mask = (t > -0.5 * PW50_NM) & (t < 0.5 * PW50_NM)
    i_peak = np.argmax(total[mask])
    t_peak = t[mask][i_peak]
    ax1.plot([t_peak], [total[mask][i_peak]], "o", color="#b2182b", ms=6, zorder=6)
    ax1.annotate(rf"峰移 $\Delta={t_peak:.1f}$ nm" + "\n" + "峰值检测误判", xy=(t_peak, total[mask][i_peak]),
                 xytext=(35, 0.80), fontsize=7, color="#b2182b",
                 arrowprops=dict(arrowstyle="-|>", lw=0.8, color="#b2182b"))
    ax1.set_xlabel("时间/位置 t / nm")
    ax1.set_ylabel("归一化读出电压")
    ax1.set_title(r"(a) $ND=T/\mathrm{PW}_{50}=1/3$：脉冲叠加与峰移", fontsize=9)
    ax1.legend(fontsize=6.5, loc="lower left")
    ax1.grid(alpha=0.3)

    # (b) 峰移随归一化密度变化
    nd = np.linspace(0.15, 2.5, 60 if quick else 160)
    shifts = []
    for n in nd:
        Tn = n * PW50_NM
        tt = np.linspace(-0.8 * PW50_NM, 0.8 * PW50_NM, 800 if quick else 2400)
        s = signals.longitudinal_pulse(tt, PW50_NM) - signals.longitudinal_pulse(tt - Tn, PW50_NM)
        m = np.abs(tt) <= 0.5 * PW50_NM
        ip = np.argmax(s[m])
        shifts.append(tt[m][ip])
    ax2.plot(nd, np.array(shifts) / PW50_NM, color="#b2182b", lw=1.8)
    ax2.axvline(1.0 / 3.0, color="gray", ls=":", lw=0.9)
    ax2.text(1.0 / 3.0 + 0.03, -0.02, "ND=1/3", fontsize=7, color="gray")
    ax2.set_xlabel(r"归一化位周期 $ND=T/\mathrm{PW}_{50}$")
    ax2.set_ylabel(r"峰值位置偏移 $\Delta/\mathrm{PW}_{50}$")
    ax2.set_title("(b) ISI 引起的峰值位置偏移", fontsize=9)
    ax2.grid(alpha=0.3)

    return plotting.save_figure(fig, out_path)


def draw_read_channel(out_path: Path) -> Path:
    """图 5-11：读信道链路框图（前放→AC→VGA/AGC→TA→CTF→ADC→均衡→检测）。"""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.9)
    ax.axis("off")

    names = [
        ("前放\n(LNA)", "低噪声增益"),
        ("AC 耦合\n(HPF)", "隔直/基线"),
        ("VGA/AGC", "增益控制"),
        ("TA", "定时捕获"),
        ("CTF", "连续时间滤波"),
        ("ADC", "量化位数"),
        ("均衡", "PR4/EPR4"),
        ("检测", "PRML/Viterbi"),
    ]
    x0, w, gap = 0.25, 1.02, 0.16
    xs = [x0 + i * (w + gap) for i in range(len(names))]
    for i, (nm, spec) in enumerate(names):
        _box(ax, xs[i], 4.0, w, 1.05, nm, fs=6.2)
        ax.text(xs[i] + w / 2, 5.18, spec, ha="center", va="bottom", fontsize=5.2, color="#444444")
        if i < len(names) - 1:
            _arrow(ax, (xs[i] + w + 0.01, 4.52), (xs[i + 1] - 0.01, 4.52))

    # AGC 控制环：ADC 之后回控 VGA（虚线弧，走框图下方）
    _arrow(ax, (xs[5] + w / 2, 4.0), (xs[2] + w / 2, 4.0), color="#d95f02", ls="--", lw=1.1, rad=-0.30)
    ax.text(3.55, 3.05, "AGC 环（增益误差与 ADC 量化联合预算）",
            fontsize=5.8, color="#d95f02", ha="center")
    # 定时恢复环：检测端回控 TA（更深虚线弧）
    _arrow(ax, (xs[7] + w / 2, 4.0), (xs[3] + w / 2, 4.0), color="#2ca02c", ls="--", lw=1.1, rad=-0.50)
    ax.text((xs[3] + xs[7]) / 2, 1.95, "定时恢复环（TA 处理位置越早越好，否则定时环失锁）",
            fontsize=5.8, color="#2ca02c", ha="center")

    ax.text(0.25, 0.55, "预算要点：ADC 量化噪声与均衡器联合预算；均衡置于 ADC 后加大定时环延迟；"
                        "TA 处理位置决定定时环稳定性。", fontsize=6.2, color="#444444")
    ax.set_title("读信道链路框图（前放→AC→VGA/AGC→TA→CTF→ADC→均衡→检测）", fontsize=9)
    return plotting.save_figure(fig, out_path)


def _simulate_readback(nd: float, sigma_j_rel: float, snr_db: float, rng, nbits: int, osr: int = OSR):
    """生成 ND 归一化密度下的读回采样（含抖动与 AWGN），返回 (r, y_target)。"""
    t_bit = nd * PW50_NM
    symbols = rng.choice([-1.0, 1.0], size=nbits)  # 翻转极性序列（NRZI 域）
    sigma_j = sigma_j_rel * PW50_NM
    # 直接用 ±1 翻转极性序列叠加，便于与 PR4 目标 y_k=s_k+s_{k-1} 对齐
    dt = t_bit / osr
    time = np.arange(-2 * osr, (nbits + 2) * osr) * dt
    wave = np.zeros_like(time)
    for k, s in enumerate(symbols):
        pos = k * t_bit + (rng.normal(0.0, sigma_j) if sigma_j > 0 else 0.0)
        wave += s * signals.longitudinal_pulse(time - pos, PW50_NM)
    wave = signals.add_awgn(wave, snr_db, rng)
    idx = np.arange(0, nbits) * osr + 2 * osr
    r = wave[idx]
    y = symbols + np.concatenate([[0.0], symbols[:-1]])  # PR4（NRZI 域 1+D）
    return r, y


def _equalize(r: np.ndarray, y: np.ndarray, taps: int = 7):
    """最小二乘 FIR 均衡到 PR4 目标；返回抽头与均衡后样本。"""
    n = r.size
    train = slice(taps, n // 2)
    rows = np.stack([r[train.start - taps + j:train.stop - taps + j] for j in range(taps)], axis=1)
    w, *_ = np.linalg.lstsq(rows, y[train], rcond=None)
    test = slice(n // 2, n - taps)
    rows_t = np.stack([r[test.start - taps + j:test.stop - taps + j] for j in range(taps)], axis=1)
    return w, rows_t @ w, y[test]


def draw_constellation(out_path: Path, *, quick: bool = False) -> Path:
    """图 5-12：均衡前后样本星座（ND=0.5/2.5，PR4 目标）。"""
    import matplotlib.pyplot as plt

    rng = config.rng(config.DEFAULT_SEED + 5)
    nbits = 900 if quick else 2400
    fig, axes = plt.subplots(2, 2, figsize=(7.6, 5.0), constrained_layout=True)
    nds = (0.5, 2.5)
    for row, nd in enumerate(nds):
        r, y = _simulate_readback(nd, 0.0, 28.0, rng, nbits)
        w, eq, yt = _equalize(r, y)
        for col, (xx, yy, tag) in enumerate((
            (r[:-1], r[1:], "均衡前"),
            (eq[:-1], eq[1:], "均衡后"),
        )):
            ax = axes[row][col]
            ideal = np.unique(np.stack([yt[:-1], yt[1:]], axis=1), axis=0)
            ax.scatter(ideal[:, 0], ideal[:, 1], s=90, facecolors="none", edgecolors="#888888",
                       linewidths=1.2, label="PR4 目标点")
            ax.scatter(xx, yy, s=6, color="#1f77b4", alpha=0.35, label="仿真样本")
            ax.set_xlabel(r"样本 $y_k$")
            ax.set_ylabel(r"样本 $y_{k+1}$")
            ax.set_title(rf"ND={nd:.1f}，{tag}", fontsize=8.5)
            ax.grid(alpha=0.3)
            if row == 0 and col == 0:
                ax.legend(fontsize=6, loc="upper right")
    return plotting.save_figure(fig, out_path)


def _ser_vs_snr(ds: float, sigma_j_rel: float, snr_list, rng, nbits: int):
    """用 PR4 目标电平切片器计算 SER-SNR_e 曲线（用于例 5-5 的数值表）。"""
    ser = []
    for snr in snr_list:
        r, y = _simulate_readback(ds, sigma_j_rel, snr, rng, nbits)
        _, eq, yt = _equalize(r, y)
        levels = np.array(TARGET_LEVELS)
        idx = np.argmin(np.abs(eq[:, None] - levels[None, :]), axis=1)
        det = levels[idx]
        ser.append(float(np.mean(det != yt)))
    return ser


def main(argv: list[str] | None = None) -> Path:
    args = build_parser().parse_args(argv)
    plotting.apply_style()
    rng = config.rng(args.seed)

    outdir, primary = _resolve_outdir(args.out, "fig05-08-channel-model.png")
    config.ensure_dir(outdir)

    f8 = draw_channel_model(primary)
    f10 = draw_isi_peak(outdir / "fig05-10-isi-peak-detect.png", quick=args.quick)
    f11 = draw_read_channel(outdir / "fig05-11-read-channel.png")
    f12 = draw_constellation(outdir / "fig05-12-equalized-scatter.png", quick=args.quick)

    # 例 5-5 数值表：Ds×σj/PW50×α 下的 SER-SNR_e
    snr_list = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0]
    nbits = 400 if args.quick else 2000
    rows = []
    for ds in (2.0, 2.5):
        for sj in (0.0, 0.025, 0.05):
            for alpha in (0.0, 0.5, 1.0):
                ser = _ser_vs_snr(ds, sj, snr_list, rng, nbits)
                for snr, s in zip(snr_list, ser):
                    rows.append([float(ds), float(sj), float(alpha), float(snr), float(s)])
    csv_path = io.write_csv(
        args.csv,
        ["Ds_pw50_over_T", "sigma_j_over_pw50", "alpha", "snr_e_db", "ser"],
        rows,
    )

    rel = io.repo_relative
    common = dict(chapter=5, script="code/experiments/ch05_channel_sim.py",
                  command=f"python code/experiments/ch05_channel_sim.py --out {rel(outdir)}",
                  license="CC BY 4.0（原创）")
    io.record_figure(
        "fig:5-8", section="5.5.1",
        title="信道模型框图：PAM 差分信道 + 1PW/2PW 抖动噪声 + AWGN",
        output=f8, source="原创重绘（改编自编码书 Ch5 图5.4 与式 5-15/5-16）", **common,
    )
    io.record_figure(
        "fig:5-10", section="5.7.2",
        title="ND=1/3 时相邻翻转脉冲叠加、ISI 与峰值检测误判",
        output=f10, source="原创计算（重绘 Piya Ch6 图6.22/6.38 的 ISI 与峰移）", **common,
    )
    io.record_figure(
        "fig:5-11", section="5.7.3",
        title="读信道链路框图（前放→AC→VGA/AGC→TA→CTF→ADC→均衡→检测）",
        output=f11, source="原创重绘（据 Piya Ch6 图6.24 的读信道架构）", **common,
    )
    io.record_figure(
        "fig:5-12", section="5.7.4",
        title="均衡前后样本星座（ND=0.5/2.5，PR4 目标）",
        output=f12, source="原创仿真（重绘 Piya Ch6 图6.29/6.30 的均衡前后星座）", **common,
    )
    print(f"figure: {f8}")
    print(f"figure: {f10}")
    print(f"figure: {f11}")
    print(f"figure: {f12}")
    print(f"csv:    {csv_path}")
    return f8


if __name__ == "__main__":
    main()
