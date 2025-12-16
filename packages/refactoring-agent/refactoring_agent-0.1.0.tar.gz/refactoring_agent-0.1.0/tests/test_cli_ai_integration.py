import pytest
import sys
import logging
from unittest.mock import patch, MagicMock
from refactoring_agent.cli import main

def test_cli_invokes_ai_when_flag_is_set(tmp_path, capsys):
    """Проверяем, что при --ai-fix вызывается call_llm."""
    
    # 1. Создаем файл с "плохим" кодом
    f = tmp_path / "bad.py"
    f.write_text("print 'hello'", encoding="utf-8")
    
    # 2. Мокаем анализатор, чтобы он вернул CRITICAL ошибку
    fake_issues = [{
        "rule_id": "test_critical_rule",
        "severity": "critical",
        "message": "Must be fixed by AI",
        "line": 1
    }]
    
    # 3. Мокаем Console, чтобы Rich не ломал захват вывода
    with patch("refactoring_agent.cli.Console"):
        # Мокаем анализатор
        with patch("refactoring_agent.cli.analyze_file_content", return_value=fake_issues):
            # Мокаем вызов LLM
            with patch("refactoring_agent.ai_handler.call_llm") as mock_llm:
                mock_llm.return_value = "print('hello')"
                
                argv = ["refactor-agent", str(tmp_path), "--ai-fix", "--dry-run"]
                
                with patch.object(sys, "argv", argv):
                    try:
                        main()
                    except SystemExit:
                        pass
                
                # Проверяем, что AI был вызван
                assert mock_llm.called

def test_cli_ai_fails_gracefully(tmp_path, caplog):
    """Проверяем, что падение LLM пишет ошибку в лог."""
    f = tmp_path / "bad.py"
    f.write_text("print 'hello'", encoding="utf-8")
    
    fake_issues = [{
        "rule_id": "test_critical_rule",
        "severity": "critical",
        "message": "Must be fixed",
        "line": 1
    }]

    with patch("refactoring_agent.cli.Console"):
        with patch("refactoring_agent.cli.analyze_file_content", return_value=fake_issues):
            with patch("refactoring_agent.ai_handler.call_llm") as mock_llm:
                # Эмулируем ошибку сети
                mock_llm.side_effect = RuntimeError("Connection refused")
                
                argv = ["refactor-agent", str(tmp_path), "--ai-fix", "--dry-run"]
                
                with patch.object(sys, "argv", argv):
                    # Ловим логи уровня ERROR
                    with caplog.at_level(logging.ERROR):
                        try:
                            main()
                        except SystemExit:
                            pass
                
                # ИСПРАВЛЕНИЕ: Ищем фразу "AI Fix failed", так как именно её пишет логгер
                assert "AI Fix failed" in caplog.text
