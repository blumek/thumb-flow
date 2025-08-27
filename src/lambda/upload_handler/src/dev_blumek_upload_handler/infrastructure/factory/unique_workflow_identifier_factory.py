import uuid

from dev_blumek_upload_handler.infrastructure.factory.thumbnail_generation_identifier_factory import (
    WorkflowIdentifierFactory,
)


class UniqueWorkflowIdentifierFactory(WorkflowIdentifierFactory):
    def create_identifier(self) -> str:
        return str(uuid.uuid4())
