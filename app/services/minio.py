from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, BinaryIO
from uuid import uuid4

import boto3
from botocore.config import Config
from app.services.base import BaseService


@dataclass
class MinioStorageService(BaseService):
    endpoint: str
    bucket: str
    access_key_id: str
    secret_access_key: str
    region: str = "us-east-1"
    force_path_style: bool = True
    presign_expires: int = 900

    def __post_init__(self) -> None:
        s3_config = Config(
            region_name=self.region,
            signature_version="s3v4",
            s3={"addressing_style": "path" if self.force_path_style else "virtual"},
            retries={"max_attempts": 5, "mode": "standard"},
        )

        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            config=s3_config,
        )

    async def start(self) -> None:
        return

    async def stop(self) -> None:
        return

    def put_object(self, key: str, body, content_type: Optional[str] = None) -> None:
        extra = {}
        if content_type:
            extra["ContentType"] = content_type
        self.client.put_object(Bucket=self.bucket, Key=key, Body=body, **extra)

    def upload_fileobj(self, key: str, fileobj: BinaryIO, content_type: Optional[str] = None) -> None:
        extra = {}
        if content_type:
            extra["ExtraArgs"] = {"ContentType": content_type}
        self.client.upload_fileobj(fileobj, self.bucket, key, **extra)

    def get_object_stream(self, key: str):
        resp = self.client.get_object(Bucket=self.bucket, Key=key)
        return resp["Body"], resp.get("ContentType"), resp.get("ContentLength")

    def delete_object(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def presign_get(self, key: str, expires_in: Optional[int] = None) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in or self.presign_expires,
        )

    def presign_put(self, key: str, content_type: Optional[str] = None, expires_in: Optional[int] = None) -> str:
        params = {"Bucket": self.bucket, "Key": key}
        if content_type:
            params["ContentType"] = content_type
        return self.client.generate_presigned_url(
            "put_object",
            Params=params,
            ExpiresIn=expires_in or self.presign_expires,
        )