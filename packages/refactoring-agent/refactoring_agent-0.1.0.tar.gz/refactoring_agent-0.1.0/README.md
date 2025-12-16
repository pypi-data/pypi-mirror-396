# 🛡️ Refactoring Agent
### Autonomous Technical Debt & Security Remediation Agent

Refactoring Agent is an open-source tool that autonomously scans your Python codebase for security vulnerabilities, legacy patterns, and technical debt. It uses LLMs (OpenAI or local Ollama) to **automatically propose and apply fixes**.

---

## 🚀 Features
- **Automated Security Audit:** Detects `os.system`, `eval()`, SQL injection patterns, and more.
- **AI-Powered Fixes:** Automatically rewrites vulnerable code using modern best practices (e.g., `subprocess` with robust error handling).
- **Dry-Run Mode:** Preview changes with a colored diff before applying them.
- **Local/Air-Gapped Mode:** Works fully offline using Ollama (Llama 3, Qwen 2.5).
- **Enterprise Dashboard:** Built-in GUI for visualizing vulnerabilities.

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/StasLee1982/refactoring-agent.git
cd refactoring-agent

# Install in editable mode
python -m pip install -e .

# (Optional) For the GUI dashboard and reporting
python -m pip install streamlit pandas rich
```


---

## CI policy: Security scan vs AI remediation

We intentionally separate CI into two workflows:

### 1) Security Scan (No-AI) — always-on, safe
- Runs on: `push`, `pull_request`
- No secrets required (safe on forks)
- Read-only behavior: detects issues and fails CI when needed
- Must never run `--ai-fix`

### 2) AI Remediation (Privileged) — controlled and reviewable
AI-based remediation requires secrets and is therefore restricted.

**Trigger policy**
- AI-fix runs only:
  - manually via `workflow_dispatch`
  - (optional) on `push` to `main` for *dry-run only* (no writes), if enabled
- AI-fix MUST NOT run on `pull_request` events (forks do not have secrets).

**Change policy (no bot pushes to main)**
- The workflow must never push directly into `main`.
- If changes are applied, the workflow creates a dedicated branch and opens a Pull Request.
- Human review is mandatory before merge (enforced by branch protection).

**Key/secret policy**
- Secrets are stored only in CI secret manager (e.g. GitHub Actions Secrets / Environments).
- Never put API keys inline in commands.

In short: the bot can prepare a draft, but a human must sign off.
## 🛡️ Security & Privacy (Strict Mode)

This tool implements a **Fail Closed** security policy to prevent accidental data leaks.

### 🚫 Ambiguity is Forbidden
The agent will **exit with an error** if the configuration is contradictory. It will never silently fall back to a cloud provider if you requested a local one.

### 🔒 Air-Gapped Mode (Ollama)
To run in a truly air-gapped environment, ensure no OpenAI keys are present in your environment variables.

**❌ Invalid Configuration (Will Crash):**
```bash
# Conflict! You asked for Ollama, but an OpenAI key is visible.
export RA_LLM_PROVIDER=ollama
export OPENAI_API_KEY=sk-...
