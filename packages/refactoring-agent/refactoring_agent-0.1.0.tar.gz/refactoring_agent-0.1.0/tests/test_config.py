import pytest
from refactoring_agent.config import load_config

def test_load_default_without_file(tmp_path, monkeypatch):
    """Если файла нет, конфиг загружается с дефолтными правилами."""
    monkeypatch.chdir(tmp_path)
    cfg = load_config()
    
    # Rules должны быть на месте (дефолтные)
    assert isinstance(cfg["rules"], dict)
    assert len(cfg["rules"]) > 0
    
    # Exclude может не быть, это нормально. Проверяем, что по дефолту он пустой или None
    assert cfg.get("exclude") is None or cfg.get("exclude") == []

def test_load_custom_config(tmp_path, monkeypatch):
    """Проверяем загрузку из pyproject.toml."""
    monkeypatch.chdir(tmp_path)
    
    toml_content = """
[tool.refactoring-agent]
ai_model = "gpt-5-turbo"
exclude = ["tests", "legacy"]

[tool.refactoring-agent.rules.legacy_print]
severity = "critical"
    """
    (tmp_path / "pyproject.toml").write_text(toml_content, encoding="utf-8")
    
    cfg = load_config()
    
    assert cfg["ai_model"] == "gpt-5-turbo"
    assert "tests" in cfg["exclude"]
    assert cfg["rules"]["legacy_print"]["severity"] == "critical"
