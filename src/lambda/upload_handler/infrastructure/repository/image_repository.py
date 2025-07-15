import logging
from abc import ABC, abstractmethod

import boto3

from infrastructure.repository.image_repository_model import StoreImageRequest, StoreImageReply

logger = logging.getLogger(__name__)


class ImageRepository(ABC):
    @abstractmethod
    def store(self, request: StoreImageRequest) -> StoreImageReply:
        pass


class S3UploadError(Exception):
    pass


class S3ImageRepository(ImageRepository):
    def __init__(self, s3_client: boto3.client, bucket_name: str):
        self.s3_client: boto3.client = s3_client
        self.bucket_name: str = bucket_name

    def store(self, request: StoreImageRequest) -> StoreImageReply:
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=request.image_key,
                Body=request.image_bytes,
                ContentType=f"image/{request.image_extension.value.lower()}",
            )
            return StoreImageReply(image_key=request.image_key)
        except Exception as exception:
            logger.error(f"Error occurred while storing image: {exception}")
            raise S3UploadError(f"Failed to store image: {request.image_key}") from exception


class InMemoryImageRepository(ImageRepository):
    def __init__(self):
        self.storage: dict[str, bytes] = {}

    def store(self, request: StoreImageRequest) -> StoreImageReply:
        self.storage[request.image_key] = request.image_bytes
        return StoreImageReply(image_key=request.image_key)
