import os
from typing import Optional

import boto3

from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table
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
from dev_blumek_upload_handler.infrastructure.factory.metadata_identifier_factory import (
    MetadataIdentifierFactory,
)
from dev_blumek_upload_handler.infrastructure.factory.thumbnail_generation_identifier_factory import (
    WorkflowIdentifierFactory,
)
from dev_blumek_upload_handler.infrastructure.factory.unique_image_key_factory import (
    UniqueImageKeyFactory,
)
from dev_blumek_upload_handler.infrastructure.factory.unique_metadata_identifier_factory import (
    UniqueMetadataIdentifierFactory,
)
from dev_blumek_upload_handler.infrastructure.factory.unique_workflow_identifier_factory import (
    UniqueWorkflowIdentifierFactory,
)
from dev_blumek_upload_handler.infrastructure.gateway.dynamodb_metadata_persistence_gateway import (
    DynamoDBMetadataPersistenceGateway,
)
from dev_blumek_upload_handler.infrastructure.gateway.image_persistence_gateway import (
    ImagePersistenceGateway,
)
from dev_blumek_upload_handler.infrastructure.gateway.metadata_persistence_gateway import (
    MetadataPersistenceGateway,
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
from dev_blumek_upload_handler.infrastructure.repository.dynamodb_metadata_repository import (
    DynamoDBMetadataRepository,
)
from dev_blumek_upload_handler.infrastructure.repository.image_repository import (
    ImageRepository,
)
from dev_blumek_upload_handler.infrastructure.repository.metadata_repository import (
    MetadataRepository,
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
        metadata_persistence_gateway=metadata_persistence_gateway(
            metadata_repository=dynamodb_metadata_repository(
                dynamodb_table=dynamodb_table(
                    aws_region=aws_region(), table_name=table_name()
                ),
                metadata_identifier_factory=metadata_identifier_factory(),
            ),
        ),
        event_publisher=given_event_publisher(
            sqs_client=sqs_client(aws_region=aws_region()), queue_url=queue_url()
        ),
        workflow_identifier_factory=given_workflow_identifier_factory(),
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


def given_event_publisher(sqs_client: SQSClient, queue_url: str) -> EventPublisher:
    return SQSEventPublisher(sqs_client, queue_url)


def sqs_client(aws_region: str) -> SQSClient:
    return boto3.client("sqs", region_name=aws_region)


def aws_region() -> str:
    return load_variable("AWS_REGION", default_value="us-east-1")


def queue_url() -> str:
    return load_variable("AWS_SQS_QUEUE_URL")


def metadata_persistence_gateway(
    metadata_repository: MetadataRepository,
) -> MetadataPersistenceGateway:
    return DynamoDBMetadataPersistenceGateway(metadata_repository=metadata_repository)


def dynamodb_metadata_repository(
    dynamodb_table: Table, metadata_identifier_factory: MetadataIdentifierFactory
) -> MetadataRepository:
    return DynamoDBMetadataRepository(dynamodb_table, metadata_identifier_factory)


def dynamodb_table(aws_region: str, table_name: str) -> Table:
    dynamodb = dynamodb_resource(aws_region=aws_region)
    return dynamodb.Table(table_name)


def dynamodb_resource(aws_region: str) -> DynamoDBServiceResource:
    return boto3.resource("dynamodb", region_name=aws_region)


def table_name() -> str:
    return load_variable("AWS_DYNAMODB_TABLE_NAME")


def metadata_identifier_factory() -> MetadataIdentifierFactory:
    return UniqueMetadataIdentifierFactory()


def given_workflow_identifier_factory() -> WorkflowIdentifierFactory:
    return UniqueWorkflowIdentifierFactory()


def load_variable(variable_name: str, default_value: Optional[str] = None) -> str:
    value = os.getenv(variable_name, default_value)
    if value is None:
        raise ValueError(f"Environment variable '{variable_name}' is not set.")
    return value
