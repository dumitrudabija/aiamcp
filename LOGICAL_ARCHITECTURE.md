# Logical Architecture - Actor & Responsibility Flow

**Version**: 2.3.0
**Date**: 2025-11-21
**Purpose**: High-level architecture showing actors, responsibilities, and data flow from user input to final output

**Key Update (v2.3.0)**: Clarified session persistence architecture - Python maintains ALL workflow state through auto-sessions; Claude does NOT pass data between steps

---

## Architecture Overview

This system has **3 distinct actors** with clear separation of responsibilities:

```
┌─────────────┐         ┌─────────────┐         ┌──────────────────┐
│    USER     │ ←──────→│   CLAUDE    │ ←─MCP──→│  PYTHON LOGIC    │
│  (Human)    │  Chat   │    (LLM)    │ JSON-RPC│  (Regulatory)    │
└─────────────┘         └─────────────┘         └──────────────────┘
     │                        │                         │
     │                        │                         │
     ▼                        ▼                         ▼
Provides input       Orchestrates flow          Does all work
Confirms actions     Presents results           Calculates scores
Reviews output       Asks questions             Applies regulations
```

---

## Actor Responsibilities

### USER (Human)
- ✅ Provides project description
- ✅ Confirms workflow execution ("yes, proceed")
- ✅ Reviews assessment results
- ✅ Makes final compliance decisions
- ❌ Does NOT do any calculations
- ❌ Does NOT interpret regulations

### CLAUDE (LLM)
- ✅ Understands natural language intent
- ✅ Selects appropriate tools to call
- ✅ Orchestrates multi-step workflows
- ✅ Formats JSON responses into readable text
- ✅ Provides recommendations based on results
- ❌ Does NOT calculate risk scores
- ❌ Does NOT determine compliance levels
- ❌ Does NOT modify official regulatory logic

### PYTHON LOGIC (This Codebase)
- ✅ ALL regulatory calculations
- ✅ ALL keyword matching (pure string operations)
- ✅ ALL risk scoring formulas
- ✅ ALL compliance determinations
- ✅ ALL official framework logic
- ✅ Document generation (Word files)
- ❌ Does NOT understand natural language
- ❌ Does NOT make strategic recommendations

---

## Session Persistence & Data Flow Architecture

### Automatic State Management

**Critical Architectural Feature:** Python maintains ALL workflow state automatically. Claude does NOT pass data between steps.

```
┌─────────────────────────────────────────────────────────────┐
│                    SESSION PERSISTENCE                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  When Claude calls ANY OSFI E-23 tool:                     │
│                                                             │
│  1. Python auto-creates/retrieves session                  │
│  2. Python stores tool result in session["tool_results"]   │
│  3. Later tools auto-retrieve from session state           │
│                                                             │
│  Example:                                                   │
│  - Step 2: assess_model_risk                               │
│    Python stores: session["tool_results"]["assess_model_risk"] │
│                                                             │
│  - Step 4: create_compliance_framework                      │
│    Python retrieves: session["tool_results"]["assess_model_risk"] │
│                                                             │
│  - Step 5: export_e23_report                               │
│    Python auto-injects: session["tool_results"]["assess_model_risk"] │
│                                                             │
│  Claude never passes data - just calls tools in sequence   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight:** The workflow engine in Python handles ALL data persistence. Claude's role is purely conversational orchestration - understanding user intent and selecting which tools to call. Data flows through Python's session state, not through Claude.

---

## Complete End-to-End Flow: OSFI E-23 Assessment

### Step-by-Step Journey from User Input to Word Document

```
┌────────────────────────────────────────────────────────────────────────┐
│ INITIATION: User Starts Assessment                                     │
└────────────────────────────────────────────────────────────────────────┘
    USER: "I need to assess my credit risk model for OSFI E-23"
      ↓
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - Understands user wants OSFI E-23 help   │
    │ - Recognizes regulatory framework keyword │
    │ - Requests workflow introduction           │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ PYTHON LOGIC:                              │
    │ - Detects "OSFI E-23" context              │
    │ - Builds 5-step workflow structure         │
    │ - Returns complete workflow description    │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - Presents 5-step workflow to user         │
    │ - Explains each step's purpose             │
    │ - Asks: "Ready to proceed?"                │
    │ - WAITS for user confirmation              │
    └────────────────────────────────────────────┘
      ↓
    USER: "Yes, proceed"

┌────────────────────────────────────────────────────────────────────────┐
│ STEP 1 of 5: Validate Project Description                             │
└────────────────────────────────────────────────────────────────────────┘
    Purpose: Ensure description has sufficient detail for accurate assessment

    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - Extracts project description from chat   │
    │ - Requests validation check                │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ PYTHON LOGIC:                              │
    │ - Counts words and checks length           │
    │ - Scans for 6 content areas:               │
    │   • System/Technology description          │
    │   • Business purpose                       │
    │   • Data sources                           │
    │   • Impact scope                           │
    │   • Decision process                       │
    │   • Technical architecture                 │
    │ - Calculates coverage percentage           │
    │ - Returns: PASS/FAIL + guidance            │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - "✅ Step 1 Complete: Description Valid" │
    │ - Shows coverage: "5/6 areas covered"     │
    │ - Suggests improvements if needed          │
    │ - Announces: "Moving to Step 2..."        │
    └────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ STEP 2 of 5: Comprehensive Risk Assessment                            │
└────────────────────────────────────────────────────────────────────────┘
    Purpose: Calculate model risk level using OSFI E-23 methodology

    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - Requests comprehensive risk analysis     │
    │ - Provides project details                 │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ PYTHON LOGIC:                              │
    │                                            │
    │ 1. KEYWORD DETECTION                       │
    │    Scans description for risk indicators:  │
    │    - Quantitative: volume, financial,      │
    │      customer-facing, revenue-critical     │
    │    - Qualitative: AI/ML, complexity,       │
    │      autonomy, explainability              │
    │                                            │
    │ 2. SCORE CALCULATION                       │
    │    - Quantitative factors: 10 pts each     │
    │    - Qualitative factors: 8 pts each       │
    │    - Base score computed                   │
    │                                            │
    │ 3. RISK AMPLIFICATION                      │
    │    Checks dangerous combinations:          │
    │    - AI + Financial decisions: +30%        │
    │    - Autonomous + Customer-facing: +20%    │
    │    - Black-box + Regulatory: +25%          │
    │    - Third-party + Critical: +15%          │
    │                                            │
    │ 4. DETAILED BREAKDOWN                      │
    │    - Individual factor analysis            │
    │    - Risk interaction identification       │
    │    - Final risk level determination        │
    │                                            │
    │ 5. SESSION STORAGE                         │
    │    - Stores complete result in session     │
    │    - Key: session["tool_results"]["assess_model_risk"] │
    │    - Available to all subsequent steps     │
    │                                            │
    │ Returns:                                   │
    │   - Risk Score: 0-100                      │
    │   - Risk Level: Low/Med/High/Critical      │
    │   - Detected factors list                  │
    │   - Amplification details                  │
    │   - Factor-by-factor breakdown             │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - "✅ Step 2 Complete: Risk Assessed"     │
    │ - Presents: "Risk Level: High (68/100)"   │
    │ - Explains key risk drivers                │
    │ - Shows amplification reasons              │
    │ - Recommends governance approach           │
    │ - Announces: "Moving to Step 3..."        │
    └────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ STEP 3 of 5: Lifecycle Coverage Assessment                            │
└────────────────────────────────────────────────────────────────────────┘
    Purpose: Evaluate coverage of OSFI lifecycle requirements for current stage

    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - Requests lifecycle compliance check      │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ PYTHON LOGIC:                              │
    │ - Detects current lifecycle stage:         │
    │   Design/Review/Deployment/                │
    │   Monitoring/Decommission                  │
    │ - Checks for 3 stage-specific elements     │
    │ - Calculates coverage: 0/33/67/100%        │
    │ - Identifies gaps                          │
    │                                            │
    │ - Stores result in session state:          │
    │   session["tool_results"]["evaluate_lifecycle_compliance"] │
    │                                            │
    │ Returns:                                   │
    │   - Current stage detected                 │
    │   - Coverage percentage                    │
    │   - Elements present vs missing            │
    │   - Gap recommendations                    │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - "✅ Step 3 Complete: Lifecycle Checked" │
    │ - Shows: "Design Stage: 67% coverage"     │
    │ - Explains what's documented               │
    │ - Highlights missing elements              │
    │ - Announces: "Moving to Step 4..."        │
    └────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ STEP 4 of 5: Compliance Framework Creation                            │
└────────────────────────────────────────────────────────────────────────┘
    Purpose: Generate governance requirements and compliance checklist

    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - Requests compliance framework            │
    │ - (No data passing needed)                 │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ PYTHON LOGIC:                              │
    │ - Retrieves risk level from Step 2 session │
    │ - Retrieves stage from Step 3 session      │
    │                                            │
    │ - Creates risk-based governance:           │
    │   • Approval authorities                   │
    │   • Monitoring frequency                   │
    │   • Documentation requirements             │
    │                                            │
    │ - Builds stage-specific checklist:         │
    │   • 3 OSFI elements for current stage      │
    │   • Requirements per element               │
    │   • Deliverables list                      │
    │   • Risk-level specific items              │
    │                                            │
    │ - Stores result in session state:          │
    │   session["tool_results"]["create_compliance_framework"] │
    │                                            │
    │ Returns:                                   │
    │   - Governance structure                   │
    │   - Complete compliance checklist          │
    │   - Monitoring framework                   │
    │   - Documentation standards                │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - "✅ Step 4 Complete: Framework Ready"   │
    │ - Shows governance requirements            │
    │ - Presents compliance checklist            │
    │ - Explains risk-based controls             │
    │ - Announces: "Moving to Step 5..."        │
    └────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ STEP 5 of 5: Report Generation                                        │
└────────────────────────────────────────────────────────────────────────┘
    Purpose: Create professional Word document with all assessment results

    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - Requests report generation               │
    │ - (No data passing needed)                 │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ PYTHON LOGIC:                              │
    │                                            │
    │ 1. AUTO-INJECTION FROM SESSION             │
    │    - Checks if assessment_results passed   │
    │    - If missing: auto-injects from         │
    │      session["tool_results"]["assess_model_risk"] │
    │    - Retrieves Step 3 data if available    │
    │    - Retrieves Step 4 data if available    │
    │                                            │
    │ 2. DOCUMENT GENERATION                     │
    │    - Generates Word document with:         │
    │   • Executive Summary                      │
    │   • Risk Rating Methodology                │
    │   • Lifecycle Coverage Assessment          │
    │   • Stage-Specific Compliance Checklist    │
    │   • Governance Structure (v2.2.9):         │
    │     - 5.1 Roles and Responsibilities       │
    │     - 5.2 Documentation Requirements       │
    │     - 5.3 Review and Approval Procedures   │
    │   • Monitoring Framework                   │
    │   • OSFI E-23 Principles (Annex)           │
    │                                            │
    │ - Applies stage-specific filtering         │
    │ - Adds professional validation warnings    │
    │ - Saves to file system                     │
    │                                            │
    │ Returns:                                   │
    │   - Success status                         │
    │   - File path                              │
    │   - File size                              │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - "✅ Step 5 Complete: Report Generated!" │
    │ - Shows file location                      │
    │ - Summarizes assessment outcome            │
    │ - Recommends next steps:                   │
    │   • Professional review required           │
    │   • Governance approval needed             │
    │   • Implementation planning                │
    └────────────────────────────────────────────┘
      ↓
    USER: Downloads and reviews Word document
```

---

## Key Architectural Insights

### 1. **Communication Protocol**

The Model Context Protocol (MCP) acts as a simple communication bridge:
- Claude sends requests to Python tools
- Python executes regulatory logic and returns results
- Claude formats results into readable conversation

**That's it!** The protocol just enables conversation. All regulatory work happens in Python.

### 2. **Where the "Intelligence" Lives**

| Task | Actor | Why This Actor |
|------|-------|----------------|
| Understanding natural language | Claude (LLM) | Language comprehension |
| Deciding workflow steps | Claude (LLM) | Conversation orchestration |
| Keyword detection | PYTHON | String matching logic |
| Risk score calculation | PYTHON | Mathematical formulas |
| Regulatory rule application | PYTHON | OSFI E-23 requirements |
| Compliance determination | PYTHON | Official framework logic |
| Result presentation | Claude (LLM) | Natural language formatting |
| Strategic recommendations | Claude (LLM) | Contextual reasoning |

### 3. **Session Persistence & Data Flow**

**Critical Insight:** Python maintains ALL workflow state. Claude does NOT pass data between steps.

**How it works:**
1. **Auto-session creation**: When Claude calls any OSFI tool, Python automatically creates or retrieves a session
2. **Automatic storage**: Every tool result is stored in `session["tool_results"][tool_name]`
3. **Auto-injection**: Export tools automatically retrieve previous results from session state
4. **No data passing**: Claude just calls tools in sequence - Python handles all data persistence

**Example data flow:**
```
Claude: "Run assess_model_risk"
  → Python: Stores result in session["tool_results"]["assess_model_risk"]

Claude: "Run create_compliance_framework"
  → Python: Retrieves risk data from session["tool_results"]["assess_model_risk"]
  → Python: Creates framework using retrieved data
  → Python: Stores result in session["tool_results"]["create_compliance_framework"]

Claude: "Run export_e23_report"
  → Python: Auto-injects session["tool_results"]["assess_model_risk"]
  → Python: Optionally uses session["tool_results"]["create_compliance_framework"]
  → Python: Generates Word document
```

**Session lifetime:** 2 hours from last access

### 4. **Python Logic is Standalone**

The regulatory logic doesn't depend on Claude:
- Can be called directly from Python scripts
- Can be integrated into other systems
- Can export to different formats (Word, Jira, databases)
- Claude just makes it conversational

**Core principle:** Regulatory logic is separate from user interface.

---

## Alternative Output Formats

The 5-step assessment workflow is output-agnostic:

**Current Implementation: Word Document**
- Steps 1-4: Same assessment logic
- Step 5: Generate Word document

**Alternative: Jira Tickets**
- Steps 1-4: Same assessment logic
- Step 5: Create Jira tickets via API

**Alternative: Database**
- Steps 1-4: Same assessment logic
- Step 5: Insert records into database

**Key Point:** Regulatory assessment logic is independent of output format.

---

## Summary: Who Does What

```
┌──────────────────────────────────────────────────────────────┐
│                    RESPONSIBILITY MATRIX                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  USER:           Provides input, makes decisions             │
│  CLAUDE (LLM):   Conversation UI, tool selection, formatting │
│  PYTHON:         100% of work (calculations, rules, state)   │
│  MCP:            Communication pipe only                     │
│                                                              │
│  DATA FLOW:      All through Python session state            │
│  PERSISTENCE:    Python auto-sessions (2-hour lifetime)      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**The regulatory intelligence is 100% Python.** Claude is a conversational wrapper that orchestrates tool calls - it does NOT pass data between steps. Python maintains all workflow state through automatic session management.
