import boto3


def check_s3_asset(bucket: str, key: str, profile: str = "pai-exercise") -> bool:
    """Return True if object exists in S3."""
    s3 = boto3.Session(profile_name=profile, region_name="us-east-1").client("s3")
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except s3.exceptions.ClientError:
        return False


def download_s3_asset(bucket: str, key: str, local_path: str, profile: str = "pai-exercise") -> str:
    """Download S3 object to local path. Returns local_path."""
    s3 = boto3.Session(profile_name=profile, region_name="us-east-1").client("s3")
    s3.download_file(bucket, key, local_path)
    return local_path


def upload_output(bucket: str, key: str, image_bytes: bytes, profile: str = "pai-exercise") -> None:
    """Upload image bytes to S3 output bucket."""
    s3 = boto3.Session(profile_name=profile, region_name="us-east-1").client("s3")
    s3.put_object(Bucket=bucket, Key=key, Body=image_bytes, ContentType="image/png")


def build_output_key(sku_id: str, region: str, format_name: str, filename: str) -> str:
    """Build S3 key: {sku_id}/{region}/{format_name}/{filename}"""
    return f"{sku_id}/{region}/{format_name}/{filename}"
