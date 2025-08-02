from dataclasses import dataclass


@dataclass(frozen=True)
class BedrockConfiguration:
    model_id: str
    image_strength: float
    cfg_scale: int
    steps: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.image_strength <= 1.0:
            raise ValueError("image_strength must be between 0.0 and 1.0")
        if not 1 <= self.cfg_scale <= 20:
            raise ValueError("cfg_scale must be between 1 and 20")
        if not 10 <= self.steps <= 150:
            raise ValueError("steps must be between 10 and 150")
