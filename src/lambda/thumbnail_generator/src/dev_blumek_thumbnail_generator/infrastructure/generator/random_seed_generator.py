import random

from dev_blumek_thumbnail_generator.infrastructure.generator.seed_generator import (
    SeedGenerator,
)


class RandomSeedGenerator(SeedGenerator):
    def generate(self) -> int:
        return random.randint(0, 2**31 - 1)
