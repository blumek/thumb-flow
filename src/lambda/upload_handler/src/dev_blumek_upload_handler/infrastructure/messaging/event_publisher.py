from abc import ABC

from dev_blumek_upload_handler.infrastructure.messaging.event import Event


class EventPublisher(ABC):
    def publish(self, event: Event) -> None:
        pass
