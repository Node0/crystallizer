# ./backends/providers/ollama.py
"""Adapter for local Ollama servers."""
from typing import Any, Dict

import requests

from utilities import Print
from . import register_provider


@register_provider("ollama")
class OllamaProvider:
    def __init__(self, connection_config: Dict[str, Any]):
        self.base_url = connection_config.get("base_url", "http://localhost:11434").rstrip("/")
        self.model = connection_config.get("default_model")
        self.max_tokens = connection_config.get("default_max_tokens", 1024)
        self.temperature = connection_config.get("default_temperature", 0.2)
        self.options = connection_config.get("options", {})
        self.request_timeout = connection_config.get("timeout", 120)

        if not self.model:
            raise ValueError("Ollama providers require a default_model")

    def generate(self, system_prompt: str, user_content: str) -> str:
        url = f"{self.base_url}/api/chat"
        payload: Dict[str, Any] = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
                **self.options,
            },
        }
        Print("ATTEMPT", f"Calling Ollama at {self.base_url}")
        response = requests.post(url, json=payload, timeout=self.request_timeout)
        if not response.ok:
            raise RuntimeError(f"Ollama error {response.status_code}: {response.text}")
        data = response.json()
        message = data.get("message", {})
        content = message.get("content")
        if not content:
            raise RuntimeError("Malformed response from Ollama")
        return content.strip()
