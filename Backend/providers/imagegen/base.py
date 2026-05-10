from __future__ import annotations

from abc import ABC, abstractmethod


class ImageGenProvider(ABC):
    """Generates a 9:16 image for a text prompt and saves it to disk."""

    name: str = "base"

    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def generate(
        self,
        prompt: str,
        out_path: str,
        *,
        width: int = 1024,
        height: int = 1792,
    ) -> str: ...
