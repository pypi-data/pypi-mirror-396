import os
import ast
import fnmatch
from typing import List, Dict, Any

class Scanner:
    def __init__(self, root_path: str = ".", exclude_patterns: List[str] = None):
        self.root_path = root_path
        self.exclude_patterns = exclude_patterns or []
        self.issues = []

    def is_excluded(self, path: str) -> bool:
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
        return False

    def run(self):
        print(f"Found python files. Starting analysis...")
        for root, dirs, files in os.walk(self.root_path):
            # Exclude directories logic
            dirs[:] = [d for d in dirs if not self.is_excluded(os.path.join(root, d))]
            
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    if not self.is_excluded(full_path):
                        self.scan_file(full_path)

    def scan_file(self, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check for legacy raw_input (Regex/String check for simplicity on Python 3 running legacy code)
            if "raw_input(" in content:
                # Find line number roughly
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if "raw_input(" in line:
                         self.issues.append({
                            "file": file_path,
                            "line": i + 1,
                            "type": "MAJOR",
                            "code": "legacy_raw_input",
                            "message": "Legacy 'raw_input' detected. Use 'input()' instead."
                        })

            tree = ast.parse(content)
            self.check_ast(tree, file_path)

        except SyntaxError as e:
            self.issues.append({
                "file": file_path,
                "line": e.lineno or 1,
                "type": "CRITICAL",
                "code": "syntax_error",
                "message": f"Syntax Error: {e.msg}"
            })
        except Exception as e:
            # Skip errors for non-utf8 files etc
            pass

    def check_ast(self, tree: ast.AST, file_path: str):
        for node in ast.walk(tree):
            # Security checks
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id == 'eval':
                         self.issues.append({"file": file_path, "line": node.lineno, "type": "CRITICAL", "code": "security_eval", "message": "Security Risk: usage of eval() detected."})
                    elif node.func.id == 'exec':
                         self.issues.append({"file": file_path, "line": node.lineno, "type": "CRITICAL", "code": "security_exec", "message": "Security Risk: usage of exec() detected."})
                
                if isinstance(node.func, ast.Attribute):
                     if node.func.attr == 'system' and isinstance(node.func.value, ast.Name) and node.func.value.id == 'os':
                         self.issues.append({"file": file_path, "line": node.lineno, "type": "CRITICAL", "code": "security_os_system", "message": "Security Risk: usage of os.system() detected."})

