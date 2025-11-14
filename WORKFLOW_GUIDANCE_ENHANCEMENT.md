# Workflow Guidance Enhancement (v1.15.0)

## Summary

Enhanced the MCP server's `get_server_introduction` tool and OSFI E-23 tool descriptions to provide explicit workflow sequences and stronger behavioral guidance. This ensures users see complete workflow information before assessment tools are called, and that all OSFI tools are executed in the correct sequence.

## Problem Statement

When users said "run this project description through OSFI framework", the MCP was:
1. Calling `get_server_introduction` correctly (but not showing its output)
2. Immediately proceeding to call `assess_model_risk`
3. Skipping the other 4 OSFI E-23 tools (evaluate_lifecycle_compliance, generate_risk_rating, create_compliance_framework, export_e23_report)

Users expected to see:
1. Complete introduction with the FULL 6-step OSFI E-23 workflow sequence
2. Option to run through ALL 6 steps, not just assess_model_risk
3. Clear visibility of what each step does

## Changes Implemented

### 1. Enhanced `get_server_introduction` Response (server.py:589-773)

Added new `framework_workflows` section with complete sequences:

#### OSFI E-23 Workflow (6 Steps)
```python
"osfi_e23_workflow": {
    "title": "🏦 OSFI E-23 Framework Complete Workflow",
    "sequence": [
        {"step": 1, "tool": "validate_project_description", ...},
        {"step": 2, "tool": "assess_model_risk", ...},
        {"step": 3, "tool": "evaluate_lifecycle_compliance", ...},
        {"step": 4, "tool": "generate_risk_rating", ...},
        {"step": 5, "tool": "create_compliance_framework", ...},
        {"step": 6, "tool": "export_e23_report", ...}
    ],
    "note": "All 6 steps provide comprehensive OSFI E-23 coverage. Minimum viable: steps 1-2 and 6."
}
```

#### AIA Workflow (5 Steps)
```python
"aia_workflow": {
    "title": "🇨🇦 AIA Framework Complete Workflow",
    "sequence": [
        {"step": 1, "tool": "validate_project_description", ...},
        {"step": 2, "tool": "functional_preview OR analyze_project_description", ...},
        {"step": 3, "tool": "get_questions", ...},
        {"step": 4, "tool": "assess_project", ...},
        {"step": 5, "tool": "export_assessment_report", ...}
    ]
}
```

### 2. Stronger Behavioral Directives (server.py:590-592)

Added explicit instructions to Claude Code:

```python
"assistant_directive": {
    "critical_instruction": "STOP AND PRESENT THIS INTRODUCTION FIRST. Do NOT call any other tools immediately after this...",
    "behavioral_requirement": "After presenting this introduction, you MUST ask the user which framework they want to use (AIA, OSFI E-23, or workflow-based approach) and WAIT for their response before proceeding with any assessment tools."
}
```

### 3. Enhanced Tool Descriptions

#### `get_server_introduction` (server.py:156-157)
- Added explicit trigger: "Says 'run through OSFI framework' or 'run through AIA'"
- Added warning: "⚠️ CALL THIS TOOL ALONE - Do NOT call other tools in the same response!"
- Added workflow preview in description itself
- Added wrong/correct flow examples

#### OSFI E-23 Tool Descriptions
Each tool now shows its position in the workflow:

- `validate_project_description`: "🔍 STEP 1 - FRAMEWORK READINESS VALIDATOR"
- `assess_model_risk`: "🏦 OSFI E-23 STEP 2 OF 6 - MODEL RISK ASSESSMENT"
- `evaluate_lifecycle_compliance`: "🏦 OSFI E-23 STEP 3 OF 6 - LIFECYCLE COMPLIANCE"
- `generate_risk_rating`: "🏦 OSFI E-23 STEP 4 OF 6 - RISK RATING DOCUMENTATION"
- `create_compliance_framework`: "🏦 OSFI E-23 STEP 5 OF 6 - COMPLIANCE FRAMEWORK"
- `export_e23_report`: "🏦 OSFI E-23 STEP 6 OF 6 - REPORT GENERATION"

Each description includes:
- Full workflow reference: "COMPLETE OSFI WORKFLOW: (1) validate → (2) assess_model_risk [YOU ARE HERE] → (3) evaluate → (4) generate → (5) create → (6) export"
- Explicit instruction: "When user says 'run through OSFI framework', you should execute ALL 6 steps in sequence"

### 4. User Choice Guidance (server.py:763-772)

Added explicit framework selection guidance:

```python
"next_steps_guidance": {
    "user_choice_required": "ASK THE USER: Which framework do you want to use?",
    "options": {
        "option_1": "🇨🇦 AIA Framework - For federal government automated decision systems",
        "option_2": "🏦 OSFI E-23 Framework - For financial institution models",
        "option_3": "🔄 Workflow Mode - For guided assessment with automatic progression",
        "option_4": "🇨🇦🏦 Both Frameworks - For AI systems in regulated financial institutions"
    },
    "after_user_choice": "Once user selects a framework, follow the appropriate workflow sequence shown above"
}
```

## Version Update

- Updated version from 1.14.0 → 1.15.0
- Updated in 3 locations:
  - server.py:50 (`self.server_info`)
  - server.py:596 (`server_introduction`)

## Testing

Created `test_workflow_guidance.py` to verify:
1. ✅ Assistant directive includes "STOP AND PRESENT THIS INTRODUCTION FIRST"
2. ✅ OSFI E-23 workflow includes all 6 steps in correct order
3. ✅ AIA workflow includes all 5 steps in correct order
4. ✅ Next steps guidance includes 4 framework options
5. ✅ All OSFI tool descriptions include step numbers
6. ✅ Tool descriptions reference complete workflow

All tests passed.

## Expected Behavior Changes

### Before (v1.14.0)
```
User: "Run this project through OSFI framework"
Claude: [Calls get_server_introduction AND assess_model_risk together]
Claude: [Shows only assess_model_risk output]
```

### After (v1.15.0)
```
User: "Run this project through OSFI framework"
Claude: [Calls ONLY get_server_introduction]
Claude: [Shows complete introduction with 6-step OSFI workflow]
Claude: "I can see you want to run through the OSFI E-23 framework.
        This involves 6 steps:
        1. validate_project_description
        2. assess_model_risk
        3. evaluate_lifecycle_compliance
        4. generate_risk_rating
        5. create_compliance_framework
        6. export_e23_report

        Would you like me to run through all 6 steps?"
User: "Yes, run through all 6 steps"
Claude: [Executes each step in sequence, showing output for each]
```

## Benefits

1. **Complete Workflow Visibility**: Users see the full 6-step OSFI E-23 workflow upfront
2. **Better Tool Sequencing**: Claude Code understands to call tools in order, not jump to assess_model_risk
3. **Clearer User Choice**: Users can choose to run complete workflow or specific steps
4. **Step Context**: Each tool description shows where it fits in the larger workflow
5. **Behavioral Guidance**: Stronger directives ensure introduction is presented first
6. **Framework Selection**: Clear presentation of all 4 framework options

## Files Modified

- `server.py`: Enhanced get_server_introduction response and tool descriptions
- `test_workflow_guidance.py`: New test file to verify workflow guidance

## Backward Compatibility

All changes are additive - existing functionality remains intact. The enhancements only add:
- More information in get_server_introduction response
- More explicit guidance in tool descriptions
- Behavioral directives for Claude Code

No breaking changes to:
- Tool interfaces
- Response formats
- Existing workflows
- API contracts

## Related Issues

This addresses the user feedback about:
- get_server_introduction output not being shown before other tools
- assess_model_risk being called alone instead of the full OSFI workflow
- Missing visibility into the complete OSFI E-23 tool sequence
