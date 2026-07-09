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
