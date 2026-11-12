"""例 5-3：方波 roll-off 曲线与 D50（纵向 1.46、垂直 1.02）。

对应第 5 章 5.3.3 节，生成图 5-6（roll-off 曲线与 D50 标注）。纵向曲线按源书
式 2.42/2.43 的谐波叠加计算（精确脉冲 / Lorentz / Gauss / Voigt η=0.43），
垂直曲线按式 2.45 的指数近似与微分 Gaussian 对照；D50 由数值 50% 交点给出，
并在图中标注教材值 1.46 / 1.02。

用法::

    python code/experiments/ch05_rolloff.py --out figures/ch05
    python code/experiments/ch05_rolloff.py --out figures/ch05 --quick
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hddbook import config, io, plotting, recording  # noqa: E402

# ---- 例 5-3 默认参数（nm；CGS 高斯制）----
G_NM = 50.0
DELTA_NM = 5.0
A_NM = 5.0
GAMMA_NM = 15.0
PW50_NM = 74.0     # 由式 5-7 精确脉冲数值积分得到的半峰宽
DPW50_NM = 58.6    # 垂直微分半峰宽（例 5-2 参数）
D50_BOOK_L = 1.46  # 教材纵向值（源书式 2.47）
D50_BOOK_P = 1.02  # 教材垂直值（源书式 2.46）


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default=str(config.FIG_DIR / "ch05"), help="图件输出目录（也接受单个 .png 路径）")
    p.add_argument("--csv", default=str(config.REPO_ROOT / "code" / "results" / "ch05_rolloff.csv"))
    p.add_argument("--seed", type=int, default=config.DEFAULT_SEED)
    p.add_argument("--quick", action="store_true", help="降低采样点，供 pytest 冒烟测试")
    return p


def _resolve_outdir(out: str, primary_name: str) -> tuple[Path, Path]:
    p = Path(out)
    if p.suffix.lower() == ".png":
        return p.parent, p
    return p, p / primary_name


def draw_rolloff(out_path: Path, *, quick: bool = False) -> Path:
    """图 5-6：roll-off 曲线与 D50 标注（纵向/垂直对比）。"""
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.6, 3.2), constrained_layout=True)

    n = 60 if quick else 180
    x = np.linspace(0.15, 2.5, n)   # 归一化密度 PW50/B 或 dPW50/B

    curves = {
        "精确积分": recording.rolloff_exact(
            x, pw50_nm=PW50_NM, g_nm=G_NM, delta_nm=DELTA_NM, a_nm=A_NM,
            gamma_nm=GAMMA_NM, nk=2000 if quick else 8000,
        ),
        "Lorentz": recording.rolloff_lorentz(x),
        "Gauss": recording.rolloff_gauss(x),
        r"Voigt $\eta=0.43$": recording.rolloff_voigt(x, 0.43),
    }
    styles = {"精确积分": ("-", 2.0), "Lorentz": ("--", 1.2), "Gauss": ("-.", 1.2), r"Voigt $\eta=0.43$": (":", 1.6)}
    colors = {"精确积分": "k", "Lorentz": "#1f77b4", "Gauss": "#2ca02c", r"Voigt $\eta=0.43$": "#d62728"}
    d50 = {}
    for name, y in curves.items():
        ls, lw = styles[name]
        ax1.plot(x, y, ls=ls, lw=lw, color=colors[name], label=name)
        d50[name] = recording.d50_from_curve(x, y)
    ax1.axhline(0.5, color="gray", lw=0.6, ls=":")
    ax1.axvline(D50_BOOK_L, color="#b2182b", lw=1.0, ls="--")
    ax1.text(D50_BOOK_L + 0.04, 0.92, rf"$D_{{50}}\mathrm{{PW}}_{{50}}=1.46$（教材）" "\n"
             rf"数值复现 {d50['精确积分']:.2f}", fontsize=7, color="#b2182b")
    ax1.set_xlim(0.15, 2.5)
    ax1.set_ylim(0.0, 1.02)
    ax1.set_xlabel(r"归一化线密度 $D\cdot\mathrm{PW}_{50}=1/B\cdot\mathrm{PW}_{50}$")
    ax1.set_ylabel(r"归一化峰值电压 $V_{\mathrm{peak}}(B)/V_{\mathrm{peak}}$")
    ax1.set_title("(a) 纵向记录 roll-off（谐波叠加，式 5-9）", fontsize=9)
    ax1.legend(fontsize=6.5, loc="lower left")
    ax1.grid(alpha=0.3)

    # 垂直：未微分脉冲（式 2.45）与微分 Gaussian 对照
    perp = recording.rolloff_perpendicular(x, approximate=True)
    diff = recording.rolloff_differentiated_gauss(x)
    d50_p = recording.d50_from_curve(x, perp)
    d50_d = recording.d50_from_curve(x, diff)
    ax2.plot(x, perp, "k-", lw=2.0, label="未微分 erf（式 5-9 近似）")
    ax2.plot(x, diff, "--", lw=1.4, color="#ff7f0e",
             label=rf"微分 Gaussian（$D_{{50}}d\mathrm{{PW}}_{{50}}\approx{d50_d:.2f}$）")
    ax2.axhline(0.5, color="gray", lw=0.6, ls=":")
    ax2.axvline(D50_BOOK_P, color="#b2182b", lw=1.0, ls="--")
    ax2.text(D50_BOOK_P + 0.04, 0.92, rf"$D_{{50}}d\mathrm{{PW}}_{{50}}=1.02$（教材）" "\n"
             rf"近似式复现 {d50_p:.2f}", fontsize=7, color="#b2182b")
    ax2.set_xlim(0.15, 2.5)
    ax2.set_ylim(0.0, 1.02)
    ax2.set_xlabel(r"归一化线密度 $D\cdot d\mathrm{PW}_{50}$")
    ax2.set_ylabel(r"归一化峰值电压 $V_{\mathrm{peak}}(B)/V_{\mathrm{peak}}$")
    ax2.set_title("(b) 垂直记录 roll-off 与微分脉冲对照", fontsize=9)
    ax2.legend(fontsize=6.5, loc="lower left")
    ax2.grid(alpha=0.3)

    d50["perp"] = d50_p
    d50["perp_diff"] = d50_d
    rows = []
    for xi, *vals in zip(x, curves["精确积分"], curves["Lorentz"], curves["Gauss"],
                         curves[r"Voigt $\eta=0.43$"], perp, diff):
        rows.append([float(xi), *[float(v) for v in vals],
                     D50_BOOK_L, d50["精确积分"], D50_BOOK_P, d50_p])
    return plotting.save_figure(fig, out_path), rows, d50


def main(argv: list[str] | None = None) -> Path:
    args = build_parser().parse_args(argv)
    plotting.apply_style()
    config.rng(args.seed)  # 本图无随机量

    outdir, primary = _resolve_outdir(args.out, "fig05-06-rolloff.png")
    config.ensure_dir(outdir)

    fig_path, rows, d50 = draw_rolloff(primary, quick=args.quick)
    csv_path = io.write_csv(
        args.csv,
        ["norm_density", "exact", "lorentz", "gauss", "voigt", "perp_undiff", "perp_diff",
         "d50_book_l", "d50_repro_l", "d50_book_p", "d50_repro_p"],
        rows,
    )

    rel = io.repo_relative
    io.record_figure(
        "fig:5-6",
        chapter=5,
        section="5.3.3",
        title="roll-off 曲线与 D50 标注（纵向 1.46、垂直 1.02）",
        script="code/experiments/ch05_rolloff.py",
        command=f"python code/experiments/ch05_rolloff.py --out {rel(outdir)}",
        output=fig_path,
        source="原创计算（式 5-9；重绘编码书 Ch2 图2.7 与式 2.43/2.45）",
        license="CC BY 4.0（原创）",
    )
    print(f"figure: {fig_path}")
    print(f"csv:    {csv_path}")
    print(f"D50:    LMR exact={d50['精确积分']:.3f} (book 1.46); perp approx={d50.get('perp', float('nan'))}")
    return fig_path


if __name__ == "__main__":
    main()
