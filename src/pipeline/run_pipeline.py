import os
import time
import uuid
from pathlib import Path

from .asset_manager import build_output_key, upload_output
from .image_generator import MODEL_TIERS, generate_image
from .output_manager import write_manifest
from .prompt_constructor import build_image_prompt, build_text_overlay_content
from .sku_parser import parse_sku_brief
from .text_overlay import apply_overlay
from .text_reasoning import enhance_prompt_with_reasoning, get_bedrock_client

RATIO_FORMAT_MAP = {
    "1:1": "front_label",
    "9:16": "back_label",
    "16:9": "wraparound",
}


def run_pipeline(
    sku_brief_path: str,
    model_tier: str = "dev",
    dry_run: bool = False,
    output_bucket: str = None,
    profile: str = "pai-exercise",
) -> list[str]:
    """Run full pipeline for all products x all 3 ratios. Returns list of S3 output keys."""
    start_time = time.time()
    run_id = str(uuid.uuid4())

    bucket = output_bucket or os.environ.get("PAI_OUTPUT_BUCKET", "")
    dry_run = dry_run or bool(os.environ.get("PAI_DRY_RUN"))

    brief = parse_sku_brief(sku_brief_path)
    sku_id = brief["sku_id"]
    region = brief.get("region", "us-east")

    text_client = None if dry_run else get_bedrock_client()
    model_id = MODEL_TIERS.get(model_tier, MODEL_TIERS["dev"])

    output_keys = []
    errors = []

    for product in brief["products"]:
        product_slug = (product.get("flavor") or product["name"]).lower().replace(" ", "-")
        for aspect_ratio, format_name in RATIO_FORMAT_MAP.items():
            try:
                base_prompt = build_image_prompt(brief, product, aspect_ratio)
                prompt = (
                    enhance_prompt_with_reasoning(text_client, base_prompt, product, dry_run)
                    if text_client
                    else base_prompt
                )

                image_bytes = generate_image(prompt, aspect_ratio, model_tier, dry_run, profile)
                overlay_content = build_text_overlay_content(brief, product)
                composited = apply_overlay(image_bytes, overlay_content, aspect_ratio)

                # Always save locally to outputs/results/
                local_dir = Path("outputs/results") / sku_id / region / format_name
                local_dir.mkdir(parents=True, exist_ok=True)
                local_path = local_dir / f"{product_slug}.png"
                local_path.write_bytes(composited)

                if not dry_run and bucket:
                    s3_key = build_output_key(sku_id, region, format_name, f"{product_slug}.png")
                    upload_output(bucket, s3_key, composited, profile)
                    output_keys.append(s3_key)
                    print(f"  + {product['name']} ({product.get('flavor', '')}) {aspect_ratio} -> {local_path} + s3://{bucket}/{s3_key}")
                else:
                    print(
                        f"  + {product['name']} ({product.get('flavor', '')}) {aspect_ratio} -> {local_path} [dry-run, no S3]"
                    )

            except Exception as e:
                errors.append(
                    {"product": product["name"], "ratio": aspect_ratio, "error": str(e)}
                )
                print(f"  ! {product['name']} {aspect_ratio}: {e}")

    duration = round(time.time() - start_time, 2)
    write_manifest(
        {
            "run_id": run_id,
            "models_used": [model_id],
            "images_generated": len(output_keys),
            "dry_run": dry_run,
            "errors": errors,
            "duration_seconds": duration,
        },
        bucket,
        sku_id,
        region,
        profile,
        dry_run=dry_run,
    )

    print(f"\nPipeline complete: {len(output_keys)} images, {duration}s")
    return output_keys


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PAI packaging image generation pipeline")
    parser.add_argument("sku_brief_path", help="Path to SKU brief JSON file")
    parser.add_argument("--model-tier", default="dev", choices=["dev", "iterate", "final"])
    parser.add_argument("--dry-run", action="store_true", help="Skip Bedrock calls and S3 uploads")
    parser.add_argument("--output-bucket", default=None, help="S3 output bucket name")
    parser.add_argument("--profile", default="pai-exercise", help="AWS profile name")
    args = parser.parse_args()

    run_pipeline(
        args.sku_brief_path,
        model_tier=args.model_tier,
        dry_run=args.dry_run,
        output_bucket=args.output_bucket,
        profile=args.profile,
    )
