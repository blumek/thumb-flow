from domain.types.image_extension import ImageExtension
from infrastructure.factory.key_factory import ImageKeyFactory, UniqueImageKeyFactory
from infrastructure.policy.composite_image_policy import CompositeImagePolicy
from infrastructure.policy.extension_image_policy import ExtensionImagePolicy
from infrastructure.policy.size_image_policy import SizeImagePolicy
from infrastructure.repository.image_repository import (
    ImageRepository,
    S3ImageRepository,
    InMemoryImageRepository,
)
from infrastructure.gateway.image_persistence_gateway import (
    ImagePersistenceGateway,
    S3ImagePersistenceGateway,
)
from infrastructure.policy.image_policy import ImagePolicy
from application.use_case.image_upload_use_case import UploadImageUseCase
from application.use_case.image_upload_service import UploadImageService
import boto3


def upload_image_use_case() -> UploadImageUseCase:
    return UploadImageService(
        image_persistence_gateway(
            image_repository=in_memory_image_repository(),
            image_policy=image_policy(),
            key_factory=key_factory(),
        )
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


def in_memory_image_repository() -> ImageRepository:
    return InMemoryImageRepository()


def image_repository(s3_client: boto3.client, bucket_name: str) -> ImageRepository:
    return S3ImageRepository(s3_client, bucket_name)


def s3_client() -> boto3.client:
    return boto3.client("s3")


def bucket_name() -> str:
    return "your-s3-bucket-name"


def image_policy() -> ImagePolicy:
    max_size_policy = SizeImagePolicy(max_bytes_size=5 * 1024 * 1024)  # 5 MB
    extension_policy = ExtensionImagePolicy(
        allowed_extensions={ImageExtension.PNG, ImageExtension.JPG, ImageExtension.JPEG}
    )
    return CompositeImagePolicy(max_size_policy, extension_policy)


def key_factory() -> ImageKeyFactory:
    return UniqueImageKeyFactory()
