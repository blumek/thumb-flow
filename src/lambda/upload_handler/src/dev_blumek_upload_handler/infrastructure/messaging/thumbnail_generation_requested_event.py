from dev_blumek_upload_handler.infrastructure.messaging.event import Event
from typing import Any


class ThumbnailGenerationRequestedEvent(Event):
    def __init__(self, workflow_id: str, uploaded_image_key: str, prompt: str):
        self.workflow_id = workflow_id
        self._uploaded_image_key: str = uploaded_image_key
        self._prompt: str = prompt

    def content(self) -> dict[str, str]:
        return {
            "workflow_id": self.workflow_id,
            "uploaded_image_key": self._uploaded_image_key,
            "prompt": self._prompt,
        }

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ThumbnailGenerationRequestedEvent):
            return False
        return (
            self.workflow_id == other.workflow_id
            and self._uploaded_image_key == other._uploaded_image_key
            and self._prompt == other._prompt
        )

    def __hash__(self) -> int:
        return hash((self.workflow_id, self._uploaded_image_key, self._prompt))
