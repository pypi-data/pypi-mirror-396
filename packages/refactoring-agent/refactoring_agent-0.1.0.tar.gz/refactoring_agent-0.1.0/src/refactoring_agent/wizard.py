import ast
import os

class LegacyCodeVisitor(ast.NodeVisitor):
    def __init__(self, rules_config):
        self.issues = []
        self.rules = rules_config
        # Heuristics for sensitive variable names
        self.sensitive_vars = {"token", "password", "secret", "key", "code", "otp", "auth", "session", "csrf"}

    def _add_issue(self, node, rule_id):
        config = self.rules.get(rule_id, {})
        mode = config.get("mode", "warn")
        if mode == "ignore":
            return
        
        self.issues.append({
            "file": "unknown",  # Will be filled by scanner
            "line": getattr(node, "lineno", 0),
            "rule_id": rule_id,
            "message": config.get("message", f"Issue found: {rule_id}"),
            "severity": config.get("severity", "minor"),
            "mode": mode
        })

    def _is_call(self, node, module_name, func_names):
        """Helper to check if a call matches module.func or just func."""
        if not isinstance(node, ast.Call):
            return False
        
        target_funcs = [func_names] if isinstance(func_names, str) else func_names
        
        # Check explicit: module.func()
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == module_name:
                if node.func.attr in target_funcs:
                    return True
                    
        # Check direct: func() (assuming simple import)
        if isinstance(node.func, ast.Name):
            if node.func.id in target_funcs:
                return True
                
        return False

    def visit_Print(self, node):
        self._add_issue(node, "legacy_print")
        self.generic_visit(node)

    def visit_Call(self, node):
        # 1. raw_input
        if isinstance(node.func, ast.Name) and node.func.id == "raw_input":
            self._add_issue(node, "legacy_raw_input")

        # 2. eval / exec
        if isinstance(node.func, ast.Name):
            if node.func.id == "eval":
                self._add_issue(node, "security_eval")
            elif node.func.id == "exec":
                self._add_issue(node, "security_exec")

        # 3. os.system
        if self._is_call(node, "os", "system"):
            self._add_issue(node, "security_os_system")

        # 4. subprocess.Popen(..., shell=True)
        if self._is_call(node, "subprocess", ("Popen", "run", "call")):
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, (ast.Constant, ast.NameConstant)):
                    if kw.value.value is True:
                        self._add_issue(node, "security_subprocess_shell")

        # 5. pickle.load / pickle.loads
        if self._is_call(node, "pickle", ("load", "loads")):
            self._add_issue(node, "security_pickle_untrusted")

        self.generic_visit(node)

    def visit_Assign(self, node):
        # 6. Insecure Random for Secrets
        # Check: variable_name = random.choice(...)
        if isinstance(node.value, ast.Call) and self._is_call(node.value, "random", ("choice", "randint", "randrange", "random")):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    # Check if variable name looks sensitive (e.g. 'api_key', 'user_password')
                    name_lower = target.id.lower()
                    if any(s in name_lower for s in self.sensitive_vars):
                        self._add_issue(node.value, "security_insecure_random")
                        
        self.generic_visit(node)

class RefactoringWizard:
    def __init__(self, config=None):
        self.config = config or {}
        # Make sure we default to empty dict if None
        self.rules = self.config.get("rules", {}) if self.config else {}

    def scan_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            try:
                tree = ast.parse(content)
            except SyntaxError:
                return [{
                    "file": file_path,
                    "line": 1,
                    "rule_id": "syntax_error",
                    "message": "Syntax Error: Cannot parse file content.",
                    "severity": "critical",
                    "mode": "error"
                }]

            visitor = LegacyCodeVisitor(self.rules)
            visitor.visit(tree)
            
            # Enrich issues with filename
            for issue in visitor.issues:
                issue["file"] = file_path
                
            return visitor.issues
        except Exception as e:
            # Silently ignore read errors or return generic error
            return []
