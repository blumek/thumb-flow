import uuid

from dev_blumek_thumbnail_generator.infrastructure.factory.metadata_identifier_factory import (
    MetadataIdentifierFactory,
)


class UniqueMetadataIdentifierFactory(MetadataIdentifierFactory):
    def create_identifier(self) -> str:
        return str(uuid.uuid4())
