import pytest
import os
from refactoring_agent.llm_provider import LLMConfig, LLMConfigError

def test_fail_closed_ollama_with_openai_key():
    """Сценарий: Пользователь хочет Ollama, но забыл unset OPENAI_KEY."""
    env = {
        "RA_LLM_PROVIDER": "ollama",
        "RA_LLM_MODEL": "qwen2.5-coder",
        "RA_LLM_BASE_URL": "http://localhost:11434",
        "OPENAI_API_KEY": "sk-dangerous-key" # <--- Конфликт!
    }
    
    # Подменяем переменные окружения
    with pytest.MonkeyPatch.context() as m:
        for k, v in env.items():
            m.setenv(k, v)
        
        # Должно упасть с ошибкой безопасности
        with pytest.raises(LLMConfigError) as excinfo:
            LLMConfig.from_env()
        
        assert "SECURITY ERROR" in str(excinfo.value)
        assert "обнаружены ключи OpenAI" in str(excinfo.value)

def test_ambiguous_auto_mode():
    """Сценарий: Auto режим, но есть конфиги от обоих провайдеров."""
    env = {
        "RA_LLM_PROVIDER": "", # auto
        "RA_LLM_MODEL": "qwen2.5-coder",
        "RA_LLM_BASE_URL": "http://localhost:11434",
        "OPENAI_API_KEY": "sk-test"
    }
    
    with pytest.MonkeyPatch.context() as m:
        for k, v in env.items():
            m.setenv(k, v)
            
        with pytest.raises(LLMConfigError) as excinfo:
            LLMConfig.from_env()
        
        assert "AMBIGUOUS CONFIG" in str(excinfo.value)
