import uuid

from dev_blumek_upload_handler.infrastructure.factory.image_key_factory import ImageKeyFactory


class UniqueImageKeyFactory(ImageKeyFactory):
    def create_key(self, image_name: str) -> str:
        return f"{uuid.uuid4()}-{image_name}"
