from abc import ABC, abstractmethod


class WorkflowIdentifierFactory(ABC):
    @abstractmethod
    def create_identifier(self) -> str:
        pass
