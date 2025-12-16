from .llm_provider import get_llm_provider

class LLMClient:
    def __init__(self):
        # Получаем правильного провайдера (Ollama или OpenAI) с учетом Strict Mode
        self.provider = get_llm_provider()

    def get_completion(self, prompt: str) -> str:
        """
        Отправляет запрос к AI и возвращает ответ.
        """
        return self.provider.get_completion(prompt)
