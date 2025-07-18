import logging

import boto3

from dev_blumek_upload_handler.infrastructure.repository.image_repository import (
    ImageRepository,
)
from dev_blumek_upload_handler.infrastructure.repository.image_repository_model import (
    StoreImageRequest,
    StoreImageReply,
)

logger = logging.getLogger(__name__)


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
                ContentType=request.image_extension.mime_type,
            )
            return StoreImageReply(image_key=request.image_key)
        except Exception as exception:
            logger.error(f"Error occurred while storing image: {exception}")
            raise S3UploadError(
                f"Failed to store image: {request.image_key}"
            ) from exception


class S3UploadError(Exception):
    pass
