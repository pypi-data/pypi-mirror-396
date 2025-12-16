import pytest
import os
from unittest import mock
from refactoring_agent.llm_provider import LLMConfig, LLMConfigError

def test_llm_config_defaults():
    """Проверяем дефолтное поведение (Auto)."""
    # В новой безопасной системе пустой конфиг вызывает ошибку.
    # Чтобы проверить успешный Auto-выбор, дадим хотя бы ключ (имитация OpenAI)
    env = {"OPENAI_API_KEY": "sk-mock"}
    
    with mock.patch.dict(os.environ, env, clear=True):
        cfg = LLMConfig.from_env()
        assert cfg.provider == "openai"
        assert cfg.model == "gpt-4o-mini"
        assert cfg.timeout == 120.0

def test_llm_config_ollama_env():
    """Проверяем настройки Ollama через Env."""
    test_env = {
        "RA_LLM_PROVIDER": "ollama",
        "RA_LLM_MODEL": "llama3-custom",
        "RA_LLM_BASE_URL": "http://localhost:11434", # <-- Обязательно для Strict Mode!
        "RA_LLM_TIMEOUT": "300"
    }
    
    # Важно: очищаем OPENAI ключи, чтобы не было конфликта безопасности
    with mock.patch.dict(os.environ, test_env, clear=True):
        cfg = LLMConfig.from_env()
        assert cfg.provider == "ollama"
        assert cfg.model == "llama3-custom"
        assert cfg.timeout == 300.0

def test_llm_config_fail_empty():
    """Новый тест: проверяем, что абсолютно пустое окружение роняет систему (Fail Closed)."""
    with mock.patch.dict(os.environ, {}, clear=True):
        with pytest.raises(LLMConfigError):
            LLMConfig.from_env()
