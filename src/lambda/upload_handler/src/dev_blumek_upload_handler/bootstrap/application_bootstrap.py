import os
from typing import Optional

import boto3

from mypy_boto3_s3.client import S3Client
from mypy_boto3_sqs.client import SQSClient

from dev_blumek_upload_handler.application.use_case.initialize_thumbnail_generation_service import (
    InitializeThumbnailGenerationService,
)
from dev_blumek_upload_handler.application.use_case.initialize_thumbnail_generation_use_case import (
    InitializeThumbnailGenerationUseCase,
)
from dev_blumek_upload_handler.domain.types.image_extension import ImageExtension
from dev_blumek_upload_handler.infrastructure.factory.image_key_factory import (
    ImageKeyFactory,
)
from dev_blumek_upload_handler.infrastructure.factory.unique_image_key_factory import (
    UniqueImageKeyFactory,
)
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway import (
    ImagePersistenceGateway,
)
from dev_blumek_upload_handler.infrastructure.gateway.s3_image_persistence_gateway import (
    S3ImagePersistenceGateway,
)
from dev_blumek_upload_handler.infrastructure.messaging.event_publisher import (
    EventPublisher,
)
from dev_blumek_upload_handler.infrastructure.messaging.sqs_event_publisher import (
    SQSEventPublisher,
)
from dev_blumek_upload_handler.infrastructure.policy.composite_image_policy import (
    CompositeImagePolicy,
)
from dev_blumek_upload_handler.infrastructure.policy.extension_image_policy import (
    ExtensionImagePolicy,
)
from dev_blumek_upload_handler.infrastructure.policy.image_policy import ImagePolicy
from dev_blumek_upload_handler.infrastructure.policy.size_image_policy import (
    SizeImagePolicy,
)
from dev_blumek_upload_handler.infrastructure.repository.image_repository import (
    ImageRepository,
)
from dev_blumek_upload_handler.infrastructure.repository.s3_image_repository import (
    S3ImageRepository,
)


def initialize_thumbnail_generation_use_case() -> InitializeThumbnailGenerationUseCase:
    return InitializeThumbnailGenerationService(
        image_persistence_gateway=image_persistence_gateway(
            image_repository=s3_image_repository(
                s3_client=s3_client(), bucket_name=bucket_name()
            ),
            image_policy=image_policy(),
            key_factory=key_factory(),
        ),
        event_publisher=given_event_publisher(
            sqs_client=sqs_client(
                queue_url=load_variable("AWS_SQS_QUEUE_URL"),
                aws_region=load_variable("AWS_REGION", default_value="us-east-1"),
            )
        ),
    )


def image_persistence_gateway(
    image_repository: ImageRepository,
    image_policy: ImagePolicy,
    key_factory: ImageKeyFactory,
) -> ImagePersistenceGateway:
    return S3ImagePersistenceGateway(
        image_repository=image_repository,
        image_policy=image_policy,
        image_key_factory=key_factory,
    )


def s3_image_repository(s3_client: S3Client, bucket_name: str) -> ImageRepository:
    return S3ImageRepository(s3_client, bucket_name)


def s3_client() -> S3Client:
    return boto3.client("s3")


def bucket_name() -> str:
    return load_variable("AWS_S3_BUCKET_NAME")


def image_policy() -> ImagePolicy:
    max_size_policy = SizeImagePolicy(max_bytes_size=5 * 1024 * 1024)  # 5 MB
    extension_policy = ExtensionImagePolicy(
        allowed_extensions={ImageExtension.PNG, ImageExtension.JPG, ImageExtension.JPEG}
    )
    return CompositeImagePolicy(max_size_policy, extension_policy)


def key_factory() -> ImageKeyFactory:
    return UniqueImageKeyFactory()


def given_event_publisher(sqs_client: SQSClient) -> EventPublisher:
    return SQSEventPublisher(sqs_client)


def sqs_client(queue_url: str, aws_region: str) -> SQSClient:
    return boto3.client("sqs", region_name=aws_region, endpoint_url=queue_url)


def load_variable(variable_name: str, default_value: Optional[str] = None) -> str:
    value = os.getenv(variable_name, default_value)
    if value is None:
        raise ValueError(f"Environment variable '{variable_name}' is not set.")
    return value
