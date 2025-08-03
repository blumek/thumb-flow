from abc import ABC


class Event(ABC):
    def queue(self) -> str:
        pass

    def content(self) -> dict[str, str]:
        pass
