# ./backends/providers/anthropic.py
"""Adapter for Anthropic Claude models."""
from typing import Any, Dict, List

import requests

from utilities import Print
from . import register_provider


@register_provider("anthropic")
class AnthropicProvider:
    def __init__(self, connection_config: Dict[str, Any]):
        self.base_url = connection_config.get("base_url", "https://api.anthropic.com/v1").rstrip("/")
        self.api_key = connection_config.get("api_key")
        self.model = connection_config.get("default_model")
        self.max_tokens = connection_config.get("default_max_tokens", 1024)
        self.temperature = connection_config.get("default_temperature", 0.2)
        self.version = connection_config.get("anthropic_version", "2023-06-01")
        self.extra_options = connection_config.get("options", {})
        self.request_timeout = connection_config.get("timeout", 60)

        if not self.api_key:
            raise ValueError("Anthropic providers require an API key")
        if not self.model:
            raise ValueError("Anthropic providers require a default_model")

    def generate(self, system_prompt: str, user_content: str) -> str:
        url = f"{self.base_url}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.version,
            "content-type": "application/json",
        }
        messages: List[Dict[str, Any]] = [{"role": "user", "content": user_content}]
        payload: Dict[str, Any] = {
            "model": self.model,
            "system": system_prompt,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        payload.update(self.extra_options)

        Print("ATTEMPT", f"Calling Anthropic at {self.base_url}")
        response = requests.post(url, headers=headers, json=payload, timeout=self.request_timeout)
        if not response.ok:
            raise RuntimeError(f"Anthropic error {response.status_code}: {response.text}")
        data = response.json()
        try:
            content = data["content"][0]["text"]
        except (KeyError, IndexError) as exc:
            raise RuntimeError("Malformed response from Anthropic") from exc
        return content.strip()
