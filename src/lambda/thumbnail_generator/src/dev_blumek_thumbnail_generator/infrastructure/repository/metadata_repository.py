from abc import ABC, abstractmethod

from dev_blumek_thumbnail_generator.infrastructure.repository.metadata_repository_model import (
    StoreMetadataRequest,
    StoreMetadataReply,
)


class MetadataRepository(ABC):
    @abstractmethod
    def store(self, store_metadata_request: StoreMetadataRequest) -> StoreMetadataReply:
        pass
