from dataclasses import dataclass
from datetime import timedelta

import boto3
from botocore.client import Config


@dataclass(frozen=True)
class StorageConfig:
    endpoint_url: str
    public_endpoint_url: str
    uploads_bucket: str
    outputs_bucket: str
    access_key_id: str
    secret_access_key: str
    signed_url_ttl_seconds: int = 3600


class StorageService:
    def __init__(self, config: StorageConfig, public_urls: bool = False) -> None:
        self.config = config
        endpoint_url = config.public_endpoint_url if public_urls else config.endpoint_url
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=config.access_key_id,
            aws_secret_access_key=config.secret_access_key,
            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            region_name="us-east-1",
        )

    def ensure_buckets(self) -> None:
        existing = {item["Name"] for item in self.client.list_buckets().get("Buckets", [])}
        for bucket in (self.config.uploads_bucket, self.config.outputs_bucket):
            if bucket not in existing:
                self.client.create_bucket(Bucket=bucket)

    def create_upload_url(self, storage_key: str, content_type: str) -> str:
        self.ensure_buckets()
        public_storage = StorageService(self.config, public_urls=True)
        return public_storage.client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": self.config.uploads_bucket,
                "Key": storage_key,
                "ContentType": content_type,
            },
            ExpiresIn=self.config.signed_url_ttl_seconds,
        )

    def head_upload(self, storage_key: str) -> dict:
        return self.client.head_object(Bucket=self.config.uploads_bucket, Key=storage_key)

    def get_upload_bytes(self, storage_key: str) -> bytes:
        response = self.client.get_object(Bucket=self.config.uploads_bucket, Key=storage_key)
        return response["Body"].read()

    def put_markdown(self, storage_key: str, markdown: str) -> None:
        self.client.put_object(
            Bucket=self.config.outputs_bucket,
            Key=storage_key,
            Body=markdown.encode("utf-8"),
            ContentType="text/markdown; charset=utf-8",
        )

    def create_download_url(self, storage_key: str) -> tuple[str, timedelta]:
        public_storage = StorageService(self.config, public_urls=True)
        url = public_storage.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": self.config.outputs_bucket, "Key": storage_key},
            ExpiresIn=self.config.signed_url_ttl_seconds,
        )
        return url, timedelta(seconds=self.config.signed_url_ttl_seconds)

