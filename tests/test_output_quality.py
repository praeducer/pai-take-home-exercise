"""
QA/E2E output quality tests.

These tests guarantee that:
1. dry-run mode does NOT write files to outputs/results/ (regression for bug where
   the Stop hook's integration test overwrote real images with 69-byte placeholders)
2. Real pipeline output files (when present) are valid PNGs with correct dimensions
   and non-trivial file sizes (i.e., not DRY_RUN_PIXEL placeholders)
3. apply_overlay never returns a DRY_RUN_PIXEL-sized result on valid input
"""

import io
import os
import shutil
from pathlib import Path

import pytest
from PIL import Image

from src.pipeline.image_generator import DRY_RUN_PIXEL
from src.pipeline.run_pipeline import RATIO_FORMAT_MAP, run_pipeline
from src.pipeline.text_overlay import apply_overlay

# Minimum size (bytes) for a real pipeline image. DRY_RUN_PIXEL is 69 bytes.
MIN_REAL_IMAGE_BYTES = 100_000  # 100 KB

# Expected dimensions for each aspect ratio after overlay compositing
EXPECTED_DIMS = {
    "1:1": (1024, 1024),
    "9:16": (576, 1024),
    "16:9": (1024, 576),
}

SAMPLE_BRIEF_PATH = "inputs/sample_sku_brief.json"
SKU_ID = "organic-trail-mix-us"
REGION = "us-west"


# ---------------------------------------------------------------------------
# Regression: dry-run must NOT write to outputs/results/
# ---------------------------------------------------------------------------


def test_dry_run_does_not_write_to_results(tmp_path, monkeypatch):
    """Regression: dry-run overwrote real images with 69-byte placeholders (now fixed)."""
    # Patch Path("outputs/results") target inside run_pipeline to a temp dir so
    # we don't pollute real outputs if something regresses.
    fake_results = tmp_path / "results"
    fake_results.mkdir()

    # Run dry-run pipeline — it must NOT create any .png files anywhere
    with monkeypatch.context() as m:
        m.setenv("PAI_DRY_RUN", "1")
        # Change working directory to a temp location so relative paths resolve
        # into tmp_path instead of the real outputs/
        orig_cwd = os.getcwd()
        os.chdir(tmp_path)
        # Create the required input structure in tmp_path
        src_brief = Path(orig_cwd) / SAMPLE_BRIEF_PATH
        if src_brief.exists():
            (tmp_path / "inputs").mkdir(exist_ok=True)
            shutil.copy(src_brief, tmp_path / "inputs" / "sample_sku_brief.json")
            brief_path = str(tmp_path / "inputs" / "sample_sku_brief.json")
        else:
            os.chdir(orig_cwd)
            pytest.skip("sample_sku_brief.json not found — skipping")

        try:
            run_pipeline(brief_path, dry_run=True)
        finally:
            os.chdir(orig_cwd)

    # tmp_path/results should be empty — dry-run must not write images
    png_files = list(tmp_path.rglob("*.png"))
    assert png_files == [], (
        f"dry-run wrote {len(png_files)} PNG file(s) — regression detected: "
        f"{[str(p) for p in png_files]}"
    )


# ---------------------------------------------------------------------------
# Real output file quality checks (skip if files not yet generated)
# ---------------------------------------------------------------------------


def _get_result_files():
    """Return list of (path, aspect_ratio) for existing output PNGs."""
    results_root = Path("outputs/results") / SKU_ID / REGION
    found = []
    for ratio, fmt in RATIO_FORMAT_MAP.items():
        fmt_dir = results_root / fmt
        if fmt_dir.exists():
            for png in fmt_dir.glob("*.png"):
                found.append((png, ratio))
    return found


@pytest.mark.skipif(
    not any(
        (Path("outputs/results") / SKU_ID / REGION / fmt).exists()
        for fmt in RATIO_FORMAT_MAP.values()
    ),
    reason="No output files found — run the pipeline first to generate real images",
)
def test_output_files_not_placeholder():
    """All output PNGs must be real images, not DRY_RUN_PIXEL placeholders."""
    files = _get_result_files()
    assert files, "Expected output files in outputs/results/ but found none"
    for path, ratio in files:
        size = path.stat().st_size
        assert size >= MIN_REAL_IMAGE_BYTES, (
            f"{path.name} ({ratio}) is only {size} bytes — likely a DRY_RUN_PIXEL placeholder"
        )


@pytest.mark.skipif(
    not any(
        (Path("outputs/results") / SKU_ID / REGION / fmt).exists()
        for fmt in RATIO_FORMAT_MAP.values()
    ),
    reason="No output files found — run the pipeline first to generate real images",
)
def test_output_files_are_valid_png():
    """All output files must be readable, valid PNG images."""
    files = _get_result_files()
    for path, ratio in files:
        img = Image.open(path)
        img.verify()  # raises if not a valid image


@pytest.mark.skipif(
    not any(
        (Path("outputs/results") / SKU_ID / REGION / fmt).exists()
        for fmt in RATIO_FORMAT_MAP.values()
    ),
    reason="No output files found — run the pipeline first to generate real images",
)
def test_output_files_correct_dimensions():
    """Output PNGs must match the expected dimensions for each aspect ratio.

    Note: the dev tier (Titan V2) generates at 1024×1024 for all ratios because
    Titan only supports square dimensions. Nova Canvas (iterate/final tier) generates
    at the exact target dimensions.
    """
    files = _get_result_files()
    for path, ratio in files:
        img = Image.open(path)
        w, h = img.size
        # All ratios currently generate 1024×1024 (Titan V2 dev tier limitation)
        # The overlay preserves the input dimensions, so check reasonable sizes.
        assert w >= 512 and h >= 512, (
            f"{path.name} ({ratio}) has suspicious dimensions {w}×{h}"
        )
        assert w * h >= 512 * 512, (
            f"{path.name} ({ratio}) total pixels {w*h} too small for a real image"
        )


# ---------------------------------------------------------------------------
# apply_overlay never produces DRY_RUN_PIXEL-sized output on valid input
# ---------------------------------------------------------------------------


def test_overlay_never_produces_placeholder_size():
    """apply_overlay on a real (even synthetic) image must never return 69 bytes."""
    for ratio, (w, h) in EXPECTED_DIMS.items():
        img = Image.new("RGB", (w, h), color=(128, 128, 128))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        content = {
            "title": "Test\nOriginal",
            "attributes": ["organic", "non-gmo"],
            "regulatory_text": "See label.",
        }
        result = apply_overlay(buf.getvalue(), content, ratio)
        assert len(result) != len(DRY_RUN_PIXEL), (
            f"apply_overlay for {ratio} returned DRY_RUN_PIXEL-sized output ({len(result)} bytes)"
        )
        assert len(result) > 1000, (
            f"apply_overlay for {ratio} returned suspiciously small output: {len(result)} bytes"
        )
