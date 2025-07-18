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
from dev_blumek_upload_handler.infrastructure.policy.composite_image_policy import (
    CompositeImagePolicy,
)
from dev_blumek_upload_handler.infrastructure.policy.extension_image_policy import (
    ExtensionImagePolicy,
)
from dev_blumek_upload_handler.application.use_case.image_upload_use_case import (
    UploadImageUseCase,
)
from dev_blumek_upload_handler.application.use_case.image_upload_service import (
    UploadImageService,
)
import boto3

from dev_blumek_upload_handler.infrastructure.policy.image_policy import ImagePolicy
from dev_blumek_upload_handler.infrastructure.policy.size_image_policy import (
    SizeImagePolicy,
)
from dev_blumek_upload_handler.infrastructure.repository.image_repository import (
    ImageRepository,
)
from dev_blumek_upload_handler.infrastructure.repository.in_memory_image_repository import (
    InMemoryImageRepository,
)
from dev_blumek_upload_handler.infrastructure.repository.s3_image_repository import (
    S3ImageRepository,
)


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
