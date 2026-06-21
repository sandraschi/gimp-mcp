"""Local LLM integration — Ollama and LM Studio with auto-detection (Glom On)."""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

import httpx

from .logging_config import get_logger

logger = get_logger(__name__)

OLLAMA_PORT = 11434
LMSTUDIO_PORT = 1234
OLLAMA_URL = f"http://127.0.0.1:{OLLAMA_PORT}"
LMSTUDIO_URL = f"http://127.0.0.1:{LMSTUDIO_PORT}"

SETTINGS_PROVIDER_KEY = "LOCAL_LLM_PROVIDER"
SETTINGS_MODEL_KEY = "LOCAL_LLM_MODEL"


def _get_provider() -> str:
    return os.environ.get(SETTINGS_PROVIDER_KEY, "disabled")


def _get_model() -> str:
    return os.environ.get(SETTINGS_MODEL_KEY, "")


def update_settings(provider: str, model: str) -> None:
    os.environ[SETTINGS_PROVIDER_KEY] = provider
    os.environ[SETTINGS_MODEL_KEY] = model


async def detect() -> dict[str, Any]:
    """Scan for running Ollama and LM Studio instances."""
    result: dict[str, Any] = {"ollama": {"running": False, "models": []}, "lmstudio": {"running": False, "models": []}}

    # Ollama
    try:
        async with httpx.AsyncClient(timeout=2) as c:
            r = await c.get(f"{OLLAMA_URL}/api/tags")
            if r.status_code == 200:
                data = r.json()
                models = [m["name"] for m in data.get("models", [])]
                result["ollama"] = {"running": True, "models": models, "url": OLLAMA_URL}
    except Exception:
        pass

    # LM Studio
    try:
        async with httpx.AsyncClient(timeout=2) as c:
            r = await c.get(f"{LMSTUDIO_URL}/v1/models")
            if r.status_code == 200:
                data = r.json()
                models = [m["id"] for m in data.get("data", [])]
                result["lmstudio"] = {"running": True, "models": models, "url": LMSTUDIO_URL}
    except Exception:
        pass

    return result


async def chat(
    messages: list[dict[str, str]],
    image_path: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> str:
    """Send a chat request to the configured local LLM. Optionally includes an image for multimodal models."""
    provider = provider or _get_provider()
    model = model or _get_model()

    if provider == "disabled" or not model:
        return "Local LLM not configured. Configure in Settings."

    if provider == "ollama":
        return await _ollama_chat(model, messages, image_path)
    elif provider == "lmstudio":
        return await _lmstudio_chat(model, messages, image_path)
    return "Unknown provider"


def _build_multimodal_messages(messages: list[dict], image_path: str | None) -> list[dict]:
    if not image_path:
        return messages
    try:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = Path(image_path).suffix.lstrip(".") or "png"
        data_uri = f"data:image/{ext};base64,{b64}"

        last_msg = messages[-1] if messages else {"role": "user", "content": ""}
        multimodal = {
            "role": last_msg.get("role", "user"),
            "content": [
                {"type": "text", "text": last_msg.get("content", "")},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ],
        }
        return [*messages[:-1], multimodal] if len(messages) > 1 else [multimodal]
    except Exception as e:
        logger.warning(f"Failed to attach image to message: {e}")
        return messages


async def _ollama_chat(model: str, messages: list[dict], image_path: str | None) -> str:
    if image_path:
        msg = messages[-1] if messages else {"role": "user", "content": ""}
        try:
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            msg["images"] = [b64]
            messages = [*messages[:-1], msg] if len(messages) > 1 else [msg]
        except Exception as e:
            logger.warning(f"Failed to attach image: {e}")

    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(f"{OLLAMA_URL}/api/chat", json={"model": model, "messages": messages, "stream": False})
        r.raise_for_status()
        data = r.json()
        return data.get("message", {}).get("content", "")


async def _lmstudio_chat(model: str, messages: list[dict], image_path: str | None) -> str:
    messages = _build_multimodal_messages(messages, image_path)
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(f"{LMSTUDIO_URL}/v1/chat/completions", json={"model": model, "messages": messages})
        r.raise_for_status()
        data = r.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")


async def understand_image(image_path: str, instruction: str = "Describe this image in detail.") -> str:
    """Use a multimodal local model to understand an image."""
    messages = [{"role": "user", "content": instruction}]
    return await chat(messages, image_path=image_path)


async def suggest_gimp_ops(image_path: str, request: str) -> list[dict]:
    example = '[{"tool": "gimp_color", "params": {"operation": "brightness_contrast", "brightness": 10}}, {"tool": "gimp_pdb", "params": {"procedure": "plug-in-gauss", "args": [0, 1, 3.0, 3.0, 0]}}]'
    prompt = (
        f"You are a GIMP expert. The user wants to: {request}\n\n"
        f"Output a JSON list of GIMP operations to execute. Each operation is an object with "
        f"'tool' (one of: gimp_color, gimp_filter, gimp_transform, gimp_layer, gimp_pdb) "
        f"and 'params' (dict of parameters). "
        f"Example: {example}\n\n"
        f"Return ONLY the JSON array, no markdown, no explanation."
    )
    result = await understand_image(image_path, prompt)
    try:
        cleaned = result.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        logger.warning(f"LLM returned non-JSON: {result[:200]}")
        return []
