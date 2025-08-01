import os
from typing import Optional

import boto3
from mypy_boto3_s3.client import S3Client
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

from dev_blumek_thumbnail_generator.application.use_case.generate_thumbail_use_case import (
    GenerateThumbnailUseCase,
)
from dev_blumek_thumbnail_generator.application.use_case.generate_thumbnail_service import (
    GenerateThumbnailService,
)
from dev_blumek_thumbnail_generator.infrastructure.factory.image_key_factory import (
    ImageKeyFactory,
)
from dev_blumek_thumbnail_generator.infrastructure.factory.unique_image_key_factory import (
    UniqueImageKeyFactory,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.image_persistence_gateway import (
    ImagePersistenceGateway,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.image_query_gateway import (
    ImageQueryGateway,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.s3_image_persistence_gateway import (
    S3ImagePersistenceGateway,
)
from dev_blumek_thumbnail_generator.infrastructure.gateway.s3_image_query_gateway import (
    S3ImageQueryGateway,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.bedrock_thumbnail_generator import (
    BedrockThumbnailGenerator,
    BedrockConfiguration,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.random_seed_generator import (
    RandomSeedGenerator,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.seed_generator import (
    SeedGenerator,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.thumbnail_generator import (
    ThumbnailGenerator,
)
from dev_blumek_thumbnail_generator.infrastructure.repository.image_repository import (
    ImageRepository,
)
from dev_blumek_thumbnail_generator.infrastructure.repository.s3_image_repository import (
    S3ImageRepository,
)


def generate_thumbnail_use_case() -> GenerateThumbnailUseCase:
    return GenerateThumbnailService(
        image_query_gateway=image_query_gateway(
            image_repository=s3_image_repository(
                s3_client=s3_client(), bucket_name=raw_bucket_name()
            )
        ),
        image_persistence_gateway=image_persistence_gateway(
            image_repository=s3_image_repository(
                s3_client=s3_client(), bucket_name=thumbnail_bucket_name()
            ),
            key_factory=key_factory(),
        ),
        thumbnail_generator=thumbnail_generator(
            bedrock_client=bedrock_client(aws_region=aws_region()),
            configuration=bedrock_configuration(),
            seed_generator=seed_generator(),
        ),
    )


def image_query_gateway(image_repository: ImageRepository) -> ImageQueryGateway:
    return S3ImageQueryGateway(image_repository=image_repository)


def s3_image_repository(s3_client: S3Client, bucket_name: str) -> ImageRepository:
    return S3ImageRepository(s3_client, bucket_name)


def s3_client() -> S3Client:
    return boto3.client("s3")


def raw_bucket_name() -> str:
    return load_variable("AWS_S3_RAW_BUCKET_NAME")


def image_persistence_gateway(
    image_repository: ImageRepository, key_factory: ImageKeyFactory
) -> ImagePersistenceGateway:
    return S3ImagePersistenceGateway(
        image_repository=image_repository,
        image_key_factory=key_factory,
    )


def thumbnail_bucket_name() -> str:
    return load_variable("AWS_S3_THUMBNAIL_BUCKET_NAME")


def key_factory() -> ImageKeyFactory:
    return UniqueImageKeyFactory()


def thumbnail_generator(
    bedrock_client: BedrockRuntimeClient,
    configuration: BedrockConfiguration,
    seed_generator: SeedGenerator,
) -> ThumbnailGenerator:
    return BedrockThumbnailGenerator(
        bedrock_client=bedrock_client,
        configuration=configuration,
        seed_generator=seed_generator,
    )


def bedrock_client(aws_region: str) -> BedrockRuntimeClient:
    return boto3.client("bedrock-runtime", region_name=aws_region)


def aws_region() -> str:
    return load_variable("AWS_REGION", "eu-central-1")


def bedrock_configuration() -> BedrockConfiguration:
    return BedrockConfiguration(
        model_id=load_variable(
            "AWS_BEDROCK_MODEL_ID", "stability.stable-diffusion-xl-v1"
        ),
        image_strength=float(load_variable("AWS_BEDROCK_IMAGE_STRENGTH", "0.8")),
        cfg_scale=int(load_variable("AWS_BEDROCK_CFG_SCALE", "7")),
        steps=int(load_variable("AWS_BEDROCK_STEPS", "40")),
    )


def seed_generator() -> SeedGenerator:
    return RandomSeedGenerator()


def load_variable(variable_name: str, default_value: Optional[str] = None) -> str:
    value = os.getenv(variable_name, default_value)
    if value is None:
        raise ValueError(f"Environment variable '{variable_name}' is not set.")
    return value
