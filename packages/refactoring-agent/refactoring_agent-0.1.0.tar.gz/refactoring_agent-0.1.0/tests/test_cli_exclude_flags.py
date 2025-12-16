import pytest
from unittest.mock import patch
from refactoring_agent.cli import main

def run_cli(monkeypatch, cwd, args, capsys):
    """Хелпер для запуска CLI."""
    import sys
    
    monkeypatch.chdir(cwd)
    # ИСПРАВЛЕНИЕ: Убрали "check". 
    # "." означает текущую папку (которую мы подменили через chdir)
    argv = ["refactor-agent", "."] + args
    
    with patch.object(sys, "argv", argv):
        try:
            main()
        except SystemExit:
            pass 
    
    return capsys.readouterr().out

def test_cli_exclude_flag_excludes_custom_directory(tmp_path, capsys, monkeypatch):
    """Проверяем флаг --exclude (приоритет над всем)."""
    (tmp_path / "main.py").write_text("print('ok')\n", encoding="utf-8")
    
    legacy_dir = tmp_path / "demo_legacy"
    legacy_dir.mkdir()
    (legacy_dir / "legacy.py").write_text("print 'old'\n", encoding="utf-8")

    # Без флага -> 2 файла
    out_default = run_cli(monkeypatch, tmp_path, [], capsys)
    assert "Found 2 python files" in out_default

    # С флагом -> 1 файл
    out_excluded = run_cli(monkeypatch, tmp_path, ["--exclude", "demo_legacy"], capsys)
    assert "Found 1 python files" in out_excluded
    assert "demo_legacy/legacy.py" not in out_excluded

def test_config_exclude_rule_is_respected(tmp_path, capsys, monkeypatch):
    """Проверяем, что exclude из конфига работает."""
    (tmp_path / "main.py").write_text("print('main')\n", encoding="utf-8")
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_legacy.py").write_text("val = raw_input('old')\n", encoding="utf-8")
    
    fake_config = {
        "exclude": ["tests"], 
        "rules": {}, 
        "ai_provider": "openai"
    }

    # Патчим load_config именно внутри CLI, так как там он импортирован
    with patch("refactoring_agent.cli.load_config", return_value=fake_config):
        out = run_cli(monkeypatch, tmp_path, [], capsys)
        
    assert "Found 1 python files" in out

def test_cli_no_default_excludes_flag(tmp_path, capsys, monkeypatch):
    """Проверяем флаг --no-default-excludes."""
    (tmp_path / "main.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "vendor.py").write_text("print('vendor')\n", encoding="utf-8")
    
    fake_config_with_defaults = {
        "exclude": ["vendor.py"],
        "rules": {}
    }
    
    # 1. Проверяем, что конфиг работает
    with patch("refactoring_agent.cli.load_config", return_value=fake_config_with_defaults):
        out_normal = run_cli(monkeypatch, tmp_path, [], capsys)
    assert "Found 1 python files" in out_normal 
    
    # 2. Проверяем с флагом --no-default-excludes
    with patch("refactoring_agent.cli.load_config", return_value=fake_config_with_defaults):
         out_flag = run_cli(monkeypatch, tmp_path, ["--no-default-excludes"], capsys)
    
    assert "Found 2 python files" in out_flag
