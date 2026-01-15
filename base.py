import os
import dotenv
import requests
import uuid
from typing import Dict, Any, Optional

class BaseAgent:
    def __init__(self, name: str, llm_client=None, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.execution_log = []

        # OpenRouter configuration
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set in environment")

        self.model = self.config.get(
            "model",
            "openai/gpt-4o-mini"  # cheap + fast, change anytime
        )

    async def _call_llm(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 800
    ) -> str:
        """Actual OpenRouter API call"""

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",  # required by OpenRouter
            "X-Title": "AETHER"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"OpenRouter error {response.status_code}: {response.text}"
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    def log_execution(self, event: str, data: Any):
        self.execution_log.append({
            "id": str(uuid.uuid4()),
            "event": event,
            "data": data
        })
