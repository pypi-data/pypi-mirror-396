import os
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Union

# Регулярка для поиска строк в кавычках (чтобы не реагировать на слова внутри текста)
_STRING_RE = re.compile(r"""('([^'\\]|\\.)*'|\"([^\"\\]|\\.)*\")""")

def _strip_strings_and_comments(line: str) -> str:
    """
    Удаляет строковые литералы и комментарии.
    Пример: print("os.system detected") -> print("")
    """
    line = _STRING_RE.sub("''", line)
    if "#" in line:
        line = line.split("#", 1)[0]
    return line

def collect_python_files(root: Path, exclude_patterns: List[str]) -> List[str]:
    python_files = []
    normalized_excludes = [p.rstrip("/") for p in exclude_patterns]

    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not _is_excluded(os.path.join(root_dir, d), normalized_excludes)]
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root_dir, file)
                if not _is_excluded(full_path, normalized_excludes):
                    python_files.append(full_path)
    return python_files

def _is_excluded(path: str, patterns: List[str]) -> bool:
    for pat in patterns:
        if pat in path: return True
        if os.path.basename(path) == pat: return True
    return False

def analyze_file_content(file_path: str, config: Union[Dict, Any]) -> List[Dict[str, Any]]:
    issues = []
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        return [{"rule_id": "read_error", "severity": "critical", "message": f"Error: {e}", "line": 0}]

    try:
        ast.parse(content)
    except SyntaxError as e:
        return [{"rule_id": "syntax_error", "severity": "critical", "message": f"Syntax Error: {e.msg}", "line": e.lineno or 0}]

    if isinstance(config, dict):
        rules = config.get("rules", {})
    else:
        rules = getattr(config, "rules", {})

    lines = content.splitlines()

    for rule_id, rule_cfg in rules.items():
        if rule_cfg.get("mode") == "ignore": continue
        
        severity = rule_cfg.get("severity", "major")
        message = rule_cfg.get("message", "Issue detected")
        
        for i, line in enumerate(lines, 1):
            # ВАЖНО: Очищаем строку перед проверкой!
            scan = _strip_strings_and_comments(line)
            
            if rule_id == "legacy_raw_input":
                if re.search(r"\braw_input\s*\(", scan) and "def " not in scan:
                    issues.append({"rule_id": rule_id, "severity": severity, "message": message, "line": i})
        
            elif rule_id == "security_eval":
                if re.search(r"\beval\s*\(", scan):
                    issues.append({"rule_id": rule_id, "severity": severity, "message": message, "line": i})

            elif rule_id == "security_exec":
                if re.search(r"\bexec\s*\(", scan):
                    issues.append({"rule_id": rule_id, "severity": severity, "message": message, "line": i})
                    
            elif rule_id == "security_os_system":
                if re.search(r"\bos\s*\.\s*system\s*\(", scan):
                    issues.append({"rule_id": rule_id, "severity": severity, "message": message, "line": i})

            elif rule_id == "legacy_print":
                py2_print_re = re.compile(r"^\s*print\s+['\"a-zA-Z0-9]")
                if py2_print_re.match(scan):
                    issues.append({"rule_id": rule_id, "severity": severity, "message": message, "line": i})

    return issues
