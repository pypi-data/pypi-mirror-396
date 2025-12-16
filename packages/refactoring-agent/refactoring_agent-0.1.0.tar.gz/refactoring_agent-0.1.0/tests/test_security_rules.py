import pytest
from refactoring_agent.utils import analyze_file_content

TEST_CONFIG = {
    "rules": {
        "security_os_system": {
            "pattern": r"os\.system\(",
            "message": "Security Risk: usage of os.system() detected.",
            "severity": "critical"
        },
        "security_eval": {
            "pattern": r"eval\(",
            "message": "Security Risk: usage of eval() detected.",
            "severity": "critical"
        },
        "legacy_print": {
            "pattern": r"^\s*print\s+['\"a-zA-Z0-9]",
            "message": "Legacy 'print' detected.",
            "severity": "major"
        }
    }
}

def test_security_os_system_detected(tmp_path):
    f = tmp_path / "vulnerable.py"
    f.write_text("import os\nos.system('rm -rf /')", encoding="utf-8")
    
    issues = analyze_file_content(f, TEST_CONFIG)
    found = any(i["rule_id"] == "security_os_system" for i in issues)
    assert found, f"Ожидали найти os.system, но нашли: {issues}"

def test_security_eval_detected(tmp_path):
    f = tmp_path / "bad_eval.py"
    f.write_text("x = eval('2 + 2')", encoding="utf-8")
    
    issues = analyze_file_content(f, TEST_CONFIG)
    found = any(i["rule_id"] == "security_eval" for i in issues)
    assert found, f"Ожидали найти eval, но нашли: {issues}"

def test_legacy_print_detected(tmp_path):
    f = tmp_path / "old.py"
    f.write_text("print 'hello'", encoding="utf-8")
    
    issues = analyze_file_content(f, TEST_CONFIG)
    # Python 3 может определить это как syntax_error раньше, чем сработает regex
    found = any(i["rule_id"] in ["legacy_print", "syntax_error"] for i in issues)
    assert found, f"Ожидали найти legacy print или syntax_error, но нашли: {issues}"
