import uuid
from abc import ABC, abstractmethod


class ImageKeyFactory(ABC):
    @abstractmethod
    def create_key(self, image_name: str) -> str:
        pass


class UniqueImageKeyFactory(ImageKeyFactory):
    def create_key(self, image_name: str) -> str:
        return f"{uuid.uuid4()}-{image_name}"
