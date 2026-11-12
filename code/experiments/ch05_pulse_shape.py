"""例 5-2：互易原理读出几何与纵向/垂直孤立重放脉冲。

对应第 5 章 5.3 节，生成图 5-4（互易原理读出几何与 Φ(k) 势函数链）、图 5-5
（纵向精确积分 vs Lorentz/Gauss/Voigt（η=0.43）与垂直 erf/Gaussian 对照）。

参数取正文例 5-2 / 表 5-2：g=50 nm、δ=5 nm、a=5 nm、γ=15 nm、G=20–100 nm。
纵向精确脉冲按源书式 2.27 数值积分；Voigt 权重 η 取教材标定值 0.43（式 2.39），
并对精确曲线做单参数拟合，要求残差 <3%。

用法::

    python code/experiments/ch05_pulse_shape.py --out figures/ch05
    python code/experiments/ch05_pulse_shape.py --out figures/ch05 --quick
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hddbook import config, io, plotting, recording  # noqa: E402

# ---- 例 5-2 默认参数（nm；CGS 高斯制）----
G_NM = 50.0          # GMR 读出间隙 g=(G-δ)/2
DELTA_NM = 5.0       # GMR 自由层厚度 δ
A_NM = 5.0           # 翻转参数 a
GAMMA_NM = 15.0      # 净磁间距 γ=d+t/2
ETA_BOOK = 0.43      # 教材 Voigt 权重（源书图 2.5 标定值）
D_NM = 12.5          # 垂直记录磁头-介质间距 d（γ=15、t=5）
T_NM = 5.0           # 膜厚 t
S_NM = 5.0           # 介质-SUL 间距 s


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default=str(config.FIG_DIR / "ch05"), help="图件输出目录（也接受单个 .png 路径）")
    p.add_argument("--csv", default=str(config.REPO_ROOT / "code" / "results" / "ch05_pulse_shape.csv"))
    p.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    p.add_argument("--quick", action="store_true", help="降低积分网格，供 pytest 冒烟测试")
    return p


def _resolve_outdir(out: str, primary_name: str) -> tuple[Path, Path]:
    p = Path(out)
    if p.suffix.lower() == ".png":
        return p.parent, p
    return p, p / primary_name


def draw_reciprocity(out_path: Path, *, quick: bool = False) -> Path:
    """图 5-4：互易原理读出几何与 Φ(k) 势函数链。"""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.4), constrained_layout=True)

    # ---- (a) 读出几何示意 ----
    ax1.set_xlim(-330, 330)
    ax1.set_ylim(-90, 200)
    ax1.axis("off")
    ax1.set_aspect("auto")
    ax1.set_title("(a) GMR 互易读出几何（屏蔽间距 G、自由层 δ、净磁间距 γ）", fontsize=8.5)

    # 介质与面内磁化
    ax1.add_patch(Rectangle((-240, 0), 480, 40, fc="#e8d9b8", ec="k", lw=0.9))
    for xs in (-200, -150, -100, -50):
        ax1.annotate("", xy=(xs - 20, 20), xytext=(xs, 20), arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#1f4e79"))
    for xs in (50, 100, 150, 200):
        ax1.annotate("", xy=(xs + 20, 20), xytext=(xs, 20), arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#1f4e79"))
    ax1.text(0, 34, r"$M(x)=M_r\tanh[2(x-x_0)/(\pi a)]$", fontsize=7.5, ha="center", color="#b2182b")

    # 屏蔽层 + GMR 叠层 + 自由层
    ax1.add_patch(Rectangle((-150, 110), 120, 40, fc="#9fb3c8", ec="k", lw=0.9))
    ax1.add_patch(Rectangle((30, 110), 120, 40, fc="#9fb3c8", ec="k", lw=0.9))
    ax1.add_patch(Rectangle((-30, 110), 60, 40, fc="#f4b183", ec="k", lw=0.9))
    ax1.add_patch(Rectangle((-3, 110), 6, 40, fc="#c55a11", ec="k", lw=0.8))
    ax1.text(-95, 130, "屏蔽层", fontsize=7.5, ha="center", va="center")
    ax1.text(95, 130, "屏蔽层", fontsize=7.5, ha="center", va="center")
    ax1.text(0, 130, "GMR\n叠层", fontsize=6.8, ha="center", va="center")
    ax1.plot([-240, 240], [110, 110], "k--", lw=0.8)
    ax1.text(-328, 113, "ABS", fontsize=7, va="bottom")

    # 虚拟磁位势 Φ 等值线（示意，向介质内衰减）
    for r, col in zip((25, 45, 65), ("#7f7f7f", "#999999", "#b3b3b3")):
        th = np.linspace(0.05, np.pi - 0.05, 120)
        ax1.plot(0.9 * r * np.cos(th), 110 - r * np.sin(th) * 1.0, color=col, lw=0.9, ls="--")
    ax1.text(58, 72, r"$\Phi(x,y)$", fontsize=8, color="#555555")

    # 尺寸标注
    ax1.annotate("", xy=(-30, 165), xytext=(30, 165), arrowprops=dict(arrowstyle="<|-|>", lw=0.9, color="#333333"))
    ax1.text(-45, 165, "G", fontsize=8, ha="right", va="center")
    ax1.annotate("", xy=(0, 40), xytext=(0, 110), arrowprops=dict(arrowstyle="<|-|>", lw=0.9, color="#333333"))
    ax1.text(-14, 76, r"$\gamma$", fontsize=9, ha="right")
    ax1.annotate("", xy=(180, 110), xytext=(180, 150), arrowprops=dict(arrowstyle="<|-|>", lw=0.9, color="#333333"))
    ax1.text(188, 130, "h", fontsize=8)
    ax1.annotate("自由层 δ", xy=(3, 148), xytext=(60, 165), fontsize=7,
                 arrowprops=dict(arrowstyle="-|>", lw=0.7, color="#c55a11"))
    ax1.text(-325, 62, r"$V\propto\int\Phi\,\nabla\!\cdot\!\vec{M}\,dx\,dy$", fontsize=8.5)

    # ---- (b) Φ(k) 势函数链 ----
    k = np.logspace(np.log10(2e-3), np.log10(0.15), 200 if quick else 600)
    phi = recording.head_potential_ft(k, g_nm=G_NM, delta_nm=DELTA_NM, gamma_nm=GAMMA_NM)
    mag = recording.transition_magnetization_ft(k, a_nm=A_NM)
    phi_n = phi / np.max(phi)
    mag_n = mag / np.max(mag)
    v_n = phi_n * mag_n
    v_n = v_n / np.max(v_n)

    ax2.loglog(k, np.maximum(phi_n, 1e-5), color="#1f77b4", lw=1.4, label=r"$|\Phi_s(k)|e^{-k\gamma}$")
    ax2.loglog(k, mag_n, color="#d95f02", lw=1.4, label=r"$|M(k)|$")
    ax2.loglog(k, np.maximum(v_n, 1e-5), color="#2ca02c", lw=1.6, label=r"$|V(k)|=|\Phi_s(k)M(k)|$")
    ax2.axvline(2 * np.pi / G_NM, color="#777777", ls="--", lw=0.9)
    ax2.text(2 * np.pi / G_NM * 1.03, 0.25, r"$k=2\pi/g$", fontsize=7, color="#555555", rotation=90, va="top")
    ax2.set_xlabel(r"空间频率 k / nm$^{-1}$")
    ax2.set_ylabel("归一化幅度")
    ax2.set_title(r"(b) $\Phi(k)$ 势函数链：$\Phi\to M\to V$", fontsize=8.5)
    ax2.set_ylim(1e-5, 2.0)
    ax2.legend(fontsize=7, loc="lower left")
    ax2.grid(alpha=0.3, which="both")
    plotting.plain_log_axis(ax2)  # 中文字体缺 U+2212，对数刻度改用纯文本

    return plotting.save_figure(fig, out_path)


def draw_pulse_shapes(out_path: Path, *, quick: bool = False) -> Path:
    """图 5-5：纵向精确积分 vs Lorentz/Gauss/Voigt 与垂直 erf/Gaussian 对照。"""
    import matplotlib.pyplot as plt

    n = 401 if quick else 1201
    x = np.linspace(-300.0, 300.0, n)
    exact = recording.exact_replay_pulse(
        x, g_nm=G_NM, delta_nm=DELTA_NM, a_nm=A_NM, gamma_nm=GAMMA_NM,
        nk=4000 if quick else 20000,
    )

    # 以 η=0.43 固定、拟合 PW50（式 2.39），并报告相对残差
    def _fit(pw: float):
        model = recording.voigt_pulse(x, pw, ETA_BOOK)
        return model

    def _resid(p):
        model = _fit(p[0])
        scale = p[1]
        return scale * model - exact

    sol = least_squares(_resid, [70.0, 1.0], bounds=([20.0, 0.5], [200.0, 2.0]))
    pw_fit = float(sol.x[0])
    voigt = sol.x[1] * recording.voigt_pulse(x, pw_fit, ETA_BOOK)
    rms = float(np.sqrt(np.mean((voigt - exact) ** 2)))

    # 自由拟合 η 作为对照（η 弱可辨识，写入 CSV）
    def _resid_free(p):
        return p[2] * recording.voigt_pulse(x, p[1], p[0]) - exact

    sol_free = least_squares(_resid_free, [0.4, 74.0, 1.0], bounds=([0.0, 20.0, 0.5], [1.0, 200.0, 2.0]))
    eta_free = float(sol_free.x[0])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.2), constrained_layout=True)

    ax1.plot(x, exact, "k-", lw=2.0, label="精确积分（式 5-7）")
    ax1.plot(x, recording.lorentz_pulse(x, pw_fit), "--", color="#1f77b4", lw=1.3, label=r"Lorentz（$\eta=0$）")
    ax1.plot(x, recording.gauss_pulse(x, pw_fit), "-.", color="#2ca02c", lw=1.3, label=r"Gauss（$\eta=1$）")
    ax1.plot(x, voigt, ":", color="#d62728", lw=2.0, label=rf"Voigt $\eta={ETA_BOOK}$")
    ax1.set_xlim(-200, 200)
    ax1.set_ylim(-0.02, 1.08)
    ax1.set_xlabel("沿道位置 x / nm")
    ax1.set_ylabel("归一化读出电压 V/V_peak")
    ax1.set_title(r"(a) 纵向：精确积分与 Lorentz/Gauss/Voigt", fontsize=9)
    ax1.legend(fontsize=7, loc="upper right")
    ax1.grid(alpha=0.3)
    ax1.text(
        -195, 0.52,
        rf"$\eta={ETA_BOOK}$（教材标定）" "\n" rf"拟合 PW50={pw_fit:.1f} nm" "\n" rf"RMS 误差={rms*100:.1f}%",
        fontsize=7, va="center",
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#d62728", alpha=0.9),
    )

    # 垂直：未微分 erf 与微分 Gaussian
    dpw50 = recording.perpendicular_dpw50(G_NM, DELTA_NM, A_NM, D_NM, T_NM, S_NM)
    t50 = dpw50 / 1.73
    xp = np.linspace(-200.0, 200.0, n)
    erf_p = recording.perpendicular_pulse_erf(xp, dpw50)
    gauss_p = recording.perpendicular_pulse_gauss(xp, dpw50)
    ax2.plot(xp, erf_p, color="#9467bd", lw=1.8, label="未微分 erf（式 5-8）")
    ax2.plot(xp, gauss_p, color="#ff7f0e", lw=1.8, ls="--", label="微分 Gaussian（式 5-8）")
    ax2.axhline(0.0, color="k", lw=0.5)
    ax2.set_xlabel("沿道位置 x / nm")
    ax2.set_ylabel("归一化读出电压")
    ax2.set_title("(b) 垂直：erf 与微分 Gaussian 对照", fontsize=9)
    ax2.legend(fontsize=7, loc="upper left")
    ax2.grid(alpha=0.3)
    ax2.text(
        5, -0.85,
        rf"$d\mathrm{{PW}}_{{50}}={dpw50:.1f}$ nm" "\n" rf"$T_{{50}}={t50:.1f}$ nm" "\n"
        r"$d\mathrm{PW}_{50}\approx1.73\,T_{50}$",
        fontsize=7, va="center",
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#9467bd", alpha=0.9),
    )
    ax2.set_ylim(-1.1, 1.1)

    # CSV：曲线 + 拟合参数
    rows = []
    for xi, ve, vl, vg, vv, er, ga in zip(
        x[:: max(1, n // 240)], exact[:: max(1, n // 240)], recording.lorentz_pulse(x, pw_fit)[:: max(1, n // 240)],
        recording.gauss_pulse(x, pw_fit)[:: max(1, n // 240)], voigt[:: max(1, n // 240)],
        np.interp(x[:: max(1, n // 240)], xp, erf_p), np.interp(x[:: max(1, n // 240)], xp, gauss_p),
    ):
        rows.append([float(xi), float(ve), float(vl), float(vg), float(vv), float(er), float(ga),
                     ETA_BOOK, pw_fit, rms])
    return plotting.save_figure(fig, out_path), rows, dict(dpw50=dpw50, t50=t50, pw_fit=pw_fit, rms=rms, eta_free=eta_free)


def main(argv: list[str] | None = None) -> Path:
    args = build_parser().parse_args(argv)
    plotting.apply_style()
    config.rng(args.seed)  # 本图无随机量

    outdir, primary = _resolve_outdir(args.out, "fig05-04-reciprocity.png")
    config.ensure_dir(outdir)

    f4 = draw_reciprocity(outdir / "fig05-04-reciprocity.png", quick=args.quick)
    f5, rows, meta = draw_pulse_shapes(outdir / "fig05-05-pulse-shape.png", quick=args.quick)

    csv_path = io.write_csv(
        args.csv,
        ["x_nm", "v_exact", "v_lorentz", "v_gauss", "v_voigt", "v_perp_erf", "v_perp_gauss",
         "eta", "pw50_fit_nm", "fit_rms"],
        rows,
    )

    rel = io.repo_relative
    io.record_figure(
        "fig:5-4",
        chapter=5,
        section="5.3.1",
        title="互易原理读出几何与 Φ(k) 势函数链",
        script="code/experiments/ch05_pulse_shape.py",
        command=f"python code/experiments/ch05_pulse_shape.py --out {rel(outdir)}",
        output=f4,
        source="原创重绘（据编码书 Ch2 §2.3 互易原理与式 2.22–2.27）",
        license="CC BY 4.0（原创）",
    )
    io.record_figure(
        "fig:5-5",
        chapter=5,
        section="5.3.2",
        title="纵向精确积分 vs Lorentz/Gauss/Voigt（η=0.43）与垂直 erf/Gaussian 对照",
        script="code/experiments/ch05_pulse_shape.py",
        command=f"python code/experiments/ch05_pulse_shape.py --out {rel(outdir)}",
        output=f5,
        source="原创计算（式 5-7；重绘编码书 Ch2 图2.5 与式 2.30/2.36）",
        license="CC BY 4.0（原创）",
    )
    print(f"figure: {f4}")
    print(f"figure: {f5}")
    print(f"csv:    {csv_path}")
    print(f"Voigt:  eta={ETA_BOOK} pw50={meta['pw_fit']:.2f} nm rms={meta['rms']*100:.2f}% (free eta={meta['eta_free']:.3f})")
    print(f"Perp:   dPW50={meta['dpw50']:.1f} nm T50={meta['t50']:.1f} nm")
    return f5


if __name__ == "__main__":
    main()
