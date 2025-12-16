import pytest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from refactoring_agent.ai_handler import get_ai_fix

def test_get_ai_fix_success():
    """Проверяет, что get_ai_fix вызывает LLM и возвращает чистый код."""
    snippet = "import os\nos.system('ls')"
    issue = {"message": "Use subprocess", "line": 2}
    
    # Эмулируем конфиг
    config = SimpleNamespace(ai_provider="openai", ai_model="gpt-4o")

    # Мокаем вызов call_llm внутри ai_handler
    with patch("refactoring_agent.ai_handler.call_llm") as mock_llm:
        # Имитируем ответ от ИИ (с маркдауном, который должен убраться)
        mock_llm.return_value = "```python\nimport subprocess\nsubprocess.run(['ls'])\n```"
        
        fixed_code = get_ai_fix(snippet, issue, config)
        
        # Проверяем, что вызов был
        assert mock_llm.called
        # Проверяем, что результат очищен от маркдауна
        assert "subprocess.run" in fixed_code
        assert "```" not in fixed_code

def test_get_ai_fix_handles_error():
    """Проверяет, что при ошибке LLM функция не падает, а возвращает None."""
    snippet = "code"
    issue = {"message": "msg", "line": 1}
    config = SimpleNamespace(ai_provider="openai", ai_model="gpt-4")

    with patch("refactoring_agent.ai_handler.call_llm") as mock_llm:
        # Эмулируем ошибку сети/API
        mock_llm.side_effect = Exception("API Error")
        
        fixed_code = get_ai_fix(snippet, issue, config)
        
        assert fixed_code is None
