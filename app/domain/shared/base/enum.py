from enum import Enum


class PestSenseEnum(str, Enum):
    """String enum base for stable JSON contracts."""

    def __str__(self) -> str:
        return self.value