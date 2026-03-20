import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import boto3


def write_manifest(
    run_data: dict,
    bucket: str,
    sku_id: str,
    region: str,
    profile: str = "pai-exercise",
    dry_run: bool = False,
) -> None:
    """Write pipeline run manifest to S3 (if not dry_run) and local outputs/runs/."""
    manifest = {
        "run_id": run_data.get("run_id", str(uuid.uuid4())),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sku_id": sku_id,
        "region": region,
        "models_used": run_data.get("models_used", []),
        "images_generated": run_data.get("images_generated", 0),
        "dry_run": run_data.get("dry_run", False),
        "errors": run_data.get("errors", []),
        "duration_seconds": run_data.get("duration_seconds", 0),
    }

    manifest_json = json.dumps(manifest, indent=2)

    # Write to S3 only when we have a bucket and are not in dry-run mode
    if bucket and not dry_run:
        s3 = boto3.Session(profile_name=profile, region_name="us-east-1").client("s3")
        s3_key = f"{sku_id}/{region}/manifest.json"
        s3.put_object(
            Bucket=bucket,
            Key=s3_key,
            Body=manifest_json.encode(),
            ContentType="application/json",
        )

    # Always write locally
    local_dir = Path("outputs/runs")
    local_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_file = local_dir / f"{ts}_{sku_id}.json"
    local_file.write_text(f"{manifest_json}\n", encoding="utf-8")
