"""AI image generation with switchable backends (Gemini, Stability AI, BFL/Flux)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .logging_config import get_logger

logger = get_logger(__name__)

_OUTPUT_DIR = Path("generated_images")
_OUTPUT_DIR.mkdir(exist_ok=True)

AVAILABLE_PROVIDERS = ["gemini", "stability", "bfl"]

SETTINGS_KEYS = {
    "gemini": "GEMINI_API_KEY",
    "stability": "STABILITY_API_KEY",
    "bfl": "BFL_API_KEY",
}


def get_available_providers() -> list[str]:
    return [p for p in AVAILABLE_PROVIDERS if os.environ.get(SETTINGS_KEYS[p])]


def update_settings(provider: str, api_key: str) -> None:
    os.environ[SETTINGS_KEYS[provider]] = api_key


def get_settings_status() -> dict[str, bool]:
    return {p: bool(os.environ.get(SETTINGS_KEYS[p])) for p in AVAILABLE_PROVIDERS}


async def generate(
    provider: str,
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    quality: str = "standard",
    style: str = "photorealistic",
) -> dict[str, Any]:
    provider = provider.lower()
    if provider == "gemini":
        return await _gemini_generate(prompt, width, height, quality, style)
    elif provider == "stability":
        return await _stability_generate(prompt, width, height, quality, style)
    elif provider == "bfl":
        return await _bfl_generate(prompt, width, height, quality, style)
    return {"success": False, "error": f"Unknown provider: {provider}"}


async def _gemini_generate(prompt: str, width: int, height: int, quality: str, style: str) -> dict[str, Any]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {"success": False, "error": "Gemini API key not configured. Set GEMINI_API_KEY or use Settings page."}
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        aspect = f"{width}x{height}"
        styled_prompt = f"{prompt} --style {style}" if style else prompt
        response = client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=styled_prompt,
            aspect_ratio=aspect.replace("x", ":"),
            number_of_images=1,
        )
        if not response.generated_images:
            return {"success": False, "error": "No images returned by Gemini"}
        img_data = response.generated_images[0].image.image_bytes
        import hashlib
        path = _OUTPUT_DIR / f"gemini_{hashlib.md5(prompt.encode()).hexdigest()[:8]}_{width}x{height}.png"
        path.write_bytes(img_data)
        return {"success": True, "image_path": str(path), "provider": "gemini"}
    except ImportError:
        return {"success": False, "error": "google-genai SDK not installed. Run: uv add google-genai"}
    except Exception as e:
        return {"success": False, "error": f"Gemini generation failed: {e}"}


async def _stability_generate(prompt: str, width: int, height: int, quality: str, style: str) -> dict[str, Any]:
    api_key = os.environ.get("STABILITY_API_KEY")
    if not api_key:
        return {"success": False, "error": "Stability AI API key not configured. Set STABILITY_API_KEY or use Settings page."}
    try:
        import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
        from stability_sdk import client as stability_client
        stability_api = stability_client.StabilityInference(key=api_key, verbose=False)
        answers = stability_api.generate(prompt=prompt, width=width, height=height, samples=1)
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    return {"success": False, "error": "Prompt filtered by Safety API"}
                if artifact.type == generation.ARTIFACT_IMAGE:
                    import hashlib
                    path = _OUTPUT_DIR / f"sd_{hashlib.md5(prompt.encode()).hexdigest()[:8]}_{width}x{height}.png"
                    path.write_bytes(artifact.binary)
                    return {"success": True, "image_path": str(path), "provider": "stability"}
        return {"success": False, "error": "No image artifacts returned"}
    except ImportError:
        return {"success": False, "error": "stability-sdk not installed. Run: uv add stability-sdk"}
    except Exception as e:
        return {"success": False, "error": f"Stability AI generation failed: {e}"}


async def _bfl_generate(prompt: str, width: int, height: int, quality: str, style: str) -> dict[str, Any]:
    api_key = os.environ.get("BFL_API_KEY")
    if not api_key:
        return {"success": False, "error": "BFL API key not configured. Set BFL_API_KEY or use Settings page."}
    try:
        from bfl import Bfl
        client = Bfl(api_key=api_key)
        result = client.generate_image(prompt=prompt, width=width, height=height, quality=quality)
        import hashlib
        path = _OUTPUT_DIR / f"bfl_{hashlib.md5(prompt.encode()).hexdigest()[:8]}_{width}x{height}.png"
        import httpx
        resp = httpx.get(result.url)
        resp.raise_for_status()
        path.write_bytes(resp.content)
        return {"success": True, "image_path": str(path), "provider": "bfl"}
    except ImportError:
        return {"success": False, "error": "bfl SDK not installed. Run: uv add bfl"}
    except Exception as e:
        return {"success": False, "error": f"BFL generation failed: {e}"}
