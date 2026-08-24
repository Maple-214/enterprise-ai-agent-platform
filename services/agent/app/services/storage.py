import io
import boto3
from botocore.client import Config
from ..core.config import settings


def client():
    return boto3.client(
        "s3",
        endpoint_url=f"http{'s' if settings.minio_secure else ''}://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ensure_bucket() -> None:
    s3 = client()
    try:
        s3.head_bucket(Bucket=settings.minio_bucket)
    except Exception:
        s3.create_bucket(Bucket=settings.minio_bucket)


def put_object(key: str, data: bytes, content_type: str) -> None:
    client().put_object(Bucket=settings.minio_bucket, Key=key, Body=io.BytesIO(data), ContentType=content_type)


def get_object(key: str) -> bytes:
    return client().get_object(Bucket=settings.minio_bucket, Key=key)["Body"].read()
