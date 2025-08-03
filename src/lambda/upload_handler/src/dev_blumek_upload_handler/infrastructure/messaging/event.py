from abc import ABC, abstractmethod


class Event(ABC):
    @abstractmethod
    def queue(self) -> str:
        pass

    @abstractmethod
    def content(self) -> dict[str, str]:
        pass
