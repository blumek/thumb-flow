import unittest

from domain.types.image_extension import ImageExtension
from infrastructure.gateway.image_persistence_gateway_model import StoreImageGatewayRequest
from infrastructure.policy.image_policy import (
    ImagePolicyComposite,
    ImagePolicySize,
    ImagePolicyExtension,
)


class TestImagePolicySize(unittest.TestCase):
    def test_is_valid_when_image_size_is_less_than_max_size(self):
        # Arrange
        max_size = 1000
        policy = ImagePolicySize(max_bytes_size=max_size)
        request = StoreImageGatewayRequest(
            image_name="test_image",
            image_extension=ImageExtension.PNG,
            image_bytes=b"x" * 500,  # 500 bytes, less than max
        )

        # Act
        result = policy.is_valid(request)

        # Assert
        self.assertTrue(result)

    def test_is_valid_when_image_size_equals_max_size(self):
        # Arrange
        max_size = 1000
        policy = ImagePolicySize(max_bytes_size=max_size)
        request = StoreImageGatewayRequest(
            image_name="test_image",
            image_extension=ImageExtension.PNG,
            image_bytes=b"x" * 1000,  # 1000 bytes, equal to max
        )

        # Act
        result = policy.is_valid(request)

        # Assert
        self.assertTrue(result)

    def test_is_invalid_when_image_size_exceeds_max_size(self):
        # Arrange
        max_size = 1000
        policy = ImagePolicySize(max_bytes_size=max_size)
        request = StoreImageGatewayRequest(
            image_name="test_image",
            image_extension=ImageExtension.PNG,
            image_bytes=b"x" * 1001,  # 1001 bytes, exceeds max
        )

        # Act
        result = policy.is_valid(request)

        # Assert
        self.assertFalse(result)


class TestImagePolicyExtension(unittest.TestCase):
    def test_is_valid_when_extension_is_allowed(self):
        # Arrange
        allowed_extensions = {"png", "jpg"}
        policy = ImagePolicyExtension(allowed_extensions=allowed_extensions)
        request = StoreImageGatewayRequest(
            image_name="test_image",
            image_extension=ImageExtension.PNG,
            image_bytes=b"test_image_data",
        )

        # Act
        result = policy.is_valid(request)

        # Assert
        self.assertTrue(result)

    def test_is_invalid_when_extension_is_not_allowed(self):
        # Arrange
        allowed_extensions = {"png", "jpg"}
        policy = ImagePolicyExtension(allowed_extensions=allowed_extensions)
        request = StoreImageGatewayRequest(
            image_name="test_image",
            image_extension=ImageExtension.GIF,
            image_bytes=b"test_image_data",
        )

        # Act
        result = policy.is_valid(request)

        # Assert
        self.assertFalse(result)

    def test_is_valid_with_case_insensitive_extensions(self):
        # Arrange
        allowed_extensions = {"PNG", "jpg"}  # Uppercase PNG
        policy = ImagePolicyExtension(allowed_extensions=allowed_extensions)
        request = StoreImageGatewayRequest(
            image_name="test_image",
            image_extension=ImageExtension.PNG,
            image_bytes=b"test_image_data",
        )

        # Act
        result = policy.is_valid(request)

        # Assert
        self.assertTrue(result)


class TestImagePolicyComposite(unittest.TestCase):
    def test_is_valid_when_all_policies_pass(self):
        # Arrange
        size_policy = ImagePolicySize(max_bytes_size=1000)
        extension_policy = ImagePolicyExtension(allowed_extensions={"png", "jpg"})
        composite_policy = ImagePolicyComposite(size_policy, extension_policy)

        request = StoreImageGatewayRequest(
            image_name="test_image",
            image_extension=ImageExtension.PNG,
            image_bytes=b"x" * 500,  # 500 bytes, less than max
        )

        # Act
        result = composite_policy.is_valid(request)

        # Assert
        self.assertTrue(result)

    def test_is_invalid_when_any_policy_fails(self):
        # Arrange
        size_policy = ImagePolicySize(max_bytes_size=1000)
        extension_policy = ImagePolicyExtension(allowed_extensions={"png", "jpg"})
        composite_policy = ImagePolicyComposite(size_policy, extension_policy)

        # Request with valid size but invalid extension
        request = StoreImageGatewayRequest(
            image_name="test_image",
            image_extension=ImageExtension.GIF,  # Not allowed
            image_bytes=b"x" * 500,  # 500 bytes, less than max
        )

        # Act
        result = composite_policy.is_valid(request)

        # Assert
        self.assertFalse(result)

    def test_is_invalid_when_multiple_policies_fail(self):
        # Arrange
        size_policy = ImagePolicySize(max_bytes_size=1000)
        extension_policy = ImagePolicyExtension(allowed_extensions={"png", "jpg"})
        composite_policy = ImagePolicyComposite(size_policy, extension_policy)

        # Request with invalid size and invalid extension
        request = StoreImageGatewayRequest(
            image_name="test_image",
            image_extension=ImageExtension.GIF,  # Not allowed
            image_bytes=b"x" * 1500,  # 1500 bytes, exceeds max
        )

        # Act
        result = composite_policy.is_valid(request)

        # Assert
        self.assertFalse(result)

    def test_is_valid_with_no_policies(self):
        # Arrange
        composite_policy = ImagePolicyComposite()  # No policies

        request = StoreImageGatewayRequest(
            image_name="test_image",
            image_extension=ImageExtension.PNG,
            image_bytes=b"test_image_data",
        )

        # Act
        result = composite_policy.is_valid(request)

        # Assert
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
