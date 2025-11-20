# Logical Architecture - Actor & Responsibility Flow

**Version**: 2.0.1
**Date**: 2025-11-20
**Purpose**: High-level architecture showing actors, responsibilities, and data flow from user input to final output

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

## Complete End-to-End Flow: OSFI E-23 Assessment

### Step-by-Step Journey from User Input to Word Document

```
┌────────────────────────────────────────────────────────────────────────┐
│ STEP 1: User Initiates                                                 │
└────────────────────────────────────────────────────────────────────────┘
    USER: "I need to assess my credit risk model for OSFI E-23"
      ↓
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - Parses natural language intent           │
    │ - Recognizes "OSFI E-23" keyword           │
    │ - Decides to call get_server_introduction  │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ MCP PROTOCOL:                              │
    │ - JSON-RPC call over stdio                 │
    │ - Tool: get_server_introduction            │
    │ - Parameters: {user_context: "OSFI E-23"} │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ PYTHON - introduction_builder.py:          │
    │ - framework_detector.detect() finds "osfi" │
    │ - Builds 6-step workflow structure         │
    │ - Returns JSON with workflow steps         │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - Receives JSON response                   │
    │ - Formats as readable workflow             │
    │ - Asks: "Proceed with OSFI E-23?"         │
    │ - WAITS for user confirmation              │
    └────────────────────────────────────────────┘
      ↓
    USER: "Yes, proceed"

┌────────────────────────────────────────────────────────────────────────┐
│ STEP 2: Project Description Validation (Step 1 of 6)                  │
└────────────────────────────────────────────────────────────────────────┘
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - Calls validate_project_description       │
    │ - Passes project description from chat     │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ PYTHON - description_validator.py:         │
    │ - Counts words (Python len())              │
    │ - Checks for 6 content areas (keyword match│
    │ - Calculates coverage % (pure math)        │
    │ - Returns: pass/fail + recommendations     │
    └────────────────────────────────────────────┘
      ↓
    CLAUDE: Presents validation results

┌────────────────────────────────────────────────────────────────────────┐
│ STEP 3: Risk Assessment (Step 2 of 6)                                 │
└────────────────────────────────────────────────────────────────────────┘
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - Calls assess_model_risk                  │
    │ - Passes: project_name, description        │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ PYTHON - osfi_e23_processor.py:            │
    │                                            │
    │ Line 266-283: KEYWORD MATCHING (PURE PYTHON)
    │ ┌──────────────────────────────────────┐  │
    │ │ description_lower = desc.lower()     │  │
    │ │                                      │  │
    │ │ 'high_volume': any(                 │  │
    │ │   term in description_lower         │  │
    │ │   for term in ['millions',          │  │
    │ │                'thousands',          │  │
    │ │                'large scale']       │  │
    │ │ )                                   │  │
    │ │                                      │  │
    │ │ 'ai_ml_usage': any(                 │  │
    │ │   term in description_lower         │  │
    │ │   for term in ['ai', 'ml',          │  │
    │ │                'neural network']    │  │
    │ │ )                                   │  │
    │ └──────────────────────────────────────┘  │
    │                                            │
    │ Line 286-287: SCORE CALCULATION            │
    │ ┌──────────────────────────────────────┐  │
    │ │ quant_score = sum(...) * 10          │  │
    │ │ qual_score = sum(...) * 8            │  │
    │ └──────────────────────────────────────┘  │
    │                                            │
    │ Line 308-318: RISK AMPLIFICATION           │
    │ ┌──────────────────────────────────────┐  │
    │ │ if financial_impact + ai_ml_usage:   │  │
    │ │     multiplier += 0.3  # 30% boost   │  │
    │ └──────────────────────────────────────┘  │
    │                                            │
    │ Line 321: FINAL SCORE                      │
    │ ┌──────────────────────────────────────┐  │
    │ │ return min(final_score, 100)         │  │
    │ └──────────────────────────────────────┘  │
    │                                            │
    │ Returns: {                                 │
    │   risk_score: 68,                          │
    │   risk_level: "High",                      │
    │   quantitative_indicators: {...},          │
    │   qualitative_indicators: {...},           │
    │   amplification_applied: 1.3               │
    │ }                                          │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - Receives JSON with risk_score: 68        │
    │ - Formats as: "Risk Level: High (68/100)"  │
    │ - Adds interpretation: "This indicates..." │
    │ - Recommends next steps                    │
    └────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│ STEPS 4-5: Lifecycle, Risk Rating, Compliance Framework               │
└────────────────────────────────────────────────────────────────────────┘
    [Similar flow: Claude calls tools → Python calculates → Claude presents]

┌────────────────────────────────────────────────────────────────────────┐
│ STEP 6: Document Generation (Final Step)                              │
└────────────────────────────────────────────────────────────────────────┘
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - Calls export_e23_report                  │
    │ - Passes all previous assessment results   │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ PYTHON - osfi_e23_report_generators.py:    │
    │                                            │
    │ 1. Extract data from results:              │
    │    - risk_level: "High"                    │
    │    - risk_score: 68                        │
    │    - detected_factors: [...]               │
    │                                            │
    │ 2. Use python-docx library:                │
    │    doc = Document()                        │
    │    doc.add_heading("OSFI E-23 Report")     │
    │    doc.add_paragraph("Risk Level: High")   │
    │                                            │
    │ 3. Add compliance checklist:               │
    │    for requirement in requirements:        │
    │        doc.add_paragraph(f"☐ {req}")       │
    │                                            │
    │ 4. Save file:                              │
    │    doc.save("OSFI_E23_Report.docx")        │
    │                                            │
    │ Returns: {                                 │
    │   success: true,                           │
    │   file_path: "/path/to/report.docx"        │
    │ }                                          │
    └────────────────────────────────────────────┘
      ↓
    ┌────────────────────────────────────────────┐
    │ CLAUDE (LLM):                              │
    │ - "✅ Report generated successfully!"      │
    │ - "File: OSFI_E23_Report.docx"            │
    │ - "Next steps: Review with compliance..."  │
    └────────────────────────────────────────────┘
      ↓
    USER: Downloads and reviews Word document
```

---

## Key Architectural Insights

### 1. **MCP is Just a Communication Protocol**

```
MCP Protocol = JSON-RPC over stdio

Example MCP Call:
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "assess_model_risk",
    "arguments": {
      "projectName": "Credit Model",
      "projectDescription": "ML model using neural networks..."
    }
  }
}

MCP Response:
{
  "content": [{
    "type": "text",
    "text": "{\"risk_score\": 68, \"risk_level\": \"High\"}"
  }]
}
```

**That's it!** MCP just delivers function calls and returns results. All the work is Python.

### 2. **Where the "Intelligence" Lives**

| Task | Actor | Location |
|------|-------|----------|
| Understanding "assess my model" | Claude (LLM) | Claude's neural network |
| Deciding which tool to call | Claude (LLM) | Claude's reasoning |
| Finding keyword "neural network" | PYTHON | `any(term in desc for term in [...])` |
| Calculating risk score | PYTHON | `sum(...) * 10` |
| Applying amplification | PYTHON | `multiplier += 0.3` |
| Determining "High" vs "Critical" | PYTHON | `if score >= 51: return "High"` |
| Formatting results nicely | Claude (LLM) | Claude's language generation |
| Making recommendations | Claude (LLM) | Claude's reasoning |

### 3. **The Python Code is 100% Portable**

You could remove Claude entirely and use the Python code as:

```python
# Direct Python usage (NO LLM)
from osfi_e23_processor import OSFIE23Processor

processor = OSFIE23Processor()
result = processor.assess_model_risk(
    project_name="Credit Model",
    project_description="Neural network for loan approvals..."
)

print(result['risk_level'])  # "High"
print(result['risk_score'])  # 68
```

**Everything works the same!** The MCP layer just makes it conversational.

---

## Alternative Output Formats (e.g., Jira Tickets)

### Current Flow (Word Document)
```
Python Assessment → export_e23_report() → Word Document
```

### Alternative Flow (Jira Ticket)
```
Python Assessment → create_jira_ticket() → Jira API → Ticket Created
```

**Nothing changes in the assessment logic!** Only the final export step changes.

---

## Summary: Who Does What

```
┌──────────────────────────────────────────────────────────────┐
│                    RESPONSIBILITY MATRIX                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  USER:           Provides input, makes decisions             │
│  CLAUDE (LLM):   Conversation UI, orchestration, formatting  │
│  PYTHON:         100% of actual work (calculations, rules)   │
│  MCP:            Just the communication pipe                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**The regulatory intelligence is 100% Python.** Claude is a conversational wrapper.
