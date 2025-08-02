import base64
import json
import logging
from typing import Any, Dict, Optional

from botocore.response import StreamingBody
from mypy_boto3_bedrock_runtime import BedrockRuntimeClient
from mypy_boto3_bedrock_runtime.type_defs import InvokeModelResponseTypeDef

from dev_blumek_thumbnail_generator.infrastructure.generator.becrock_configuration import (
    BedrockConfiguration,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.seed_generator import (
    SeedGenerator,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.thumbnail_generator import (
    ThumbnailGenerator,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.thumbnail_generator_model import (
    GenerateThumbnailRequest,
    GenerateThumbnailReply,
)

logger = logging.getLogger(__name__)


class BedrockThumbnailGenerator(ThumbnailGenerator):
    def __init__(
        self,
        bedrock_client: BedrockRuntimeClient,
        configuration: BedrockConfiguration,
        seed_generator: SeedGenerator,
    ) -> None:
        self._bedrock_client = bedrock_client
        self._config = configuration
        self._seed_generator = seed_generator

    def generate_thumbnail(
        self, request: GenerateThumbnailRequest
    ) -> GenerateThumbnailReply:
        try:
            model_request: Dict[str, Any] = self.__build_model_request(request)
            response: InvokeModelResponseTypeDef = self.__invoke_bedrock_model(
                model_request
            )
            thumbnail_bytes: bytes = self.__extract_thumbnail_bytes(response)
            return GenerateThumbnailReply(thumbnail_bytes=thumbnail_bytes)
        except BedrockThumbnailGenerationError:
            raise
        except Exception as exception:
            logger.error(
                "Error occurred during thumbnail generation", exc_info=exception
            )
            raise BedrockThumbnailGenerationError(
                f"Unexpected error during thumbnail generation: {exception}"
            ) from exception

    def __build_model_request(
        self, request: GenerateThumbnailRequest
    ) -> Dict[str, Any]:
        seed: int = (
            request.seed
            if request.seed is not None
            else self._seed_generator.generate()
        )

        base64_image = base64.b64encode(request.input_image_bytes).decode("utf-8")

        return {
            "mode": "image-to-image",
            "text_prompts": [{"text": request.prompt, "weight": 1.0}],
            "init_image": base64_image,
            "init_image_mode": "IMAGE_STRENGTH",
            "image_strength": self._config.image_strength,
            "steps": self._config.steps,
            "cfg_scale": self._config.cfg_scale,
            "seed": seed,
        }

    def __invoke_bedrock_model(
        self, model_request: Dict[str, Any]
    ) -> InvokeModelResponseTypeDef:
        try:
            return self._bedrock_client.invoke_model(
                modelId=self._config.model_id,
                body=json.dumps(model_request),
                contentType="application/json",
                accept="application/json",
            )
        except Exception as e:
            raise BedrockThumbnailGenerationError(
                f"Failed to invoke Bedrock model {self._config.model_id}: {e}"
            ) from e

    def __extract_thumbnail_bytes(self, response: InvokeModelResponseTypeDef) -> bytes:
        body: Optional[StreamingBody] = response.get("body")
        if not body:
            raise BedrockThumbnailGenerationError(
                "Invalid Bedrock response: No response body received"
            )

        return self.__read_and_parse(body)

    def __read_and_parse(self, body: StreamingBody) -> bytes:
        try:
            body_str = self.__read(body).decode("utf-8")
            response_data = json.loads(body_str)

            if self.__is_content_available(response_data):
                base64_image = self.__get_image_base64(response_data)
                return base64.b64decode(base64_image)

            logger.error(f"Unexpected response format: {response_data}")
            raise BedrockThumbnailGenerationError(
                "Invalid response format from Bedrock model"
            )
        except json.JSONDecodeError as exception:
            logger.error(f"Failed to parse Bedrock response: {exception}")
            raise BedrockThumbnailGenerationError(
                f"Failed to parse Bedrock response: {exception}"
            ) from exception

    @staticmethod
    def __is_content_available(response_data: Dict[str, Any]) -> bool:
        return "artifacts" in response_data and len(response_data["artifacts"]) > 0

    @staticmethod
    def __get_image_base64(response_data: Dict[str, Any]) -> str:
        base64_value: str = response_data["artifacts"][0].get("base64")
        if base64_value is None:
            raise BedrockThumbnailGenerationError(
                "Missing base64 data in Bedrock response"
            )
        return base64_value

    @staticmethod
    def __read(body: StreamingBody) -> bytes:
        try:
            return body.read()
        except Exception as e:
            raise BedrockThumbnailGenerationError(f"Failed to read body: {e}") from e


class BedrockThumbnailGenerationError(Exception):
    pass
