import os
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from .llm_client import LLMClient

class AIHandler:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.console = Console()
        self.client = LLMClient()

    def process_issues(self, issues: List[Dict[str, Any]]):
        """
        Process found issues and attempt to fix them using LLM.
        """
        if not issues:
            self.console.print("[green][OK] Clean! No issues found.[/green]")
            return

        self.console.print(f"\n[bold yellow][AUTO-FIX] Starting Remediation...[/bold yellow]")
        
        # Display Provider Banner
        provider = os.getenv("RA_LLM_PROVIDER", "openai").upper()
        if provider == "OPENAI" and not os.getenv("OPENAI_API_KEY") and not os.getenv("RA_OPENAI_API_KEY"):
             provider = "OPENAI (Missing Key)"
        
        model = os.getenv("RA_LLM_MODEL", "None")
        
        self.console.print(Panel(
            f"☁️  LLM Provider: {provider}\nModel: {model}",
            title="AI Config",
            border_style="blue"
        ))

        for issue in issues:
            self.fix_issue(issue)

    def fix_issue(self, issue: Dict[str, Any]):
        file_path = issue["file"]
        self.console.print(f"\n👉 Processing [bold]{file_path}[/bold]...")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Construct a prompt for the LLM
            prompt = (
                f"Fix the following python code issue.\n"
                f"Issue Code: {issue['code']}\n"
                f"Message: {issue['message']}\n"
                f"Line: {issue['line']}\n"
                f"Full Content:\n```python\n{content}\n```\n"
                f"Return ONLY the fixed python code. No markdown, no explanations."
            )

            # Get fix from LLM
            fixed_content = self.client.get_completion(prompt)
            
            # Clean up response (strip markdown blocks if LLM adds them)
            fixed_content = fixed_content.replace("```python", "").replace("```", "").strip()

            if self.dry_run:
                self.show_diff(file_path, content, fixed_content)
                self.console.print("   [yellow]--dry-run enabled, changes NOT written.[/yellow]")
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(fixed_content)
                self.console.print("   [green]✔ Fix applied.[/green]")

        except Exception as e:
            self.console.print(f"   [red]Failed to fix: {e}[/red]")

    def show_diff(self, file_path: str, original: str, fixed: str):
        import difflib
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            fixed.splitlines(keepends=True),
            fromfile=file_path,
            tofile=file_path,
        )
        diff_text = "".join(diff)
        if diff_text:
             syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
             self.console.print(Panel(syntax, title=f"Diff: {file_path}", border_style="yellow"))
        else:
             self.console.print("   [dim]No changes generated.[/dim]")
