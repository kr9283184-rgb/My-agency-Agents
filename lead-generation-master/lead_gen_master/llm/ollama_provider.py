import json
from typing import Optional
import requests

from lead_gen_master.config import Config
from lead_gen_master.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, model: str = "llama3.2"):
        self.base_url = Config.OLLAMA_BASE_URL.rstrip("/")
        self.model = model

    def is_available(self) -> bool:
        try:
            resp = requests.get(
                f"{self.base_url}/api/tags", timeout=5
            )
            return resp.status_code == 200
        except requests.RequestException:
            return False

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        if not self.is_available():
            return ""

        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            return resp.json().get("response", "")
        except requests.RequestException as e:
            return f"[Ollama error: {e}]"
