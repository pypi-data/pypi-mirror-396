import argparse
import sys
import os
from typing import Optional
from .scanner import Scanner
from .ai_handler import AIHandler
from .llm_provider import LLMConfigError

# Используем Optional вместо |, чтобы поддерживать Python 3.9
def _set_env_strict(key: str, value: Optional[str]) -> None:
    """
    Safely sets environment variable from config/CLI.
    Raises LLMConfigError if there is a conflict with existing env var.
    """
    if value is None:
        return
    v = str(value).strip()
    if v == "" or v.lower() == "auto":
        return

    existing = os.getenv(key)
    if existing and existing != v:
        raise LLMConfigError(
            f"CONFIG CONFLICT: {key} already set to {existing!r}, "
            f"but CLI/Config requests {v!r}. "
            f"Please unset the environment variable or match the CLI argument."
        )

    if not existing:
        os.environ[key] = v

def main():
    parser = argparse.ArgumentParser(description="Refactoring Agent CLI")
    parser.add_argument("path", nargs="?", default=".", help="Path to check")
    parser.add_argument("--exclude", action="append", help="Exclude paths")
    parser.add_argument("--no-default-excludes", action="store_true")
    parser.add_argument("--ai-fix", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    
    parser.add_argument("--ai-provider", default=None, help="Override AI provider")
    parser.add_argument("--ai-model", default=None, help="Override AI model")
    
    args = parser.parse_args()

    try:
        _set_env_strict("RA_LLM_PROVIDER", args.ai_provider)
        _set_env_strict("RA_LLM_MODEL", args.ai_model)
    except LLMConfigError as e:
        print(f"[CRITICAL CONFIG ERROR] {e}")
        sys.exit(1)

    excludes = [
        ".git", ".venv", "venv", "env", "__pycache__", ".pytest_cache", 
        ".mypy_cache", ".ruff_cache", "node_modules", ".idea", ".vscode"
    ]
    if not args.no_default_excludes:
        if args.exclude:
            excludes.extend(args.exclude)
    else:
        if args.exclude:
            excludes = args.exclude

    scanner = Scanner(root_path=args.path, exclude_patterns=excludes)
    try:
        scanner.run()
        
        if args.ai_fix:
            ai = AIHandler(dry_run=args.dry_run)
            ai.process_issues(scanner.issues)
            
    except Exception as e:
        if "AMBIGUOUS CONFIG" in str(e) or "CONFIG CONFLICT" in str(e):
             print(f"\n[SECURITY STOP] {e}")
             sys.exit(1)
        raise e

if __name__ == "__main__":
    main()
