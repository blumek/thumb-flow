import json
from typing import Mapping

from mypy_boto3_sqs import SQSClient
from mypy_boto3_sqs.type_defs import (
    SendMessageResultTypeDef,
    MessageAttributeValueTypeDef,
)
from mypy_boto3_sqs.type_defs import GetQueueUrlResultTypeDef

from dev_blumek_upload_handler.infrastructure.messaging.event import Event
from dev_blumek_upload_handler.infrastructure.messaging.event_publisher import (
    EventPublisher,
)


class SQSEventPublisher(EventPublisher):
    def __init__(self, sqs_client: SQSClient):
        self.sqs_client = sqs_client

    def publish(self, event: Event) -> None:
        response: SendMessageResultTypeDef = self.sqs_client.send_message(
            QueueUrl=self.__to_queue_url(event),
            MessageBody=json.dumps(event.content()),
            MessageAttributes=self.to_message_attributes(event),
        )

        if not self.is_successful(response):
            raise SQSEventPublishingError(
                f"Failed to publish event to SQS queue {event.queue()}: {response}"
            )

    def __to_queue_url(self, event: Event) -> str:
        queue_url_result: GetQueueUrlResultTypeDef = self.sqs_client.get_queue_url(
            QueueName=event.queue()
        )
        return queue_url_result["QueueUrl"]

    @staticmethod
    def to_message_attributes(
        event: Event,
    ) -> Mapping[str, MessageAttributeValueTypeDef]:
        event_type_attribute: MessageAttributeValueTypeDef = {
            "DataType": "String",
            "StringValue": event.__class__.__name__,
        }
        return {"event_type": event_type_attribute}

    @staticmethod
    def is_successful(response: SendMessageResultTypeDef) -> bool:
        return (
            response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 200
            and "MessageId" in response
        )


class SQSEventPublishingError(Exception):
    pass
