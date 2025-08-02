from abc import ABC, abstractmethod


class SeedGenerator(ABC):
    @abstractmethod
    def generate(self) -> int:
        pass
