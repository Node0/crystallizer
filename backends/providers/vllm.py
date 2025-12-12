# ./backends/providers/vllm.py
"""Adapter for vLLM deployments exposing the OpenAI-compatible API."""
from typing import Any, Dict

import requests

from utilities import Print
from . import register_provider


@register_provider("vllm")
class VLLMProvider:
    def __init__(self, connection_config: Dict[str, Any]):
        self.base_url = connection_config.get("base_url", "http://localhost:8000/v1").rstrip("/")
        self.api_key = connection_config.get("api_key")
        self.model = connection_config.get("default_model")
        self.max_tokens = connection_config.get("default_max_tokens", 1024)
        self.temperature = connection_config.get("default_temperature", 0.7)
        self.extra_options = connection_config.get("options", {})
        self.request_timeout = connection_config.get("timeout", 60)

        # Some vLLM deployments may not require auth
        if not self.model:
            raise ValueError("vLLM providers require a default_model")

    def generate(self, system_prompt: str, user_content: str) -> str:
        url = f"{self.base_url}/chat/completions"
        payload: Dict[str, Any] = {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
        }
        payload.update(self.extra_options)

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        Print("ATTEMPT", f"Calling vLLM at {self.base_url}")
        response = requests.post(url, headers=headers, json=payload, timeout=self.request_timeout)
        if not response.ok:
            raise RuntimeError(f"vLLM error {response.status_code}: {response.text}")
        data = response.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError) as exc:
            raise RuntimeError("Malformed response from vLLM provider") from exc
