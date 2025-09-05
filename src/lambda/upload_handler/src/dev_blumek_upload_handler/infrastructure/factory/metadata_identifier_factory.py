from abc import ABC, abstractmethod


class MetadataIdentifierFactory(ABC):
    @abstractmethod
    def create_identifier(self) -> str:
        pass
