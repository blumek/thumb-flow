import json
import logging
from typing import Dict, Any

from aws_lambda_typing.context import Context as LambdaContext

from dev_blumek_thumbnail_generator.application.use_case.generate_thumbail_use_case_model import (
    GenerateThumbnailUseCaseRequest,
    GenerateThumbnailUseCaseReply,
)
from dev_blumek_thumbnail_generator.bootstrap.application_bootstrap import (
    generate_thumbnail_use_case,
)

generate_thumbnail = generate_thumbnail_use_case()
logger = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    try:
        if "Records" not in event:
            logger.error("Event does not contain Records")
            return {"statusCode": 400, "body": "Invalid SQS event format"}

        responses = []
        for record in event["Records"]:
            generate_thumbnail_request: GenerateThumbnailUseCaseRequest = (
                __to_generate_thumbnail_request(record)
            )
            generate_thumbnail_reply: GenerateThumbnailUseCaseReply = (
                generate_thumbnail.generate_thumbnail(generate_thumbnail_request)
            )
            responses.append(
                {
                    "statusCode": 200,
                    "image_key": generate_thumbnail_reply.thumbnail_key,
                }
            )

        return {"statusCode": 200, "body": json.dumps({"responses": responses})}
    except KeyError as e:
        logger.error(f"Missing required field in event: {e}")
        return {"statusCode": 400, "body": f"Missing required field: {e}"}
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {"statusCode": 500, "body": f"Internal server error: {e}"}


def __to_generate_thumbnail_request(
    record: Dict[str, Any],
) -> GenerateThumbnailUseCaseRequest:
    try:
        if "body" in record:
            message_body = json.loads(record["body"])
        else:
            message_body = record

        required_fields: list[str] = ["uploaded_image_key", "prompt"]
        for field in required_fields:
            if field not in message_body:
                raise KeyError(field)

        return GenerateThumbnailUseCaseRequest(
            image_key=message_body["uploaded_image_key"],
            prompt=message_body["prompt"],
        )
    except json.JSONDecodeError:
        logger.error("Failed to parse SQS message body as JSON")
        raise ValueError("Invalid JSON in SQS message body")
