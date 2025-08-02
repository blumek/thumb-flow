import unittest
from parameterized import parameterized

from dev_blumek_thumbnail_generator.infrastructure.generator.becrock_configuration import (
    BedrockConfiguration,
)


class TestBedrockConfiguration(unittest.TestCase):
    def test_should_create_configuration_with_valid_parameters(self) -> None:
        actual_configuration: BedrockConfiguration = BedrockConfiguration(
            model_id="givenModel", image_strength=0.5, cfg_scale=10, steps=50
        )

        self.assertEqual(actual_configuration.model_id, "givenModel")
        self.assertEqual(actual_configuration.image_strength, 0.5)
        self.assertEqual(actual_configuration.cfg_scale, 10)
        self.assertEqual(actual_configuration.steps, 50)

    @parameterized.expand(
        [("lower_bound", 0.0), ("middle_value", 0.5), ("upper_bound", 1.0)]
    )
    def test_should_accept_valid_image_strength(
        self, _name: str, given_value: float
    ) -> None:
        actual_configuration: BedrockConfiguration = BedrockConfiguration(
            model_id="test", image_strength=given_value, cfg_scale=10, steps=50
        )

        self.assertEqual(actual_configuration.image_strength, given_value)

    @parameterized.expand(
        [
            ("below_lower_bound", -0.1, "image_strength must be between 0.0 and 1.0"),
            ("above_upper_bound", 1.1, "image_strength must be between 0.0 and 1.0"),
        ]
    )
    def test_should_reject_invalid_image_strength(
        self, _name: str, given_value: float, expected_message: str
    ) -> None:
        with self.assertRaises(ValueError) as context:
            BedrockConfiguration(
                model_id="test", image_strength=given_value, cfg_scale=10, steps=50
            )
        self.assertIn(expected_message, str(context.exception))

    @parameterized.expand(
        [("lower_bound", 1), ("middle_value", 10), ("upper_bound", 20)]
    )
    def test_should_accept_valid_cfg_scale(self, _name: str, given_value: int) -> None:
        actual_configuration: BedrockConfiguration = BedrockConfiguration(
            model_id="test", image_strength=0.5, cfg_scale=given_value, steps=50
        )

        self.assertEqual(actual_configuration.cfg_scale, given_value)

    @parameterized.expand(
        [
            ("below_lower_bound", 0, "cfg_scale must be between 1 and 20"),
            ("above_upper_bound", 21, "cfg_scale must be between 1 and 20"),
        ]
    )
    def test_should_reject_invalid_cfg_scale(
        self, _name: str, given_value: int, expected_message: str
    ) -> None:
        with self.assertRaises(ValueError) as context:
            BedrockConfiguration(
                model_id="test", image_strength=0.5, cfg_scale=given_value, steps=50
            )

        self.assertIn(expected_message, str(context.exception))

    @parameterized.expand(
        [("lower_bound", 10), ("middle_value", 50), ("upper_bound", 150)]
    )
    def test_should_accept_valid_steps(self, _name: str, given_value: int) -> None:
        actual_configuration: BedrockConfiguration = BedrockConfiguration(
            model_id="test", image_strength=0.5, cfg_scale=10, steps=given_value
        )

        self.assertEqual(actual_configuration.steps, given_value)

    @parameterized.expand(
        [
            ("below_lower_bound", 9, "steps must be between 10 and 150"),
            ("above_upper_bound", 151, "steps must be between 10 and 150"),
        ]
    )
    def test_should_reject_invalid_steps(
        self, _name: str, given_value: int, expected_message: str
    ) -> None:
        with self.assertRaises(ValueError) as context:
            BedrockConfiguration(
                model_id="test", image_strength=0.5, cfg_scale=10, steps=given_value
            )

        self.assertIn(expected_message, str(context.exception))


if __name__ == "__main__":
    unittest.main()
