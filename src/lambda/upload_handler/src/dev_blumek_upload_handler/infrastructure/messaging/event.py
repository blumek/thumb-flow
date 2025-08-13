from abc import ABC, abstractmethod


class Event(ABC):
    @abstractmethod
    def content(self) -> dict[str, str]:
        pass
