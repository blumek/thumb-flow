import logging
from pathlib import Path

from mypy_boto3_s3.client import S3Client
from mypy_boto3_s3.type_defs import GetObjectOutputTypeDef

from dev_blumek_thumbnail_generator.domain.types.image_extension import ImageExtension
from dev_blumek_thumbnail_generator.infrastructure.repository.image_repository import (
    ImageRepository,
)
from dev_blumek_thumbnail_generator.infrastructure.repository.image_repository_model import (
    StoreImageRequest,
    StoreImageReply,
    RetrieveImageRequest,
    RetrieveImageReply,
)

logger = logging.getLogger(__name__)


class S3ImageRepository(ImageRepository):
    def __init__(self, s3_client: S3Client, bucket_name: str):
        self.s3_client: S3Client = s3_client
        self.bucket_name: str = bucket_name

    def retrieve(self, request: RetrieveImageRequest) -> RetrieveImageReply:
        try:
            response: GetObjectOutputTypeDef = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=request.image_key,
            )

            return RetrieveImageReply(
                image_name=self.__image_name(request),
                image_extension=self.__content_type(response),
                image_bytes=self.__read_image_bytes(response),
            )
        except self.s3_client.exceptions.NoSuchKey:
            raise S3RetrieveError(f"Image under key: {request.image_key} not found")
        except Exception as exception:
            logger.error("Error occurred while retrieving image", exc_info=exception)
            raise S3RetrieveError(
                f"Failed to retrieve image: {request.image_key}"
            ) from exception

    @staticmethod
    def __read_image_bytes(response: GetObjectOutputTypeDef) -> bytes:
        try:
            body = response["Body"]
            data = body.read()
            body.close()
            return data
        except Exception as exception:
            logger.error("An error occurred while reading image", exc_info=exception)
            raise S3RetrieveError("Failed to read image data") from exception

    @staticmethod
    def __content_type(response: GetObjectOutputTypeDef) -> ImageExtension:
        if "ContentType" not in response:
            raise S3RetrieveError("ContentType not found in S3 response")
        return ImageExtension.from_mime_type(response["ContentType"])

    @staticmethod
    def __image_name(request: RetrieveImageRequest) -> str:
        return Path(request.image_key).name

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


class S3RetrieveError(Exception):
    pass
