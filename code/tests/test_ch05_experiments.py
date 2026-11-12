"""第 5 章实验脚本的冒烟测试（小采样、<60 s、不污染仓库 manifest）。

每个脚本都以 ``--quick`` 运行到 pytest 的临时目录，并断言：
- 约定的图件文件已生成且为 300 dpi 白底 PNG；
- CSV 已写出且含表头；
- 通过 ``HDDBOOK_MANIFEST`` 重定向的临时 manifest 中出现了对应 figure_id。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

CODE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CODE_ROOT))
sys.path.insert(0, str(CODE_ROOT / "experiments"))

import ch05_channel_sim  # noqa: E402
import ch05_media_noise  # noqa: E402
import ch05_pulse_shape  # noqa: E402
import ch05_rolloff  # noqa: E402
import ch05_snr_calib  # noqa: E402
import ch05_write_field  # noqa: E402

FIGURES = {
    "ch05_write_field": [
        "fig05-01-write-geometry.png",
        "fig05-02-karlqvist-field.png",
        "fig05-03-hysteresis-a.png",
    ],
    "ch05_pulse_shape": ["fig05-04-reciprocity.png", "fig05-05-pulse-shape.png"],
    "ch05_rolloff": ["fig05-06-rolloff.png"],
    "ch05_media_noise": ["fig05-07-media-noise.png"],
    "ch05_channel_sim": [
        "fig05-08-channel-model.png",
        "fig05-10-isi-peak-detect.png",
        "fig05-11-read-channel.png",
        "fig05-12-equalized-scatter.png",
    ],
    "ch05_snr_calib": ["fig05-09-simulator-flow.png"],
}

IDS = {
    "ch05_write_field": {"fig:5-1", "fig:5-2", "fig:5-3"},
    "ch05_pulse_shape": {"fig:5-4", "fig:5-5"},
    "ch05_rolloff": {"fig:5-6"},
    "ch05_media_noise": {"fig:5-7"},
    "ch05_channel_sim": {"fig:5-8", "fig:5-10", "fig:5-11", "fig:5-12"},
    "ch05_snr_calib": {"fig:5-9"},
}


def _run(monkeypatch, tmp_path, module, name: str):
    """运行一个脚本的 --quick 模式并返回 (输出目录, CSV, manifest 条目)。"""
    monkeypatch.setenv("HDDBOOK_MANIFEST", str(tmp_path / "manifest.yaml"))
    outdir = tmp_path / "figs"
    csv_path = tmp_path / f"{name}.csv"
    module.main(["--out", str(outdir), "--csv", str(csv_path), "--quick"])

    manifest = yaml.safe_load((tmp_path / "manifest.yaml").read_text(encoding="utf-8"))
    return outdir, csv_path, manifest


def _assert_png_300dpi_white(path: Path):
    from PIL import Image

    assert path.exists(), f"missing figure: {path}"
    assert path.stat().st_size > 10_000, f"figure too small: {path}"
    with Image.open(path) as im:
        dpi = im.info.get("dpi", (0, 0))
        assert dpi[0] >= 299 and dpi[1] >= 299, f"dpi={dpi} for {path}"
        assert im.convert("RGB").getpixel((0, 0)) == (255, 255, 255), f"non-white background: {path}"


def test_write_field_smoke(monkeypatch, tmp_path):
    outdir, csv_path, manifest = _run(monkeypatch, tmp_path, ch05_write_field, "ch05_write_field")
    for name in FIGURES["ch05_write_field"]:
        _assert_png_300dpi_white(outdir / name)
    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert "a_nm" in header and "x0_nm" in header
    ids = {e["figure_id"] for e in manifest}
    assert ids == IDS["ch05_write_field"]
    assert all(e["chapter"] == 5 for e in manifest)


def test_pulse_shape_smoke(monkeypatch, tmp_path):
    outdir, csv_path, manifest = _run(monkeypatch, tmp_path, ch05_pulse_shape, "ch05_pulse_shape")
    for name in FIGURES["ch05_pulse_shape"]:
        _assert_png_300dpi_white(outdir / name)
    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert "v_exact" in header and "pw50_fit_nm" in header
    ids = {e["figure_id"] for e in manifest}
    assert ids == IDS["ch05_pulse_shape"]


def test_rolloff_smoke(monkeypatch, tmp_path):
    outdir, csv_path, manifest = _run(monkeypatch, tmp_path, ch05_rolloff, "ch05_rolloff")
    for name in FIGURES["ch05_rolloff"]:
        _assert_png_300dpi_white(outdir / name)
    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert "d50_repro_l" in header
    ids = {e["figure_id"] for e in manifest}
    assert ids == IDS["ch05_rolloff"]


def test_media_noise_smoke(monkeypatch, tmp_path):
    outdir, csv_path, manifest = _run(monkeypatch, tmp_path, ch05_media_noise, "ch05_media_noise")
    for name in FIGURES["ch05_media_noise"]:
        _assert_png_300dpi_white(outdir / name)
    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert "psd_total_norm" in header
    ids = {e["figure_id"] for e in manifest}
    assert ids == IDS["ch05_media_noise"]


def test_channel_sim_smoke(monkeypatch, tmp_path):
    outdir, csv_path, manifest = _run(monkeypatch, tmp_path, ch05_channel_sim, "ch05_channel_sim")
    for name in FIGURES["ch05_channel_sim"]:
        _assert_png_300dpi_white(outdir / name)
    header = csv_path.read_text(encoding="utf-8").splitlines()[0]
    assert "ser" in header and "sigma_j_over_pw50" in header
    ids = {e["figure_id"] for e in manifest}
    assert ids == IDS["ch05_channel_sim"]


def test_snr_calib_smoke(monkeypatch, tmp_path):
    outdir, csv_path, manifest = _run(monkeypatch, tmp_path, ch05_snr_calib, "ch05_snr_calib")
    for name in FIGURES["ch05_snr_calib"]:
        _assert_png_300dpi_white(outdir / name)
    rows = csv_path.read_text(encoding="utf-8").splitlines()
    assert rows[0].startswith("iteration")
    assert len(rows) > 2  # 至少包含初值与若干迭代
    ids = {e["figure_id"] for e in manifest}
    assert ids == IDS["ch05_snr_calib"]
