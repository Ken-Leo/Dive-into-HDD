"""例 5-1：纵向/垂直记录写场几何、Karlqvist 写场与翻转参数 a。

对应第 5 章 5.2 节，生成图 5-1（写场几何示意）、图 5-2（Karlqvist 等值线与
道内场梯度）、图 5-3（磁滞回线族与 a 随 H0/Hc、Mr·t、⟨D⟩ 的变化）。

参数取正文表 5-2 / 例 5-1：gW=0.2 μm、H0=2.5Hc、γ=15 nm、a=5–25 nm、
⟨D⟩=8–12 nm；Hc=2500 Oe、Mr=400 G、S*=0.8、t=10 nm。

用法::

    python code/experiments/ch05_write_field.py --out figures/ch05
    python code/experiments/ch05_write_field.py --out figures/ch05 --quick   # 冒烟测试

脚本固定随机种子（本图无随机量，仅为接口一致），输出 CSV 并登记 manifest。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hddbook import config, io, plotting, recording  # noqa: E402

# ---- 例 5-1 默认参数（正文表 5-2，CGS 高斯制）----
GW_NM = 200.0          # 写头深间隙 gW = 0.2 μm
HC_OE = 2500.0         # 矫顽力 Hc
MR_G = 400.0           # 剩磁 Mr（G = emu/cm³）
T_NM = 10.0            # 膜厚 t
GAMMA_NM = 15.0        # 净磁间距 γ = d + t/2
S_STAR = 0.8           # 回线方形度 S*
GRAIN_NM = 10.0        # 平均晶粒尺寸 ⟨D⟩
H0_OVER_HC = 2.5       # 深间隙场与矫顽力比


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default=str(config.FIG_DIR / "ch05"), help="图件输出目录（也接受单个 .png 路径）")
    p.add_argument("--csv", default=str(config.REPO_ROOT / "code" / "results" / "ch05_write_field.csv"))
    p.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    p.add_argument("--quick", action="store_true", help="降低采样点，供 pytest 冒烟测试")
    return p


def _resolve_outdir(out: str, primary_name: str) -> tuple[Path, Path]:
    """把 --out 解析为 (输出目录, 主图路径)；兼容目录与单个 .png 两种写法。"""
    p = Path(out)
    if p.suffix.lower() == ".png":
        return p.parent, p
    return p, p / primary_name


def _draw_triad(ax, ox: float, oy: float, scale: float) -> None:
    """画沿道 x、垂直 y、跨道 z 的三轴坐标系（z 以圆点表示指向纸外）。"""
    arrow = dict(arrowstyle="-|>", lw=1.2, color="k", shrinkA=0, shrinkB=0)
    ax.annotate("", xy=(ox + scale, oy), xytext=(ox, oy), arrowprops=arrow)
    ax.annotate("", xy=(ox, oy + scale), xytext=(ox, oy), arrowprops=arrow)
    ax.text(ox + scale + 4, oy - 2, "x", fontsize=8, va="center")
    ax.text(ox - 10, oy + scale + 4, "y", fontsize=8)
    ax.plot([ox], [oy], marker="o", ms=6, mfc="white", mec="k", mew=1.0, zorder=6)
    ax.plot([ox], [oy], marker=".", ms=2.5, color="k", zorder=7)
    ax.text(ox + 6, oy - 14, "z（指向纸外）", fontsize=7)


def _double_arrow(ax, p0, p1, text, offset=(0, 0), fontsize=8) -> None:
    """画带标注的双向尺寸箭头。"""
    ax.annotate(
        "",
        xy=p1,
        xytext=p0,
        arrowprops=dict(arrowstyle="<|-|>", lw=0.9, color="#333333", shrinkA=0, shrinkB=0),
    )
    ax.text(
        (p0[0] + p1[0]) / 2 + offset[0],
        (p0[1] + p1[1]) / 2 + offset[1],
        text,
        fontsize=fontsize,
        ha="center",
        va="center",
        bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85),
    )


def draw_write_geometry(out_path: Path) -> Path:
    """图 5-1：纵向/垂直记录写场、翻转锯齿壁与坐标系（d、t、s、SUL）。"""
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle

    fig, (ax_l, ax_p) = plt.subplots(1, 2, figsize=(7.6, 3.8))
    for ax in (ax_l, ax_p):
        ax.set_aspect("auto")   # 示意图纵向适当放大，便于标注
        ax.axis("off")

    # ---------------- (a) 纵向记录 ----------------
    ax_l.set_xlim(-330, 330)
    ax_l.set_ylim(-95, 190)
    ax_l.set_title("(a) 纵向记录：面内写场与锯齿形翻转壁", fontsize=9)

    # 衬底 + 介质膜（厚度 t）
    ax_l.add_patch(Rectangle((-240, -30), 480, 30, fc="#cfcfcf", ec="k", lw=0.8))
    ax_l.add_patch(Rectangle((-240, 0), 480, 40, fc="#e8d9b8", ec="k", lw=0.9))
    ax_l.text(-235, -16, "衬底", fontsize=8, va="center")
    ax_l.text(-235, 34, r"介质膜（纵向，$M_r$）", fontsize=7.5, va="center")

    # 磁头：左右极靴，中间 gW 间隙；ABS 在 y=70
    for x0 in (-130, 25):
        ax_l.add_patch(Rectangle((x0, 70), 105, 45, fc="#9fb3c8", ec="k", lw=0.9))
    ax_l.text(-78, 92, "写极靴", fontsize=8, ha="center", va="center")
    ax_l.plot([-240, 240], [70, 70], "k--", lw=0.8)
    ax_l.text(-328, 73, "ABS（气浮面）", fontsize=7, va="bottom")

    # 间隙、间距、膜厚标注
    _double_arrow(ax_l, (-25, 122), (25, 122), "gW = 0.2 μm", offset=(0, 7))
    _double_arrow(ax_l, (-218, 40), (-218, 70), "d", offset=(-13, 0))
    _double_arrow(ax_l, (255, 0), (255, 40), "t", offset=(13, 0))

    # 锯齿形翻转壁（沿 y 方向来回摆动）
    zig = [(6.0 * (1 if j % 2 else -1), 40.0 * j / 10.0) for j in range(11)] + [(0.0, 40.0)]
    ax_l.add_patch(Polygon(zig, closed=False, fill=False, ec="#b2182b", lw=2.4, zorder=5))
    ax_l.text(12, 34, "锯齿形翻转壁", fontsize=6.8, color="#b2182b", va="center")

    # 面内磁化箭头：左侧 -x，右侧 +x
    for xs in (-205, -165, -125, -85, -50):
        ax_l.annotate("", xy=(xs - 22, 18), xytext=(xs, 18), arrowprops=dict(arrowstyle="-|>", lw=1.3, color="#1f4e79"))
    for xs in (50, 85, 125, 165, 205):
        ax_l.annotate("", xy=(xs + 22, 18), xytext=(xs, 18), arrowprops=dict(arrowstyle="-|>", lw=1.3, color="#1f4e79"))

    # 写场流线：从间隙边缘向介质内弯曲
    for start, end, rad in (
        ((-25, 70), (-95, 12), 0.32),
        ((25, 70), (95, 12), -0.32),
        ((-25, 70), (-150, 34), 0.18),
        ((25, 70), (150, 34), -0.18),
    ):
        ax_l.add_patch(
            FancyArrowPatch(start, end, connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>",
                            mutation_scale=9, lw=1.1, color="#d95f02")
        )
    ax_l.text(-150, 62, r"$H_a$（写场）", fontsize=8, color="#d95f02",
              bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))
    ax_l.annotate("", xy=(0, 44), xytext=(0, 68),
                  arrowprops=dict(arrowstyle="-|>", lw=1.0, color="#d95f02", ls="--"))
    ax_l.text(4, 56, r"$H_0>2H_c$", fontsize=7, color="#d95f02", va="center")

    # 翻转中心 x0
    ax_l.plot([0], [-10], marker="v", ms=5, color="#b2182b")
    ax_l.plot([0, 0], [-12, -40], ls=":", lw=0.8, color="#b2182b")
    ax_l.text(0, -48, r"$x_0$（翻转中心）", fontsize=7, ha="center", color="#b2182b")
    _draw_triad(ax_l, -318, 128, 26)

    # ---------------- (b) 垂直记录 ----------------
    ax_p.set_xlim(-330, 330)
    ax_p.set_ylim(-110, 200)
    ax_p.set_title("(b) 垂直记录：单极头 + SUL 与垂直磁化", fontsize=9)

    # SUL（软磁底层）位于介质下方；坐标系零点取 SUL 顶面
    ax_p.add_patch(Rectangle((-240, -35), 480, 35, fc="#8fa3b8", ec="k", lw=0.9))
    ax_p.add_patch(Rectangle((-240, 0), 480, 40, fc="#e8d9b8", ec="k", lw=0.9))
    ax_p.text(-140, -18, "SUL（软磁底层）", fontsize=8, va="center", color="white")
    ax_p.text(95, 52, "垂直介质", fontsize=7.5, va="center")

    # 单极主极 + 拖尾屏蔽
    ax_p.add_patch(Rectangle((-40, 90), 60, 50, fc="#9fb3c8", ec="k", lw=0.9))
    ax_p.add_patch(Rectangle((55, 90), 65, 50, fc="#9fb3c8", ec="k", lw=0.9))
    ax_p.text(-10, 115, "主极", fontsize=7.5, ha="center", va="center")
    ax_p.text(87, 115, "拖尾屏蔽", fontsize=7, ha="center", va="center")
    ax_p.plot([-240, 240], [90, 90], "k--", lw=0.8)
    ax_p.text(-328, 93, "ABS", fontsize=7, va="bottom")

    _double_arrow(ax_p, (165, 40), (165, 90), "d", offset=(15, 0))
    _double_arrow(ax_p, (258, 0), (258, 40), "t", offset=(14, 0))
    _double_arrow(ax_p, (-258, -35), (-258, 0), "s", offset=(-14, 0))
    _double_arrow(ax_p, (20, 152), (55, 152), "gW", offset=(0, 8))

    # 垂直磁化：左半向上、右半向下
    for xs in (-205, -165, -125, -85, -45):
        ax_p.annotate("", xy=(xs, 35), xytext=(xs, 4), arrowprops=dict(arrowstyle="-|>", lw=1.4, color="#1f4e79"))
    for xs in (45, 85, 125, 165, 205):
        ax_p.annotate("", xy=(xs, 4), xytext=(xs, 35), arrowprops=dict(arrowstyle="-|>", lw=1.4, color="#1f4e79"))
    ax_p.text(-205, 43, r"$+M_r$", fontsize=8, color="#1f4e79")
    ax_p.text(255, 46, r"$-M_r$", fontsize=8, color="#1f4e79")

    # 垂直翻转壁
    ax_p.plot([0, 0], [0, 40], color="#b2182b", lw=2.4, zorder=5)
    for j in range(1, 6):
        ax_p.plot([-3.5, 3.5], [7.0 * j, 7.0 * j], color="#b2182b", lw=0.8, alpha=0.55)
    ax_p.text(10, 45, "垂直翻转壁", fontsize=6.8, color="#b2182b", va="center")

    # 写场：主极 → 介质 → SUL → 屏蔽 的回路
    for xs, rad in ((-25, 0.22), (0, 0.0), (18, -0.22)):
        ax_p.add_patch(
            FancyArrowPatch((xs, 90), (xs * 0.7, 8), connectionstyle=f"arc3,rad={rad}",
                            arrowstyle="-|>", mutation_scale=9, lw=1.2, color="#d95f02")
        )
    ax_p.add_patch(
        FancyArrowPatch((30, 4), (78, 86), connectionstyle="arc3,rad=-0.22",
                        arrowstyle="-|>", mutation_scale=9, lw=1.2, color="#d95f02")
    )
    ax_p.text(-125, 66, r"$H_0$（垂直写场）", fontsize=8, color="#d95f02")
    _draw_triad(ax_p, -318, 140, 26)

    fig.subplots_adjust(wspace=0.06)
    out = plotting.save_figure(fig, out_path)
    return out


def draw_karlqvist(out_path: Path, *, quick: bool = False) -> Path:
    """图 5-2：Karlqvist 写场等值线与道内场梯度（gW=0.2 μm，H0/Hc 扫描）。"""
    import matplotlib.pyplot as plt

    n = 90 if quick else 240
    x = np.linspace(-320.0, 320.0, n)
    y = np.linspace(6.0, 260.0, n)
    xx, yy = np.meshgrid(x, y)
    hx, hy = recording.karlqvist_field(xx, yy, GW_NM, H0_OVER_HC * HC_OE)
    ratio = hx / HC_OE

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.2), constrained_layout=True)
    levels = np.array([0.2, 0.5, 0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.3])
    cf = ax1.contourf(xx, yy, ratio, levels=levels, cmap="viridis", extend="max")
    ax1.contour(xx, yy, ratio, levels=[1.0], colors="#b2182b", linewidths=2.0)
    cb = fig.colorbar(cf, ax=ax1, fraction=0.046, pad=0.03)
    cb.ax.set_title(r"$H_x/H_c$", fontsize=8, pad=4)
    x0 = recording.transition_position(H0_OVER_HC, GW_NM, GAMMA_NM)
    ax1.axhline(GAMMA_NM, color="w", ls="--", lw=1.0)
    ax1.text(-312, GAMMA_NM + 12, r"$\gamma=d+t/2$", color="k", fontsize=7.5,
             bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.85))
    ax1.plot([x0], [GAMMA_NM], marker="o", ms=6, mfc="white", mec="#b2182b", mew=1.5, zorder=6)
    ax1.annotate(r"$x_0$", xy=(x0, GAMMA_NM), xytext=(x0 + 55, GAMMA_NM + 55),
                 color="w", fontsize=8, arrowprops=dict(arrowstyle="-|>", color="w", lw=0.9))
    # Hx=Hc 等值线顶部位置（轴上 x=0 处 Hx=Hc 的最高 y）
    ax1.annotate(r"$H_x=H_c$", xy=(0.0, 137.6), xytext=(60, 175),
                 color="#ffd9d9", fontsize=8,
                 arrowprops=dict(arrowstyle="-|>", color="#ffd9d9", lw=0.9))
    ax1.set_xlabel("沿道位置 x / nm")
    ax1.set_ylabel("离 ABS 距离 y / nm")
    ax1.set_title(r"(a) $H_x$ 等值线（$H_0=2.5H_c$，$g_W=200$ nm）", fontsize=9)
    ax1.grid(alpha=0.2)

    # 道内场梯度：在介质中心面 y=γ 处对 x 求导
    n2 = 2000 if quick else 6000
    xg = np.linspace(-260.0, 260.0, n2)
    dx = xg[1] - xg[0]
    ratios = (1.5, 2.0, 2.5, 3.0, 4.0)
    colors = plt.cm.plasma(np.linspace(0.05, 0.85, len(ratios)))
    for r, col in zip(ratios, colors):
        hx_line, _ = recording.karlqvist_field(xg, GAMMA_NM, GW_NM, r * HC_OE)
        grad = -np.gradient(hx_line, dx) / HC_OE  # 归一化到 Hc/nm
        ax2.plot(xg, grad, color=col, label=rf"$H_0/H_c={r:.1f}$")
        xi = recording.transition_position(r, GW_NM, GAMMA_NM)
        if np.isfinite(xi):
            gi = np.interp(xi, xg, grad)
            ax2.plot([xi], [gi], "o", color=col, ms=4)
    ax2.axvline(0.0, color="k", lw=0.6, ls=":")
    ax2.set_ylim(-0.095, 0.09)
    ax2.set_xlabel("沿道位置 x / nm")
    ax2.set_ylabel(r"道内场梯度 $|dH_x/dx|/H_c$ / nm$^{-1}$")
    ax2.set_title("(b) 道内场梯度（y=γ 处，圆点为 x0）", fontsize=9)
    ax2.legend(fontsize=6.5, ncol=2, loc="lower right")
    ax2.grid(alpha=0.3)

    return plotting.save_figure(fig, out_path)


def draw_hysteresis_and_a(out_path: Path, *, quick: bool = False) -> Path:
    """图 5-3：磁滞回线族与 a 随 H0/Hc、Mr·t、⟨D⟩ 的变化。"""
    import matplotlib.pyplot as plt

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(7.6, 3.0), constrained_layout=True)

    # (a) 回线族：S* 与 Mr/Ms 由式 5-2 保持一致
    h = np.linspace(-3.0 * HC_OE, 3.0 * HC_OE, 400 if quick else 1600)
    for s_star, col in zip((0.6, 0.75, 0.9), ("#1b9e77", "#d95f02", "#7570b3")):
        up, down = recording.hysteresis_loop(h, HC_OE, s_star)
        mr = recording.remanence_ratio(s_star)
        ax1.plot(h / HC_OE, up, color=col, lw=1.2, label=rf"$S^*={s_star:.2f}$, $M_r/M_s={mr:.2f}$")
        ax1.plot(h / HC_OE, down, color=col, lw=1.2, ls="--")
        # 标注 H=0 处的剩磁（±Mr/Ms）与 M=0 处的矫顽场（±Hc）
        ax1.plot([0.0, 0.0], [mr, -mr], "o", color=col, ms=3.2, zorder=5)
    ax1.axhline(0, color="k", lw=0.5)
    ax1.axvline(0, color="k", lw=0.5)
    ax1.set_xlim(-2.2, 2.2)
    ax1.set_ylim(-1.05, 1.05)
    ax1.set_xlabel(r"归一化外场 $H/H_c$")
    ax1.set_ylabel(r"归一化磁化 $M/M_s$")
    ax1.set_title("(a) 磁滞回线族（实线上升/虚线下降）", fontsize=9)
    ax1.legend(fontsize=6, loc="upper left")
    ax1.grid(alpha=0.3)

    # (b) a 随 H0/Hc 与 Mr·t 变化（Williams-Comstock + 颗粒修正）
    r_grid = np.linspace(1.25, 4.0, 120 if quick else 300)
    for mr_t, col in zip((2000.0, 4000.0, 8000.0), ("#1b9e77", "#d95f02", "#7570b3")):
        a_vals = []
        for r in r_grid:
            awc = recording.williams_comstock_a(r, HC_OE, mr_t, GAMMA_NM, S_STAR, GW_NM)
            a_vals.append(recording.grain_limited_a(awc, GRAIN_NM))
        ax2.plot(r_grid, a_vals, color=col, label=rf"$M_r t={mr_t/1000:.0f}\times10^3$ G·nm")
    awc_ref = [
        recording.williams_comstock_a(r, HC_OE, 4000.0, GAMMA_NM, S_STAR, GW_NM) for r in r_grid
    ]
    ax2.plot(r_grid, awc_ref, "k--", lw=0.9, label=r"$a_{WC}$（未加颗粒修正）")
    ax2.axhline(GRAIN_NM / np.pi, color="#b2182b", ls=":", lw=1.0, label=r"$\langle D\rangle/\pi$ 下限")
    ax2.axvline(H0_OVER_HC, color="gray", lw=0.8, ls=":")
    ax2.set_xlabel(r"深间隙场比 $H_0/H_c$")
    ax2.set_ylabel("翻转参数 a / nm")
    ax2.set_title(r"(b) a 随 $H_0/H_c$、$M_r t$ 的变化", fontsize=9)
    ax2.legend(fontsize=6, loc="upper right")
    ax2.grid(alpha=0.3)

    # (c) a 随 ⟨D⟩ 变化，显示颗粒下限
    d_grid = np.linspace(4.0, 30.0, 120 if quick else 300)
    for r, col in zip((2.0, 2.5, 4.0), ("#d95f02", "#7570b3", "#1b9e77")):
        a_vals = []
        for dg in d_grid:
            awc = recording.williams_comstock_a(r, HC_OE, 4000.0, GAMMA_NM, S_STAR, GW_NM)
            a_vals.append(recording.grain_limited_a(awc, dg))
        ax3.plot(d_grid, a_vals, color=col, label=rf"$H_0/H_c={r:.1f}$")
    ax3.plot(d_grid, d_grid / np.pi, "k:", lw=1.0, label=r"$\langle D\rangle/\pi$")
    ax3.set_xlabel(r"平均晶粒尺寸 $\langle D\rangle$ / nm")
    ax3.set_ylabel("翻转参数 a / nm")
    ax3.set_title(r"(c) a 随 $\langle D\rangle$ 的变化（颗粒下限）", fontsize=9)
    ax3.legend(fontsize=6, loc="upper left")
    ax3.grid(alpha=0.3)

    return plotting.save_figure(fig, out_path)


def main(argv: list[str] | None = None) -> Path:
    args = build_parser().parse_args(argv)
    plotting.apply_style()
    config.rng(args.seed)  # 本图无随机量，保持脚本接口一致

    outdir, primary = _resolve_outdir(args.out, "fig05-01-write-geometry.png")
    config.ensure_dir(outdir)

    f1 = draw_write_geometry(primary)
    f2 = draw_karlqvist(outdir / "fig05-02-karlqvist-field.png", quick=args.quick)
    f3 = draw_hysteresis_and_a(outdir / "fig05-03-hysteresis-a.png", quick=args.quick)

    # CSV：H0/Hc × Mr·t 的 x0、梯度、Q、a_WC、a 数据表
    rows: list[list[float]] = []
    for mr_t in (2000.0, 4000.0, 8000.0):
        for r in np.round(np.linspace(1.3, 4.0, 28), 2):
            x0, grad, q = recording.head_field_gradient(r, GW_NM, HC_OE, GAMMA_NM)
            awc = recording.williams_comstock_a(r, HC_OE, mr_t, GAMMA_NM, S_STAR, GW_NM)
            a = recording.grain_limited_a(awc, GRAIN_NM)
            rows.append([float(r), mr_t, GRAIN_NM, x0, grad, q, awc, a])
    csv_path = io.write_csv(
        args.csv,
        ["h0_over_hc", "mr_t_g_nm", "grain_nm", "x0_nm", "dHa_dx_oe_per_nm", "Q", "a_wc_nm", "a_nm"],
        rows,
    )

    rel = io.repo_relative
    io.record_figure(
        "fig:5-1",
        chapter=5,
        section="5.2.1",
        title="纵向/垂直记录写场几何、锯齿形翻转壁与坐标系（d、t、s、SUL）",
        script="code/experiments/ch05_write_field.py",
        command=f"python code/experiments/ch05_write_field.py --out {rel(outdir)}",
        output=f1,
        source="原创重绘（据编码书 Ch2 图2.2/2.3 的几何关系；式 5-1/5-5）",
        license="CC BY 4.0（原创）",
    )
    io.record_figure(
        "fig:5-2",
        chapter=5,
        section="5.2.1",
        title="Karlqvist 写场等值线与道内场梯度（gW=0.2 μm，H0/Hc 扫描）",
        script="code/experiments/ch05_write_field.py",
        command=f"python code/experiments/ch05_write_field.py --out {rel(outdir)}",
        output=f2,
        source="原创计算（式 5-1/5-5；Karlqvist 1954）",
        license="CC BY 4.0（原创）",
    )
    io.record_figure(
        "fig:5-3",
        chapter=5,
        section="5.2.2",
        title="磁滞回线族与翻转参数 a 随 H0/Hc、Mr·t、⟨D⟩ 的变化",
        script="code/experiments/ch05_write_field.py",
        command=f"python code/experiments/ch05_write_field.py --out {rel(outdir)}",
        output=f3,
        source="原创计算（式 5-2/5-4；改编自编码书 Ch2 图2.4 与式 2.14/2.15）",
        license="CC BY 4.0（原创）",
    )
    print(f"figure: {f1}")
    print(f"figure: {f2}")
    print(f"figure: {f3}")
    print(f"csv:    {csv_path}")
    return f1


if __name__ == "__main__":
    main()
