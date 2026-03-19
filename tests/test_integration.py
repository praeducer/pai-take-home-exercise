import os
import subprocess

import pytest


@pytest.mark.integration
def test_full_pipeline_dry_run():
    """Full pipeline in dry-run mode — zero API cost, verifies module wiring."""
    result = subprocess.run(
        [
            "python",
            "-m",
            "src.pipeline.run_pipeline",
            "inputs/sample_sku_brief.json",
            "--dry-run",
        ],
        env={**os.environ, "PAI_DRY_RUN": "1"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Pipeline failed: {result.stderr}"
    assert "Pipeline complete" in result.stdout
    assert "0 images" in result.stdout
