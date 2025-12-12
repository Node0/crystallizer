# ./backends/providers/openai.py
"""Adapter for OpenAI-compatible chat completion APIs (OpenAI, Fireworks, etc.)."""
from typing import Any, Dict

import requests

from utilities import Print
from . import register_provider


@register_provider("openai")
class OpenAIProvider:
    def __init__(self, connection_config: Dict[str, Any]):
        self.base_url = connection_config.get("base_url", "https://api.openai.com/v1").rstrip("/")
        self.api_key = connection_config.get("api_key")
        self.model = connection_config.get("default_model")
        self.max_tokens = connection_config.get("default_max_tokens", 1024)
        self.temperature = connection_config.get("default_temperature", 0.2)
        self.request_timeout = connection_config.get("timeout", 60)
        self.extra_options = connection_config.get("options", {})

        if not self.api_key:
            raise ValueError("OpenAI-compatible providers require an API key")
        if not self.model:
            raise ValueError("OpenAI-compatible providers require a default_model")

    def generate(self, system_prompt: str, user_content: str) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        }
        payload.update(self.extra_options)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url}/chat/completions"
        Print("ATTEMPT", f"Calling OpenAI-compatible provider at {self.base_url}")
        response = requests.post(url, headers=headers, json=payload, timeout=self.request_timeout)
        if not response.ok:
            raise RuntimeError(
                f"OpenAI-compatible provider error {response.status_code}: {response.text}"
            )
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise RuntimeError("Malformed response from OpenAI-compatible provider") from exc
