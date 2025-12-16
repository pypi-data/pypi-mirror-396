import os
import sys

class LLMConfigError(Exception):
    pass

class OpenAIProvider:
    def __init__(self, model: str, timeout: int = 60):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package is required. pip install openai")
        
        api_key = os.getenv("RA_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise LLMConfigError("OpenAI API key not found. Please set RA_OPENAI_API_KEY.")
        
        self.client = OpenAI(api_key=api_key, timeout=timeout)
        self.model = model or "gpt-4o-mini"

    def get_completion(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior python refactoring agent. Return only code."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"OpenAI API Error: {e}")

class OllamaProvider:
    def __init__(self, model: str, base_url: str, timeout: int = 60):
        try:
            import httpx
        except ImportError:
            raise ImportError("httpx is required for Ollama. pip install httpx")
        
        self.base_url = base_url or "http://localhost:11434"
        self.model = model or "qwen2.5-coder:7b"
        self.timeout = timeout

    def get_completion(self, prompt: str) -> str:
        import httpx
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "system": "You are a senior python refactoring agent. Return only code."
        }
        try:
            response = httpx.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            # Красивая ошибка, если Ollama не запущена
            raise RuntimeError(f"Ollama Connection Error ({self.base_url}): {e}")

def get_llm_provider():
    """
    Factory function to return the correct provider based on strict env config.
    """
    # 1. Читаем провайдера (которого мы жестко установили в CLI)
    provider_name = os.getenv("RA_LLM_PROVIDER", "").lower().strip()
    
    # 2. Логика выбора (Strict Mode)
    if provider_name == "ollama":
        model = os.getenv("RA_LLM_MODEL", "qwen2.5-coder:7b")
        base_url = os.getenv("RA_LLM_BASE_URL", "http://localhost:11434")
        return OllamaProvider(model=model, base_url=base_url)

    if provider_name == "openai":
        model = os.getenv("RA_LLM_MODEL", "gpt-4o-mini")
        return OpenAIProvider(model=model)

    # 3. Fallback (если ничего не задано, пробуем найти ключи)
    if os.getenv("RA_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"):
        return OpenAIProvider(model="gpt-4o-mini")
        
    # Если мы здесь — конфигурация невалидна
    raise LLMConfigError(
        "No valid LLM configuration found.\n"
        "Please set RA_LLM_PROVIDER='ollama' or provide OpenAI keys."
    )
