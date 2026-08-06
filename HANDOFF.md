# HANDOFF — AIA Assessment MCP Server

Everything needed to get this running on a new machine.

---

## What This Is

A Model Context Protocol (MCP) server that plugs into Claude Desktop and provides structured regulatory assessment tools for:

- **AIA** — Canada's Algorithmic Impact Assessment (Treasury Board Secretariat, 104 questions, 4-tier risk)
- **OSFI E-23** — Model Risk Management for federally regulated financial institutions (8 Risk Dimensions, 47 factors)

The server runs locally over stdio; Claude Desktop calls its tools the same way it calls any other MCP tool. No cloud dependency for the server itself.

Current version: **3.5.0**

---

## Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.8+ | Tested on 3.9.6 |
| Claude Desktop | claude.ai/download |
| pip | Comes with Python |
| Git | For cloning |

---

## Setup

### 1. Clone

```bash
git clone https://github.com/dumitrudabija/aiamcp.git
cd aiamcp
```

Clone wherever you like — just note the path, you'll need it for the Claude Desktop config below.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: `anthropic`, `requests`, `pyyaml`, `python-docx`.

### 3. Configure Claude Desktop

Edit Claude Desktop's config file to register the MCP server:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

Add (or merge) this block, replacing `<REPO_PATH>` with your actual clone directory:

```json
{
  "mcpServers": {
    "aia-assessment": {
      "command": "/usr/bin/python3",
      "args": ["<REPO_PATH>/server.py"],
      "env": {
        "PYTHONPATH": "<REPO_PATH>",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

Platform-specific template files are also committed at `config/claude_desktop_config_*.json` if you want a starting point.

> **Note on `command`:** Use `python3` (macOS/Linux) or `python` (Windows). On macOS, `/usr/bin/python3` is the system Python — if you installed Python via Homebrew or pyenv, use that path instead (e.g. `/opt/homebrew/bin/python3`).

### 4. Restart Claude Desktop

Fully quit and reopen. The server loads lazily — it only initializes when you first call a tool, so startup is instant.

---

## Verify It's Working

In a new Claude Desktop conversation, ask:

> "Call get_server_introduction"

You should get a structured response listing available frameworks and workflows. If you see a tool error or no tools appear in Claude's tool menu, see Troubleshooting below.

You can also run the validation script directly:

```bash
python scripts/validate_mcp.py
```

---

## Claude Code in VS Code (New Laptop)

This project is normally worked on via Claude Code, not just Claude Desktop. To get the same setup running:

### 1. Install VS Code
Download from https://code.visualstudio.com if not already installed.

### 2. Install the Claude Code CLI
Native installer (macOS/Linux):

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

This installs the `claude` binary (self-updating, no npm/Node required). Verify with:

```bash
claude doctor
```

### 3. Log in
```bash
claude
```
On first run it walks you through browser-based login (Claude.ai / Anthropic account). This is a one-time step per machine.

### 4. Connect it to VS Code
- Open the project folder in VS Code: `code ~/Projects/aia-assessment-mcp` (or File → Open Folder).
- Open the integrated terminal (`` Ctrl+` ``) and run `claude` from the project root.
- The first time you run `claude` inside a VS Code integrated terminal, it detects the IDE and offers to install the companion **Claude Code** VS Code extension — accept it. This adds inline diff viewing, file-change tracking, and lets you jump between the chat and the editor.
- If it doesn't prompt, install the "Claude Code" extension manually from the VS Code Marketplace (publisher: Anthropic) and reopen the integrated terminal.

### 5. Confirm it works
Inside the project directory, `claude` should start with the project's `CLAUDE.md` picked up automatically (you'll see it referenced in context). Try a trivial read-only ask (e.g. "what does this repo do?") to confirm it's reading the right files.

---

## Project Structure on a New Laptop (GitHub as Source of Truth)

Don't copy the `Projects/` folder over from the old machine — clone fresh from GitHub instead. The working tree accumulates local-only cruft (caches, generated reports, local permission grants) that shouldn't travel between machines, and a stale copy can silently diverge from what's actually pushed.

### Recommended layout
Keep the same convention already in use: one folder per repo directly under `~/Projects/`, e.g.:
```
~/Projects/
  aia-assessment-mcp/   ← this repo
  <other-repo>/
```

### Per-project setup on the new machine
1. `git clone https://github.com/dumitrudabija/aiamcp.git ~/Projects/aia-assessment-mcp`
2. Authenticate to GitHub when prompted on first push/pull — this repo uses an HTTPS remote (not SSH), so you'll need either a Personal Access Token (used as the password when Git/macOS Keychain prompts) or `gh auth login` if the GitHub CLI is installed. Do this once; the OS credential manager remembers it after.
3. `pip install -r requirements.txt`
4. Follow the "Setup" section above to register the MCP server with Claude Desktop, and the "Claude Code in VS Code" section above for the CLI/editor.

### What does NOT come over automatically (by design)
- **`.claude/settings.local.json`** (per-project tool permission grants) — excluded from git by a **global** gitignore rule (`~/.config/git/ignore` → `**/.claude/settings.local.json`), not the repo's own `.gitignore`. On the new laptop you need to recreate that global ignore rule yourself (or Claude Code will offer to add permissions again as you use it — either way, expect to re-approve tool permissions from scratch).
- **Claude Code's cross-session memory** (`~/.claude/projects/.../memory/`) — local to the machine, rebuilds over time as you work; see the "Not in git (local only)" note further down this doc.
- Generated output folders (`AIA_Assessments/`, `OSFI_E23_Assessments/`), `backup_v2/`, `__pycache__/`, etc. — all gitignored, regenerated as needed.

Net effect: GitHub has everything required to reproduce a working repo; machine-local state (permissions, memory, caches) is expected to be empty on day one and rebuild naturally.

---

## What Is and Isn't in Git

**In git (everything you need):**
- All Python source files
- `data/survey-enfr.json` — official bilingual AIA questionnaire (never modify)
- `config/config.json` — scoring thresholds
- `config/extraction_prompts.yaml` — tunable OSFI extraction prompt templates
- `requirements.txt`
- Platform config templates under `config/`

**Not in git (by design):**
- `AIA_Assessments/` — generated Word documents from past assessments (gitignored)
- `OSFI_E23_Assessments/` — same
- `backup_v2/` — old module backups (gitignored)
- In-memory session state — lost on every server restart (expected; 2-hour TTL during a session)

**Not in git (local only):**
- `~/.claude/projects/.../memory/` — Claude Code's cross-session memory about this project. Not critical; Claude Code will rebuild it over time. Contains context like architecture notes, workflow summaries, and environment quirks.

---

## Troubleshooting

### Tools don't appear in Claude Desktop

1. Check the config file path and JSON syntax (trailing commas break JSON).
2. Check the Python path — run `which python3` in terminal and use that exact path.
3. Run `python <REPO_PATH>/server.py` directly in a terminal to see if it starts without errors.

### Tool calls hang forever ("thinking...")

Most likely cause on a corporate machine: **SSL inspection proxy** (e.g. Netskope, Zscaler) intercepting `api.anthropic.com`. Symptoms: small plain-text chats work, but tool calls with larger payloads never return.

Fix: request an IT SSL bypass for `claude.ai`, `api.anthropic.com`, `assets-proxy.anthropic.com`, `statsig.anthropic.com`.

### "Always Allow" grants reset

If Claude Desktop's IndexedDB is cleared (can happen during troubleshooting), all previously granted tool permissions reset. You'll need to re-grant them.

### python-docx not found (Word export fails)

If Word export errors, python-docx may not be installed in the Python environment Claude Desktop is using:

```bash
/usr/bin/python3 -m pip install python-docx
```

Or use whichever Python path you configured in the Claude Desktop config.

---

## Key Files for Orientation

| File | Purpose |
|---|---|
| `server.py` | Thin MCP orchestration layer; routes tool calls to modules |
| `aia_processor.py` | AIA question extraction and scoring |
| `osfi_e23_processor.py` | Governance requirement / compliance recommendation generation |
| `osfi_e23_risk_dimensions.py` | 8 Risk Dimensions, 47 factors definition |
| `risk_dimension_extraction.py` | AI-assisted extraction + deterministic scoring |
| `model_type_classification.py` | Model type (Level 1-5) + delivery model classification via deterministic capability-evidence checks |
| `conditional_modules.py` | 4 Capability Evidence Packs (Knowledge Access, Action Execution, Autonomy, Vendor/Platform) |
| `osfi_e23_workflow.py` | 5-step OSFI E-23 assessment orchestration (classification → packs → 47-question scoring → risk level → required actions) |
| `osfi_e23_report_generators.py` | OSFI E-23 report generation (3 sections + Annex A-E) - presentation layer only |
| `osfi_e23_structure.py` | Official OSFI Principles/Outcomes/lifecycle definitions + the configurable governance matrix |
| `workflow_engine.py` | Session state, auto-sequencing, dependency validation |
| `config/extraction_prompts.yaml` | Tunable prompt templates (edit to adjust extraction behavior) |
| `data/survey-enfr.json` | Official AIA questionnaire — do not modify |
| `CLAUDE.md` | Full architecture reference for Claude Code sessions |
| `DEVELOPER_GUIDE.md` | Deeper development notes |

---

## Assessment Workflow Reference

### OSFI E-23 (3 steps)
1. `validate_project_description` — gates entry, checks 6 content areas
2. `assess_model_risk` — two-phase: MCP returns extraction prompt → Claude extracts 47 factors → calls back with values → deterministic scoring
3. `export_e23_report` — Word doc; retrieves data from server-side session automatically (no need to pass results)

### AIA (5 steps)
1. `validate_project_description`
2. `analyze_project_description`
3. `get_questions`
4. `assess_project`
5. `export_assessment_report`

Always call `get_server_introduction` first — it's enforced by the workflow and sets the context for the session.

---

## Git Remote

```
https://github.com/dumitrudabija/aiamcp.git
```
