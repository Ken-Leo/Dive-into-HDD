"""第 5 章记录物理模型（Karlqvist 写场、翻转参数、互易读出、介质噪声）。

本模块把第 5 章正文公式 5-1～5-12（对应编码书 Ch2 式 2.1、2.9、2.10、2.14、
2.15、2.26、2.27、2.36、2.39、2.43、2.45、2.57、2.60、2.62）实现为可直接
复现的函数。长度单位统一用 nm，场单位用 Oe（CGS 高斯制，与源书一致；
1 Oe = 79.577 A/m，正文另附 SI 换算表）。

约定：
- ``x`` 沿道方向、``y`` 垂直离开介质表面、``z`` 跨道方向；
- ``gamma = d + t/2`` 为纵向记录净磁间距（磁头-介质间距 + 膜厚一半）；
- 纵向/垂直的 ``Mr`` 均以 G（emu/cm³）给出，``Mr*t`` 单位为 G·nm。

所有函数只做数值计算，不做绘图；绘图由 ``code/experiments/ch05_*.py`` 完成。
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import simpson

#: Williams-Comstock 退磁梯度形状因子（tanh 翻转形状，源书式 2.13）
I_WC = 0.691

#: 颗粒修正系数（源书式 2.15）
GRAIN_COEFF = 0.35


def karlqvist_field(x_nm, y_nm, gw_nm: float, h0_oe: float):
    """纵向无限道宽 Karlqvist 磁头场（式 5-1 / 源书式 2.1）。

    参数
    ----
    x_nm, y_nm : 场点坐标（nm），y 为离开 ABS 的垂直距离，必须 > 0；
    gw_nm      : 深间隙宽度 gW（nm）；
    h0_oe      : 深间隙场 H0（Oe）。

    返回 ``(Hx, Hy)``，单位 Oe。``y=0`` 处用 1e-6 nm 防止除零。
    """
    x = np.asarray(x_nm, dtype=float)
    y = np.maximum(np.asarray(y_nm, dtype=float), 1e-6)
    hx = h0_oe / np.pi * (
        np.arctan((gw_nm / 2.0 + x) / y) + np.arctan((gw_nm / 2.0 - x) / y)
    )
    hy = -h0_oe / (2.0 * np.pi) * np.log(
        ((x + gw_nm / 2.0) ** 2 + y**2) / ((x - gw_nm / 2.0) ** 2 + y**2)
    )
    return hx, hy


def transition_position(h0_over_hc: float, gw_nm: float, gamma_nm: float) -> float:
    """纵向翻转中心 x0（式 5-5 / 源书式 2.9），返回 nm。

    分两支：H0 > 2Hc 用正切分支，H0 <= 2Hc 用 y 分支。若判别式为负说明
    场峰不足以越过 Hc，返回 nan。
    """
    r = float(h0_over_hc)
    if r <= 1.0:
        return float("nan")
    if r > 2.0:
        disc = 1.0 - (2.0 * gamma_nm / gw_nm) ** 2 + 4.0 * gamma_nm / (
            gw_nm * np.tan(np.pi / r)
        )
    else:
        tan_arg = np.tan(np.pi * (1.0 - 1.0 / r))
        if abs(tan_arg) < 1e-12:
            return float("nan")
        disc = 1.0 - (2.0 * gamma_nm / gw_nm) ** 2 - 4.0 * gamma_nm / (gw_nm * tan_arg)
    if disc < 0.0:
        return float("nan")
    return float(gw_nm / 2.0 * np.sqrt(disc))


def head_field_gradient(h0_over_hc: float, gw_nm: float, hc_oe: float, gamma_nm: float):
    """翻转中心处写场梯度 dHa/dx 与归一化梯度 Q（式 5-5 / 源书式 2.10）。

    返回 ``(x0_nm, dHa_dx_oe_per_nm, Q)``。``dHa/dx = -Q*Hc/gamma``。
    """
    r = float(h0_over_hc)
    x0 = transition_position(r, gw_nm, gamma_nm)
    if not np.isfinite(x0):
        return x0, float("nan"), float("nan")
    q = 2.0 * x0 * r / (np.pi * gw_nm) * np.sin(np.pi / r) ** 2
    return x0, -q * hc_oe / gamma_nm, q


def williams_comstock_a(
    h0_over_hc: float,
    hc_oe: float,
    mr_t_g_nm: float,
    gamma_nm: float,
    s_star: float,
    gw_nm: float,
) -> float:
    """Williams-Comstock 翻转参数 a_WC（式 5-4 / 源书式 2.14），返回 nm。

    ``mr_t_g_nm = Mr[G] * t[nm]``。梯度不足（Q 很小）时 a_WC 迅速增大。
    """
    x0, _, q = head_field_gradient(h0_over_hc, gw_nm, hc_oe, gamma_nm)
    if not np.isfinite(q) or q <= 0.0:
        return float("nan")
    lead = (1.0 - s_star) * gamma_nm / (np.pi * q)
    disc = lead**2 + 4.0 * mr_t_g_nm * gamma_nm * I_WC / (q * hc_oe)
    return float(lead + np.sqrt(max(disc, 0.0)))


def grain_limited_a(a_wc_nm: float, grain_nm: float) -> float:
    """颗粒修正后的翻转参数 a（式 5-4 / 源书式 2.15），返回 nm。

    a = sqrt((<D>/pi)^2 + 0.35 a_WC^2)，颗粒下限为 <D>/pi。
    """
    if not np.isfinite(a_wc_nm):
        return float("nan")
    return float(np.sqrt((grain_nm / np.pi) ** 2 + GRAIN_COEFF * a_wc_nm**2))


def squareness_to_u(s_star: float) -> float:
    """由回线方形度 S* 反解 arctan 回线模型的归一化矫顽斜率 u = Hc/Hs。

    由式 5-2（源书式 2.4）dM/dH|Hc = Mr/[Hc(1-S*)] 与 arctan 模型
    M/Ms = (2/pi)atan((H+Hc)/Hs) 联立可得 S* = 1 - atan(u)/u，本函数用二分法
    反解 u。
    """
    target = 1.0 - float(s_star)
    if target <= 0.0:
        return float("inf")
    lo, hi = 1e-6, 1e4
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if np.arctan(mid) / mid > target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def hysteresis_loop(h_oe, hc_oe: float, s_star: float):
    """arctan 磁滞回线族（式 5-2 自洽模型）。

    返回 ``(M_over_Ms_up, M_over_Ms_down)``：上升支在 H=-Hc 过零、
    H=0 处等于 Mr/Ms；下降支在 H=+Hc 过零。方形度 S* 与 Mr/Ms 由
    ``squareness_to_u`` 保持式 5-2 的一致性。
    """
    h = np.asarray(h_oe, dtype=float)
    u = squareness_to_u(s_star)
    hs = hc_oe / u if np.isfinite(u) else 0.0
    if hs <= 0.0:
        up = np.sign(h + hc_oe)
        down = np.sign(h - hc_oe)
        return up, down
    up = (2.0 / np.pi) * np.arctan((h + hc_oe) / hs)
    down = (2.0 / np.pi) * np.arctan((h - hc_oe) / hs)
    return up, down


def remanence_ratio(s_star: float) -> float:
    """由 S* 给出的 Mr/Ms（arctan 模型：Mr/Ms=(2/pi)atan(u)）。"""
    u = squareness_to_u(s_star)
    if not np.isfinite(u):
        return 1.0
    return float((2.0 / np.pi) * np.arctan(u))


def replay_envelope(k_nm_inv, *, g_nm=50.0, delta_nm=5.0, a_nm=5.0, gamma_nm=15.0):
    """纵向孤立翻转读出脉冲的傅里叶包络（式 5-7 / 源书式 2.27 被积函数）。

    ``k`` 为空间频率（1/nm）。返回未归一化的 V_sp(k) 包络，供精确积分、
    roll-off 叠加与噪声谱使用。k=0 附近取极限值 1。
    """
    k = np.atleast_1d(np.asarray(k_nm_inv, dtype=float))
    k = np.maximum(k, 1e-9)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        y = np.pi**2 * k * a_nm / 4.0
        f1 = np.where(y < 700.0, y / np.sinh(np.minimum(y, 700.0)), 0.0)
        s1 = np.sin(k * g_nm / 2.0) / (k * g_nm / 2.0)
        s2 = np.sin(k * (g_nm + delta_nm) / 2.0) / (k * (g_nm + delta_nm) / 2.0)
        env = np.exp(-k * gamma_nm) * f1 * s1 * s2
    env = np.nan_to_num(env, nan=1.0, posinf=0.0, neginf=0.0)
    return env


def exact_replay_pulse(
    x_nm,
    *,
    g_nm=50.0,
    delta_nm=5.0,
    a_nm=5.0,
    gamma_nm=15.0,
    nk: int = 20000,
    kmax_nm_inv: float = 8.0,
    chunk: int = 200,
):
    """纵向孤立翻转读出脉冲的精确数值积分（式 5-7 / 源书式 2.27）。

    对 e^{-k gamma} (pi^2 k a/4)/sinh(pi^2 k a/4) sinc(kg/2) sinc(k(g+delta)/2)
    cos(kx) 做 0..kmax 的 Simpson 积分；返回值按峰值归一化为 1。
    """
    x = np.atleast_1d(np.asarray(x_nm, dtype=float))
    k = np.linspace(1e-6, kmax_nm_inv, nk)
    env = replay_envelope(k, g_nm=g_nm, delta_nm=delta_nm, a_nm=a_nm, gamma_nm=gamma_nm)
    out = np.empty_like(x)
    for i in range(0, x.size, chunk):
        block = x[i : i + chunk]
        vals = np.cos(np.outer(block, k)) * env[None, :]
        out[i : i + chunk] = simpson(vals, x=k, axis=1) / np.pi
    peak = np.max(np.abs(out))
    if peak > 0:
        out = out / peak
    return out


def voigt_pulse(x_nm, pw50_nm: float, eta: float):
    """纵向 Voigt 拟合族（式 5-7 / 源书式 2.39）：eta*Lorentz+(1-eta)*Gauss。"""
    x = np.asarray(x_nm, dtype=float)
    beta = pw50_nm / (2.0 * np.sqrt(np.log(2.0)))
    lorentz = 1.0 / (1.0 + (2.0 * x / pw50_nm) ** 2)
    gauss = np.exp(-((x / beta) ** 2))
    return eta * lorentz + (1.0 - eta) * gauss


def lorentz_pulse(x_nm, pw50_nm: float):
    """纵向 Lorentz 脉冲（源书式 2.37）。"""
    x = np.asarray(x_nm, dtype=float)
    return 1.0 / (1.0 + (2.0 * x / pw50_nm) ** 2)


def gauss_pulse(x_nm, pw50_nm: float):
    """纵向 Gauss 脉冲（源书式 2.38）。"""
    x = np.asarray(x_nm, dtype=float)
    beta = pw50_nm / (2.0 * np.sqrt(np.log(2.0)))
    return np.exp(-((x / beta) ** 2))


def perpendicular_pulse_erf(x_nm, dpw50_nm: float):
    """垂直未微分读出脉冲 erf(x/beta_P)（式 5-8 / 源书式 2.30、2.36）。"""
    x = np.asarray(x_nm, dtype=float)
    beta = dpw50_nm / (2.0 * np.sqrt(np.log(2.0)))
    from scipy.special import erf

    return erf(x / beta)


def perpendicular_pulse_gauss(x_nm, dpw50_nm: float):
    """垂直微分读出脉冲（式 5-8 / 源书式 2.33），按峰值归一化。"""
    x = np.asarray(x_nm, dtype=float)
    beta = dpw50_nm / (2.0 * np.sqrt(np.log(2.0)))
    return np.exp(-((x / beta) ** 2))


def perpendicular_dpw50(
    g_nm: float, delta_nm: float, a_nm: float, d_nm: float, t_nm: float, s_nm: float
) -> float:
    """垂直微分半峰宽 dPW50（式 5-8 / 源书式 2.34），返回 nm。"""
    wp = (d_nm**2 + 2.0 * d_nm * (t_nm + s_nm) - s_nm * (2.0 * s_nm + t_nm)) / 6.0
    arg = g_nm**2 + g_nm * delta_nm + delta_nm**2 / 2.0 + np.pi**4 * a_nm**2 / 8.0 + 12.0 * wp
    return float(0.96 * np.sqrt(max(arg, 0.0)))


def longitudinal_pw50(g_nm: float, delta_nm: float, a_nm: float, gamma_nm: float) -> float:
    """纵向半峰宽 PW50 近似（源书式 2.34），返回 nm。"""
    arg = g_nm**2 + g_nm * delta_nm + delta_nm**2 / 2.0 + np.pi**4 * a_nm**2 / 8.0
    return float(np.sqrt(max(arg, 0.0)) + 1.1 * gamma_nm)


def rolloff_lorentz(x):
    """纵向 Lorentz 脉冲的 roll-off（式 5-9 / 源书式 2.43），x=PW50/B。"""
    x = np.asarray(x, dtype=float)
    u = np.pi * x / 2.0
    with np.errstate(over="ignore", divide="ignore"):
        out = np.where(u > 1e-9, u / np.sinh(u), 1.0)
    return out


def rolloff_gauss(x):
    """纵向 Gauss 脉冲的 roll-off（式 5-9 / 源书式 2.43），x=PW50/B。"""
    x = np.asarray(x, dtype=float)
    c = (np.pi * x / (4.0 * np.sqrt(np.log(2.0)))) ** 2
    out = np.zeros_like(x)
    for l in range(400):
        term = np.exp(-c * (2 * l + 1) ** 2)
        out = out + term
        if np.all(term < 1e-14):
            break
    return x * np.sqrt(np.pi) / np.sqrt(np.log(2.0)) * out


def rolloff_voigt(x, eta: float = 0.43):
    """纵向 Voigt(eta) 的 roll-off（式 5-9 / 源书式 2.43）。"""
    return eta * rolloff_lorentz(x) + (1.0 - eta) * rolloff_gauss(x)


def rolloff_exact(
    x,
    *,
    pw50_nm: float,
    g_nm=50.0,
    delta_nm=5.0,
    a_nm=5.0,
    gamma_nm=15.0,
    nk: int = 20000,
    kmax_nm_inv: float = 8.0,
):
    """纵向精确脉冲的方波 roll-off（式 5-9 / 源书式 2.42，谐波叠加）。

    x=PW50/B；按 V_peak(B)/V_peak = (2/B) sum_{l odd} V_sp(l*pi/B)/V_sp(0)
    计算，V_sp(0)=(1/pi) int_0^inf V_sp(k) dk。
    """
    x = np.atleast_1d(np.asarray(x, dtype=float))
    k = np.linspace(1e-6, kmax_nm_inv, nk)
    env = replay_envelope(k, g_nm=g_nm, delta_nm=delta_nm, a_nm=a_nm, gamma_nm=gamma_nm)
    v0 = simpson(env, x=k) / np.pi
    out = np.empty_like(x)
    for i, xi in enumerate(x):
        if xi <= 0:
            out[i] = 1.0
            continue
        b = pw50_nm / xi
        total = 0.0
        l = 1
        while True:
            kk = l * np.pi / b
            if kk > kmax_nm_inv:
                break
            total += float(replay_envelope(np.array([kk]), g_nm=g_nm, delta_nm=delta_nm, a_nm=a_nm, gamma_nm=gamma_nm)[0])
            l += 2
            if l > 20001:
                break
        out[i] = 2.0 * total / b / v0
    return out


def rolloff_perpendicular(x, *, approximate: bool = True):
    """垂直未微分脉冲的 roll-off（式 5-9 / 源书式 2.44、2.45），x=dPW50/B。

    ``approximate=True`` 用教材式 2.45 的指数近似；否则用式 2.44 的谐波级数
    （注意源书式 2.44 的归一化在翻译稿中有 OCR 歧义，默认取 2.45）。
    """
    x = np.asarray(x, dtype=float)
    if approximate:
        return np.exp(-np.log(2.0) * x**2)
    tot = np.zeros_like(x)
    for l in range(600):
        term = ((-1) ** l) / (2 * l + 1) * np.exp(-0.89 * (2 * l + 1) ** 2 * x**2)
        tot = tot + term
        if np.all(np.abs(term) < 1e-14):
            break
    return 4.0 / np.pi * tot


def rolloff_differentiated_gauss(x):
    """垂直微分脉冲（Gauss）的 roll-off，等同纵向 Gauss 式（x=dPW50/B）。"""
    return rolloff_gauss(x)


def d50_from_curve(x_grid, curve) -> float:
    """从归一化 roll-off 曲线数值求 D50（曲线下降到 0.5 的归一化密度）。"""
    x = np.asarray(x_grid, dtype=float)
    y = np.asarray(curve, dtype=float)
    below = np.flatnonzero(y < 0.5)
    if below.size == 0:
        return float("nan")
    j = below[0]
    if j == 0:
        return float(x[0])
    x0, x1 = x[j - 1], x[j]
    y0, y1 = y[j - 1], y[j]
    return float(x0 + (0.5 - y0) * (x1 - x0) / (y1 - y0))


def magnetization_variance(mr_over_ms: float) -> float:
    """纵向介质 DC 剩磁方差 <M^2>-Mr^2（归一化到 Ms^2，源书式 2.56）。

    theta_c 由 Mr/Ms = sin(theta_c)/theta_c 数值反解；Mr/Ms=1 时方差为 0。
    """
    ratio = float(np.clip(mr_over_ms, 1e-6, 1.0))
    if ratio >= 1.0 - 1e-9:
        return 0.0
    lo, hi = 1e-6, np.pi
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if np.sin(mid) / mid > ratio:
            lo = mid
        else:
            hi = mid
    theta = 0.5 * (lo + hi)
    var = 0.5 * (1.0 + np.sin(2.0 * theta) / (2.0 * theta)) - (np.sin(theta) / theta) ** 2
    return float(max(var, 0.0))


def dc_noise_psd(
    k_nm_inv,
    *,
    pw50_nm: float = 74.0,
    mr_over_ms: float = 0.8,
    sigma_v_over_v: float = 0.2,
    s_cross_nm: float = 10.0,
    s_down_nm: float = 10.0,
    w_read_nm: float = 200.0,
):
    """DC 剩磁噪声谱（式 5-11 / 源书式 2.57），返回任意单位 PSD。

    垂直记录时把 PW50 换成 dPW50；方形度=1（Mr/Ms=1）时方差为 0，谱消失。
    """
    k = np.atleast_1d(np.asarray(k_nm_inv, dtype=float))
    var = magnetization_variance(mr_over_ms)
    scale = s_cross_nm * s_down_nm / max(w_read_nm, 1e-9)
    return (
        (1.0 + sigma_v_over_v**2)
        * var
        * scale
        * np.exp(-(k * pw50_nm) ** 2 / 6.0)
    )


def transition_noise_psd(
    k_nm_inv,
    *,
    g_nm: float = 50.0,
    delta_nm: float = 5.0,
    a_nm: float = 5.0,
    gamma_nm: float = 15.0,
    sigma_v_over_v: float = 0.2,
    s_cross_nm: float = 15.0,
    w_read_nm: float = 200.0,
):
    """翻转噪声谱（式 5-12 / 源书式 2.60 的纵向形式），返回任意单位 PSD。

    只保留抖动/形状涨落主导项：e^{-2k gamma} sinc^2(kg/2) sinc^2(k(g+delta)/2)
    [1-(pi^2 k a/4/sinh(pi^2 k a/4))^2]。
    """
    k = np.atleast_1d(np.asarray(k_nm_inv, dtype=float))
    k = np.maximum(k, 1e-9)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        x = np.pi**2 * k * a_nm / 4.0
        shape = np.where(x < 700.0, x / np.sinh(np.minimum(x, 700.0)), 0.0)
        s1 = np.sin(k * g_nm / 2.0) / (k * g_nm / 2.0)
        s2 = np.sin(k * (g_nm + delta_nm) / 2.0) / (k * (g_nm + delta_nm) / 2.0)
        env = (
            np.exp(-2.0 * k * gamma_nm)
            * s1**2
            * s2**2
            * np.maximum(1.0 - shape**2, 0.0)
        )
    env = np.nan_to_num(env, nan=1.0, posinf=0.0, neginf=0.0)
    return (1.0 + sigma_v_over_v**2) * s_cross_nm / max(w_read_nm, 1e-9) * env


def transition_jitter_sigma(a_nm: float, s_cross_nm: float, w_read_nm: float) -> float:
    """抖动模式方差 sigma_j（式 5-12 / 源书式 2.62），返回 nm。"""
    return float(np.sqrt(np.pi**4 / 48.0 * a_nm**2 * s_cross_nm / max(w_read_nm, 1e-9)))


def shape_jitter_sigma(a_nm: float) -> float:
    """形状涨落方差 sigma_a（式 5-12 / 源书式 2.62），返回 nm。"""
    return float(np.sqrt(np.pi**4 * a_nm**2 / 120.0))


def lorentz_ft(k_nm_inv, pw50_nm: float):
    """Lorentz 脉冲的幅度谱（源书式 2.40），归一化到 k=0 处为 1。"""
    k = np.abs(np.asarray(k_nm_inv, dtype=float))
    return np.exp(-pw50_nm * k / 2.0)


def gauss_ft(k_nm_inv, pw50_nm: float):
    """Gauss 脉冲的幅度谱（源书式 2.40），归一化到 k=0 处为 1。"""
    k = np.abs(np.asarray(k_nm_inv, dtype=float))
    return np.exp(-(pw50_nm * k) ** 2 / (16.0 * np.log(2.0)))


def head_potential_ft(k_nm_inv, *, g_nm=50.0, delta_nm=5.0, gamma_nm=15.0):
    """互易读出势函数 Phi_s(k) e^{-k gamma}（式 5-6 / 源书式 2.25），任意单位。"""
    k = np.atleast_1d(np.asarray(k_nm_inv, dtype=float))
    k = np.maximum(k, 1e-9)
    with np.errstate(divide="ignore", invalid="ignore"):
        phi = 4.0 / (k**2 * g_nm) * np.sin(k * g_nm / 2.0) * np.sin(
            k * (g_nm + delta_nm) / 2.0
        )
    phi = np.nan_to_num(phi, nan=1.0, posinf=0.0, neginf=0.0)
    return np.abs(phi) * np.exp(-k * gamma_nm)


def transition_magnetization_ft(k_nm_inv, *, a_nm=5.0, mr_over_ms=1.0):
    """tanh 翻转剖面的磁化谱 |M(k)|（式 5-6 / 源书式 2.26），任意单位。"""
    k = np.atleast_1d(np.asarray(k_nm_inv, dtype=float))
    k = np.maximum(k, 1e-9)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        x = np.pi**2 * k * a_nm / 4.0
        m = (2.0 / k) * np.where(x < 700.0, x / np.sinh(np.minimum(x, 700.0)), 0.0)
    m = np.nan_to_num(m, nan=1.0, posinf=0.0, neginf=0.0)
    return np.abs(m) * mr_over_ms
