from infrastructure.factory.key_factory import ImageKeyFactory, UniqueImageKeyFactory
from infrastructure.repository.image_repository import ImageRepository, S3ImageRepository, InMemoryImageRepository
from infrastructure.gateway.image_persistence_gateway import ImagePersistenceGateway, S3ImagePersistenceGateway
from infrastructure.policy.image_policy import ImagePolicy, ImagePolicyComposite, ImagePolicySize, ImagePolicyExtension
from application.use_case.image_upload_use_case import UploadImageUseCase, UploadImageService
import boto3


def upload_image_use_case() -> UploadImageUseCase:
    return UploadImageService(
        image_persistence_gateway(
            image_repository = in_memory_image_repository(),
            image_policy = image_policy(),
            key_factory = key_factory()
        )
    )


def image_persistence_gateway(
        image_repository: ImageRepository,
        image_policy: ImagePolicy,
        key_factory: ImageKeyFactory
) -> ImagePersistenceGateway:
    return S3ImagePersistenceGateway(
        image_repository=image_repository,
        image_policy=image_policy,
        image_key_factory=key_factory
    )


def in_memory_image_repository() -> ImageRepository:
    return InMemoryImageRepository()


def image_repository(s3_client: boto3.client, bucket_name: str) -> ImageRepository:
    return S3ImageRepository(s3_client, bucket_name)


def s3_client() -> boto3.client:
    return boto3.client('s3')


def bucket_name() -> str:
    return "your-s3-bucket-name"


def image_policy() -> ImagePolicy:
    max_size_policy = ImagePolicySize(max_bytes_size=5 * 1024 * 1024)  # 5 MB
    extension_policy = ImagePolicyExtension(allowed_extensions={'jpg', 'jpeg', 'png'})
    return ImagePolicyComposite(max_size_policy, extension_policy)


def key_factory() -> ImageKeyFactory:
    return UniqueImageKeyFactory()
