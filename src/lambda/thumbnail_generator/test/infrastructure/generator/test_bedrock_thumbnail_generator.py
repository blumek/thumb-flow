import unittest
import json
import base64
from typing import Any, Dict
from unittest.mock import Mock, MagicMock

from mypy_boto3_bedrock_runtime import BedrockRuntimeClient

from dev_blumek_thumbnail_generator.infrastructure.generator.bedrock_thumbnail_generator import (
    BedrockThumbnailGenerator,
    BedrockConfiguration,
    BedrockThumbnailGenerationError,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.seed_generator import (
    SeedGenerator,
)
from dev_blumek_thumbnail_generator.infrastructure.generator.thumbnail_generator_model import (
    GenerateThumbnailRequest,
    GenerateThumbnailReply,
)


class TestBedrockThumbnailGenerator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bedrock_client: BedrockRuntimeClient = Mock()
        self.configuration: BedrockConfiguration = BedrockConfiguration(
            model_id="givenModel",
            image_strength=0.5,
            cfg_scale=10,
            steps=50,
        )
        self.seed_generator: SeedGenerator = Mock()
        self.thumbnail_generator: BedrockThumbnailGenerator = BedrockThumbnailGenerator(
            bedrock_client=self.bedrock_client,
            configuration=self.configuration,
            seed_generator=self.seed_generator,
        )

    def test_should_generate_thumbnail_successfully(self) -> None:
        self.given_seed_generator_returns_seed()
        self.given_bedrock_invoke_model_succeeds()
        given_request: GenerateThumbnailRequest = (
            self.given_generate_thumbnail_request()
        )

        actual_result: GenerateThumbnailReply = (
            self.thumbnail_generator.generate_thumbnail(given_request)
        )

        self.assertEqual(actual_result, self.given_expected_generate_thumbnail_reply())

    def given_seed_generator_returns_seed(self) -> None:
        self.seed_generator.generate.return_value = 12345

    def given_bedrock_invoke_model_succeeds(self) -> None:
        mock_body: MagicMock = MagicMock()
        mock_body.read.return_value = self.given_response_body()
        self.bedrock_client.invoke_model.return_value = {"body": mock_body}

    @staticmethod
    def given_response_body() -> bytes:
        return json.dumps(
            {
                "artifacts": [
                    {"base64": base64.b64encode(b"generated_thumbnail").decode("utf-8")}
                ]
            }
        ).encode("utf-8")

    @staticmethod
    def given_generate_thumbnail_request() -> GenerateThumbnailRequest:
        return GenerateThumbnailRequest(
            input_image_bytes=b"input_image_bytes", prompt="given prompt"
        )

    @staticmethod
    def given_expected_generate_thumbnail_reply() -> GenerateThumbnailReply:
        return GenerateThumbnailReply(thumbnail_bytes=b"generated_thumbnail")

    def test_should_use_provided_seed_when_available(self) -> None:
        self.given_bedrock_invoke_model_succeeds()
        given_request: GenerateThumbnailRequest = (
            self.given_generate_thumbnail_request_with_seed()
        )

        self.thumbnail_generator.generate_thumbnail(given_request)

        self.then_model_was_called_with_provided_seed()
        self.seed_generator.generate.assert_not_called()

    def then_model_was_called_with_provided_seed(self) -> None:
        model_request: Dict[str, Any] = json.loads(
            self.bedrock_client.invoke_model.call_args[1]["body"]
        )
        self.assertEqual(model_request["seed"], 42)

    @staticmethod
    def given_generate_thumbnail_request_with_seed() -> GenerateThumbnailRequest:
        return GenerateThumbnailRequest(
            input_image_bytes=b"input_image_bytes", prompt="given prompt", seed=42
        )

    def test_should_generate_seed_when_not_provided(self) -> None:
        self.given_seed_generator_returns_seed()
        self.given_bedrock_invoke_model_succeeds()
        given_request: GenerateThumbnailRequest = (
            self.given_generate_thumbnail_request()
        )

        self.thumbnail_generator.generate_thumbnail(given_request)

        self.then_model_was_called_with_generated_seed()
        self.seed_generator.generate.assert_called_once()

    def then_model_was_called_with_generated_seed(self) -> None:
        model_request: Dict[str, Any] = json.loads(
            self.bedrock_client.invoke_model.call_args[1]["body"]
        )
        self.assertEqual(model_request["seed"], 12345)

    def test_should_call_the_underlying_bedrock_client_with_correct_parameters(
        self,
    ) -> None:
        self.given_seed_generator_returns_seed()
        self.given_bedrock_invoke_model_succeeds()
        given_request: GenerateThumbnailRequest = (
            self.given_generate_thumbnail_request()
        )

        self.thumbnail_generator.generate_thumbnail(given_request)

        self.then_bedrock_client_is_called_with_correct_parameters()

    def then_bedrock_client_is_called_with_correct_parameters(self) -> None:
        self.bedrock_client.invoke_model.assert_called_once()
        call_args: Dict[str, Any] = self.bedrock_client.invoke_model.call_args[1]
        self.assertEqual(call_args["modelId"], "givenModel")
        self.assertEqual(call_args["contentType"], "application/json")
        self.assertEqual(call_args["accept"], "application/json")

        body: Dict[str, Any] = json.loads(call_args["body"])
        expected_body: Dict[str, Any] = {
            "mode": "image-to-image",
            "text_prompts": [{"text": "given prompt", "weight": 1.0}],
            "init_image": base64.b64encode(b"input_image_bytes").decode("utf-8"),
            "init_image_mode": "IMAGE_STRENGTH",
            "image_strength": self.configuration.image_strength,
            "steps": self.configuration.steps,
            "cfg_scale": self.configuration.cfg_scale,
            "seed": 12345,
        }
        self.assertEqual(body, expected_body)

    def test_should_raise_error_when_bedrock_invoke_fails(self) -> None:
        self.given_seed_generator_returns_seed()
        self.given_bedrock_invoke_model_fails()
        given_request: GenerateThumbnailRequest = (
            self.given_generate_thumbnail_request()
        )

        with self.assertRaises(BedrockThumbnailGenerationError) as context:
            self.thumbnail_generator.generate_thumbnail(given_request)

        self.assertIn("Failed to invoke Bedrock model", str(context.exception))

    def given_bedrock_invoke_model_fails(self) -> None:
        self.bedrock_client.invoke_model.side_effect = Exception("Connection error")

    def test_should_raise_error_when_response_has_no_body(self) -> None:
        self.given_seed_generator_returns_seed()
        self.given_bedrock_invoke_model_returns_no_body()
        given_request: GenerateThumbnailRequest = (
            self.given_generate_thumbnail_request()
        )

        with self.assertRaises(BedrockThumbnailGenerationError) as context:
            self.thumbnail_generator.generate_thumbnail(given_request)

        self.assertIn(
            "Invalid Bedrock response: No response body received",
            str(context.exception),
        )

    def given_bedrock_invoke_model_returns_no_body(self) -> None:
        self.bedrock_client.invoke_model.return_value = {}

    def test_should_raise_error_when_response_has_invalid_format(self) -> None:
        self.given_seed_generator_returns_seed()
        self.given_bedrock_invoke_model_returns_invalid_format()
        given_request: GenerateThumbnailRequest = (
            self.given_generate_thumbnail_request()
        )

        with self.assertRaises(BedrockThumbnailGenerationError) as context:
            self.thumbnail_generator.generate_thumbnail(given_request)

        self.assertIn(
            "Invalid response format from Bedrock model", str(context.exception)
        )

    def given_bedrock_invoke_model_returns_invalid_format(self) -> None:
        mock_body: MagicMock = MagicMock()
        mock_body.read.return_value = json.dumps({"something_else": []}).encode("utf-8")
        self.bedrock_client.invoke_model.return_value = {"body": mock_body}

    def test_should_raise_error_when_response_is_not_json(self) -> None:
        self.given_seed_generator_returns_seed()
        self.given_bedrock_invoke_model_returns_non_json()
        given_request: GenerateThumbnailRequest = (
            self.given_generate_thumbnail_request()
        )

        with self.assertRaises(BedrockThumbnailGenerationError) as context:
            self.thumbnail_generator.generate_thumbnail(given_request)

        self.assertIn("Failed to parse Bedrock response", str(context.exception))

    def given_bedrock_invoke_model_returns_non_json(self) -> None:
        mock_body: MagicMock = MagicMock()
        mock_body.read.return_value = "not a json".encode("utf-8")
        self.bedrock_client.invoke_model.return_value = {"body": mock_body}

    def test_should_raise_error_when_response_body_is_empty(self) -> None:
        self.given_seed_generator_returns_seed()
        self.given_bedrock_invoke_model_returns_empty_body()
        given_request: GenerateThumbnailRequest = (
            self.given_generate_thumbnail_request()
        )

        with self.assertRaises(BedrockThumbnailGenerationError) as context:
            self.thumbnail_generator.generate_thumbnail(given_request)

        self.assertIn(
            "Invalid Bedrock response: No response body received",
            str(context.exception),
        )

    def given_bedrock_invoke_model_returns_empty_body(self) -> None:
        self.bedrock_client.invoke_model.return_value = {"body": None}

    def test_should_raise_error_when_response_body_reading_throws_exception(
        self,
    ) -> None:
        self.given_seed_generator_returns_seed()
        self.given_bedrock_invoke_model_returns_body_reading_error()
        given_request: GenerateThumbnailRequest = (
            self.given_generate_thumbnail_request()
        )

        with self.assertRaises(BedrockThumbnailGenerationError) as context:
            self.thumbnail_generator.generate_thumbnail(given_request)

        self.assertIn("Failed to read body", str(context.exception))

    def given_bedrock_invoke_model_returns_body_reading_error(self) -> None:
        mock_body: MagicMock = MagicMock()
        mock_body.read.side_effect = Exception("Read error")
        self.bedrock_client.invoke_model.return_value = {"body": mock_body}


if __name__ == "__main__":
    unittest.main()
