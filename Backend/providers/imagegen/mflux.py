from __future__ import annotations

import os
import time
from typing import Optional

from logstream import log
from providers.imagegen.base import ImageGenProvider


class MfluxProvider(ImageGenProvider):
    """FLUX Schnell on Apple Silicon via the ``mflux`` MLX-native package.

    Lazy-loads the model on first generate() call. Subsequent calls reuse the
    in-memory weights. Schnell defaults to 2 inference steps — quality/speed
    tradeoff is set with ``MFLUX_STEPS``.
    """

    name = "mflux"

    def __init__(self) -> None:
        self._flux = None

    def is_available(self) -> bool:
        from utils import is_mac_fast_path_available

        if not is_mac_fast_path_available():
            return False
        try:
            import mflux  # noqa: F401

            return True
        except ImportError:
            return False

    def _model_alias(self) -> str:
        return (os.getenv("MFLUX_MODEL") or "schnell").strip().lower()

    def _quantize(self) -> Optional[int]:
        raw = (os.getenv("MFLUX_QUANTIZE") or "4").strip()
        if not raw or raw.lower() in {"none", "off", "0"}:
            return None
        try:
            return int(raw)
        except ValueError:
            return 4

    def _steps(self) -> int:
        raw = (os.getenv("MFLUX_STEPS") or "").strip()
        if raw:
            try:
                return int(raw)
            except ValueError:
                pass
        # Schnell looks great at 2 steps; dev needs ~20.
        return 4 if self._model_alias() == "schnell" else 20

    def _ensure_model(self) -> None:
        if self._flux is not None:
            return
        from mflux import Flux1

        alias = self._model_alias()
        quantize = self._quantize()
        log(
            f"[+] Loading mflux model='{alias}' quantize={quantize} (first call may download weights)",
            "info",
        )
        self._flux = Flux1.from_alias(alias=alias, quantize=quantize)

    def generate(
        self,
        prompt: str,
        out_path: str,
        *,
        width: int = 1024,
        height: int = 1792,
    ) -> str:
        from mflux import Config

        self._ensure_model()

        # FLUX requires multiples of 16.
        width = max(256, (int(width) // 16) * 16)
        height = max(256, (int(height) // 16) * 16)

        seed = int(time.time() * 1000) % 2_000_000_000
        config = Config(
            num_inference_steps=self._steps(),
            height=height,
            width=width,
        )
        log(
            f"[+] mflux generate: '{prompt[:60]}' ({width}x{height}, steps={config.num_inference_steps})",
            "info",
        )
        image = self._flux.generate_image(seed=seed, prompt=prompt, config=config)
        image.save(out_path)
        return out_path
