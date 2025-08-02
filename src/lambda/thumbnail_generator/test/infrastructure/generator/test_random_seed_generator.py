import unittest

from dev_blumek_thumbnail_generator.infrastructure.generator.random_seed_generator import (
    RandomSeedGenerator,
)


class TestRandomSeedGenerator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.random_seed_generator = RandomSeedGenerator()

    def test_generate_returns_integer_in_correct_range(self):
        actual_seed = self.random_seed_generator.generate()

        self.assertGreaterEqual(actual_seed, 0)
        self.assertLess(actual_seed, 2**31)
