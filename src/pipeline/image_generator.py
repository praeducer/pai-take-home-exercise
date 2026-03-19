import base64
import hashlib
import json
import os
import time
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

CACHE_DIR = Path.home() / ".cache" / "pai-pipeline"

MODEL_TIERS = {
    "dev": "amazon.titan-image-generator-v2:0",
    "iterate": "amazon.nova-canvas-v1:0",
    "final": "amazon.nova-canvas-v1:0",
}

ASPECT_RATIO_DIMS = {
    "1:1": (1024, 1024),
    "9:16": (576, 1024),
    "16:9": (1024, 576),
}

# Minimal valid 1x1 white PNG — used as dry-run placeholder
DRY_RUN_PIXEL = bytes(
    [
        0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,
        0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,
        0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
        0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
        0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,
        0x54, 0x08, 0xD7, 0x63, 0xF8, 0xFF, 0xFF, 0x3F,
        0x00, 0x05, 0xFE, 0x02, 0xFE, 0xDC, 0xCC, 0x59,
        0xE7, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, 0x4E,
        0x44, 0xAE, 0x42, 0x60, 0x82,
    ]
)


def _cache_key(prompt: str, width: int, height: int, model_id: str) -> str:
    content = f"{prompt}|{width}|{height}|{model_id}"
    return hashlib.sha256(content.encode()).hexdigest()


def _get_cached(cache_key: str) -> bytes | None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / f"{cache_key}.png"
    return cache_file.read_bytes() if cache_file.exists() else None


def _save_cached(cache_key: str, image_bytes: bytes) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{cache_key}.png").write_bytes(image_bytes)


def generate_image(
    prompt: str,
    aspect_ratio: str = "1:1",
    model_tier: str = "dev",
    dry_run: bool = False,
    profile: str = "pai-exercise",
) -> bytes:
    """Generate image via Bedrock. Returns PNG bytes. Falls back to lower tier on throttling."""
    if dry_run or os.environ.get("PAI_DRY_RUN"):
        return DRY_RUN_PIXEL

    width, height = ASPECT_RATIO_DIMS.get(aspect_ratio, (1024, 1024))
    model_id = MODEL_TIERS.get(model_tier, MODEL_TIERS["dev"])

    # Titan V2 only supports square dimensions natively; use 1024x1024 for non-square ratios
    if "titan" in model_id and (width, height) != (1024, 1024):
        width, height = 1024, 1024

    key = _cache_key(prompt, width, height, model_id)
    cached = _get_cached(key)
    if cached:
        print(f"    [cache hit] {key[:16]}...")
        return cached

    session = boto3.Session(profile_name=profile, region_name="us-east-1")
    client = session.client("bedrock-runtime")

    body = json.dumps(
        {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {"text": prompt},
            "imageGenerationConfig": {
                "width": width,
                "height": height,
                "quality": "standard",
                "numberOfImages": 1,
            },
        }
    )

    for attempt in range(3):
        try:
            response = client.invoke_model(modelId=model_id, body=body)
            result = json.loads(response["body"].read())
            image_bytes = base64.b64decode(result["images"][0])
            _save_cached(key, image_bytes)
            return image_bytes

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ("ThrottlingException", "ServiceUnavailableException") and attempt < 2:
                time.sleep(2 ** (attempt + 1))
                continue
            if attempt == 2 and model_tier != "dev":
                # Fall back to dev tier if higher tier is throttled
                return generate_image(prompt, aspect_ratio, "dev", False, profile)
            raise

    raise RuntimeError(f"Image generation failed after 3 attempts for model {model_id}")
