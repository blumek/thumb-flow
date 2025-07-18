from abc import ABC, abstractmethod


class ImageKeyFactory(ABC):
    @abstractmethod
    def create_key(self, image_name: str) -> str:
        pass
