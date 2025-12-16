"""
S3 Client for Worker
Handles file downloads and uploads to AWS S3.
"""

import os
import logging
from pathlib import Path
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load .env from worker/ directory first, then try parent directory
env_file = Path(__file__).parent / ".env"
env_local_file = Path(__file__).parent.parent / ".env.local"

if env_file.exists():
    load_dotenv(env_file)
elif env_local_file.exists():
    load_dotenv(env_local_file)
else:
    load_dotenv()

logger = logging.getLogger(__name__)

# Initialize S3 client
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

_s3_client = None


def get_client():
    """Get S3 client instance."""
    global _s3_client
    if _s3_client is None:
        if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
            raise Exception("AWS credentials not configured")
        _s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
    return _s3_client


async def download_from_s3(bucket: str, key: str, local_path: str) -> bool:
    """Download a file from S3 to local path."""
    try:
        client = get_client()
        logger.info(f"Downloading s3://{bucket}/{key} to {local_path}")
        client.download_file(bucket, key, local_path)
        logger.info(f"Downloaded {os.path.getsize(local_path)} bytes")
        return True
    except ClientError as e:
        logger.error(f"Error downloading from S3: {e}")
        return False


async def upload_to_s3(
    local_path: str,
    bucket: str,
    key: str,
    content_type: Optional[str] = None
) -> bool:
    """Upload a file to S3."""
    try:
        client = get_client()
        
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type
        
        logger.info(f"Uploading {local_path} to s3://{bucket}/{key}")
        client.upload_file(local_path, bucket, key, ExtraArgs=extra_args if extra_args else None)
        return True
    except ClientError as e:
        logger.error(f"Error uploading to S3: {e}")
        return False


async def upload_directory_to_s3(
    local_dir: str,
    bucket: str,
    s3_prefix: str
) -> bool:
    """Upload an entire directory to S3."""
    try:
        client = get_client()
        
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_dir)
                s3_key = f"{s3_prefix}/{relative_path}"
                
                logger.info(f"Uploading {local_path} to s3://{bucket}/{s3_key}")
                client.upload_file(local_path, bucket, s3_key)
        
        return True
    except ClientError as e:
        logger.error(f"Error uploading directory to S3: {e}")
        return False


async def list_objects(bucket: str, prefix: str) -> list:
    """List objects in S3 bucket with given prefix."""
    try:
        client = get_client()
        response = client.list_objects_v2(Bucket=bucket, Prefix=prefix)
        
        if "Contents" in response:
            return [obj["Key"] for obj in response["Contents"]]
        return []
    except ClientError as e:
        logger.error(f"Error listing S3 objects: {e}")
        return []
