import boto3
import uuid
import os

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
    aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET_NAME = "secure-data-sharing-abe"

def save_encrypted_file(data: bytes) -> str:
    key = f"files/{uuid.uuid4()}"
    s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=data)
    return key

def load_encrypted_file(key: str) -> bytes:
    obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    return obj["Body"].read()
