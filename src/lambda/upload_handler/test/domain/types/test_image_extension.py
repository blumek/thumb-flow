import unittest
from unittest import TestCase
from parameterized import parameterized

from domain.types.image_extension import ImageExtension


class TestImageExtension(TestCase):
    @parameterized.expand(
        [
            (ImageExtension.JPG, "jpg", "image/jpeg"),
            (ImageExtension.JPEG, "jpeg", "image/jpeg"),
            (ImageExtension.PNG, "png", "image/png"),
            (ImageExtension.GIF, "gif", "image/gif"),
            (ImageExtension.SVG, "svg", "image/svg+xml"),
            (ImageExtension.WEBP, "webp", "image/webp"),
            (ImageExtension.BMP, "bmp", "image/bmp"),
        ]
    )
    def test_should_return_correct_extension_and_mime_type(
        self, given_extension, expected_extension, expected_mime_type
    ):
        actual_extension = given_extension.extension
        actual_mime_type = given_extension.mime_type

        self.assertEqual(expected_extension, actual_extension)
        self.assertEqual(expected_mime_type, actual_mime_type)

    @parameterized.expand(
        [
            ("png", ImageExtension.PNG),
            ("jpg", ImageExtension.JPG),
            ("jpeg", ImageExtension.JPEG),
            ("gif", ImageExtension.GIF),
            ("svg", ImageExtension.SVG),
            ("webp", ImageExtension.WEBP),
            ("bmp", ImageExtension.BMP),
        ]
    )
    def test_from_extension_should_return_correct_enum_for_valid_extension(
        self, given_extension, expected_enum
    ):
        actual_result = ImageExtension.from_extension(given_extension)

        self.assertEqual(expected_enum, actual_result)

    @parameterized.expand(
        [
            (".jpg", ImageExtension.JPG),
            (".png", ImageExtension.PNG),
            (".gif", ImageExtension.GIF),
            (".jpeg", ImageExtension.JPEG),
            (".svg", ImageExtension.SVG),
            (".webp", ImageExtension.WEBP),
            (".bmp", ImageExtension.BMP),
        ]
    )
    def test_from_extension_should_return_correct_enum_for_extension_with_dot(
        self, given_extension, expected_enum
    ):
        actual_result = ImageExtension.from_extension(given_extension)

        self.assertEqual(expected_enum, actual_result)

    @parameterized.expand(
        [
            ("PNG", ImageExtension.PNG),
            ("JPG", ImageExtension.JPG),
            ("JPEG", ImageExtension.JPEG),
            ("GIF", ImageExtension.GIF),
            ("SVG", ImageExtension.SVG),
            ("WEBP", ImageExtension.WEBP),
            ("BMP", ImageExtension.BMP),
        ]
    )
    def test_from_extension_should_return_correct_enum_for_uppercase_extension(
        self, given_extension, expected_enum
    ):
        actual_result = ImageExtension.from_extension(given_extension)

        self.assertEqual(expected_enum, actual_result)

    @parameterized.expand(
        [
            ("txt",),
            ("doc",),
            ("pdf",),
            ("mp4",),
        ]
    )
    def test_from_extension_should_return_none_for_invalid_extension(
        self, given_extension
    ):
        actual_result = ImageExtension.from_extension(given_extension)

        self.assertIsNone(actual_result)

    @parameterized.expand(
        [
            ("",),
            (None,),
        ]
    )
    def test_from_extension_should_return_none_for_empty_or_none_extension(
        self, given_extension
    ):
        actual_result = ImageExtension.from_extension(given_extension)  # type: ignore

        self.assertIsNone(actual_result)


if __name__ == "__main__":
    unittest.main()
