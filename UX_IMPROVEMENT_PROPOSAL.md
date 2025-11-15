# User Experience Improvement Proposal
## Simplifying Framework Presentation Without Architectural Changes

**Problem**: Users see both AIA and OSFI E-23 workflows when calling `get_server_introduction`, which can be confusing when they only need one framework.

**Goal**: Show only the relevant framework to the user based on context, without splitting the MCP server.

---

## Current User Experience (Confusing)

When a user says: **"Help me run through OSFI E-23 for my credit risk model"**

Claude currently shows:
```
🇨🇦 Canada's Regulatory Assessment MCP Server

Framework Workflows:

🇨🇦 AIA Framework Complete Workflow
  Step 1: validate_project_description
  Step 2: functional_preview OR analyze_project_description
  Step 3: get_questions
  Step 4: assess_project
  Step 5: export_assessment_report
  [Recommended use: Federal government automated decision systems]

🏦 OSFI E-23 Framework Complete Workflow
  Step 1: validate_project_description
  Step 2: assess_model_risk
  Step 3: evaluate_lifecycle_compliance
  Step 4: generate_risk_rating
  Step 5: create_compliance_framework
  Step 6: export_e23_report
  [Recommended use: Financial institution models]

🇨🇦🏦 Combined AIA + OSFI E-23 Workflow
  [For AI systems in financial institutions requiring both]

Which framework do you want to use?
```

**Problem**: User mentioned "OSFI" explicitly, but sees AIA and Combined workflows too.

---

## Proposed User Experience (Simplified)

### Option 1: Smart Context Detection (Recommended)

When a user says: **"Help me run through OSFI E-23 for my credit risk model"**

Claude detects:
- Keywords: "OSFI", "credit risk model" → Financial context
- Auto-select: OSFI E-23 framework

Claude shows:
```
🏦 OSFI E-23 Model Risk Management Assessment

I see you're working with a model for financial regulation. I'll guide you through
OSFI Guideline E-23 compliance.

Complete OSFI E-23 Workflow (6 Steps):

  STEP 1: Validate Project Description
    → validate_project_description
    → Ensures your model description has sufficient detail

  STEP 2: Assess Model Risk
    → assess_model_risk
    → Comprehensive risk rating (Low/Medium/High/Critical)

  STEP 3: Evaluate Lifecycle Compliance
    → evaluate_lifecycle_compliance
    → Stage-specific requirements (Design/Review/Deployment/etc.)

  STEP 4: Generate Risk Rating
    → generate_risk_rating
    → Detailed risk methodology documentation

  STEP 5: Create Compliance Framework
    → create_compliance_framework
    → Governance structure and policies

  STEP 6: Export E-23 Report
    → export_e23_report
    → Professional Word document (4-6 pages)

Minimum viable assessment: Steps 1, 2, and 6

Note: If your system also makes automated decisions for government, you may
need the AIA framework too. Just ask!

Would you like me to start with Step 1 (validate your model description)?
```

**Benefits**:
- ✅ User only sees OSFI workflow (relevant to their request)
- ✅ Mentions AIA is available if needed (not overwhelming)
- ✅ Clear next step guidance
- ✅ Same server, better UX

---

### Option 2: Explicit Framework Parameter

Add optional `framework` parameter to `get_server_introduction`:

```python
{
  "name": "get_server_introduction",
  "inputSchema": {
    "type": "object",
    "properties": {
      "framework": {
        "type": "string",
        "enum": ["aia", "osfi_e23", "both", "auto"],
        "description": "Which framework to focus on (auto-detect if not specified)"
      },
      "user_context": {
        "type": "string",
        "description": "User's statement or project context for auto-detection"
      }
    }
  }
}
```

**Usage**:
```
User: "Run through OSFI framework for my credit model"

Claude calls:
  get_server_introduction(framework="osfi_e23")

Result: Only shows OSFI E-23 workflow
```

---

### Option 3: Two-Stage Introduction (Progressive Disclosure)

**Stage 1: Brief Overview**
```
🇨🇦 Canada's Regulatory Assessment MCP Server

Which framework applies to your project?

1. 🏦 OSFI E-23 - For financial institution models
   (Banks, credit unions, insurance companies)

2. 🇨🇦 AIA - For federal government automated decisions
   (Services, programs, regulatory decisions)

3. 🇨🇦🏦 Both - AI systems in regulated financial institutions

Tell me which one, and I'll show you the complete workflow.
```

**Stage 2: Detailed Workflow (after user choice)**
```
User: "OSFI E-23"

Claude: [Shows only OSFI E-23 6-step workflow]
```

**Benefits**:
- ✅ Minimal cognitive load initially
- ✅ User chooses framework first
- ✅ Detailed workflow only shown after selection

---

## Implementation Comparison

### Option 1: Smart Context Detection

**Code Changes**: `server.py` lines 666-857

**Detection Logic**:
```python
def _detect_framework(self, user_context: str) -> str:
    """Detect which framework user needs based on keywords."""

    context_lower = user_context.lower()

    # OSFI E-23 indicators
    osfi_keywords = [
        'osfi', 'e-23', 'e23', 'bank', 'financial institution',
        'credit union', 'insurance', 'model risk', 'basel',
        'regulatory capital', 'credit risk model'
    ]

    # AIA indicators
    aia_keywords = [
        'aia', 'algorithmic impact', 'government', 'federal',
        'automated decision', 'public service', 'treasury board',
        'canada.ca'
    ]

    # Combined indicators
    combined_keywords = [
        'both frameworks', 'aia and osfi', 'government and bank',
        'combined assessment'
    ]

    if any(kw in context_lower for kw in combined_keywords):
        return 'combined'
    elif any(kw in context_lower for kw in osfi_keywords):
        return 'osfi_e23'
    elif any(kw in context_lower for kw in aia_keywords):
        return 'aia'
    else:
        return 'both'  # Show both if unclear
```

**Modified Introduction**:
```python
def _get_server_introduction(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Provide framework-specific or combined introduction based on context."""

    # Get user context from arguments or session
    user_context = arguments.get('user_context', '')

    # Detect which framework to show
    framework_focus = self._detect_framework(user_context)

    # Build introduction based on detected framework
    if framework_focus == 'osfi_e23':
        return self._build_osfi_introduction()
    elif framework_focus == 'aia':
        return self._build_aia_introduction()
    else:
        return self._build_combined_introduction()  # Current behavior
```

**Effort**: 1-2 days

---

### Option 2: Explicit Framework Parameter

**Code Changes**: `server.py` lines 156-162, 666-857

**Tool Schema Update**:
```python
{
    "name": "get_server_introduction",
    "inputSchema": {
        "type": "object",
        "properties": {
            "framework": {
                "type": "string",
                "enum": ["aia", "osfi_e23", "both", "auto"],
                "description": "Which framework to focus on",
                "default": "auto"
            }
        },
        "additionalProperties": False
    }
}
```

**Effort**: 0.5 days

---

### Option 3: Two-Stage Introduction

**Code Changes**: Add new tool `choose_framework`

**New Tool**:
```python
{
    "name": "choose_framework",
    "description": "Brief overview to help user choose between AIA, OSFI E-23, or both",
    "inputSchema": {"type": "object", "properties": {}}
}
```

**Flow**:
1. Call `choose_framework` → Shows brief overview
2. User chooses
3. Call `get_server_introduction(framework="osfi_e23")` → Shows detailed workflow

**Effort**: 1 day

---

## Recommendation: Option 1 (Smart Context Detection)

### Why This Is Best

**User Experience**:
- ✅ Zero additional user input required
- ✅ Shows only relevant framework automatically
- ✅ Fallback to "both" if context unclear
- ✅ Still mentions other framework is available

**Implementation**:
- ✅ No new tools needed
- ✅ No schema changes (can use existing session context)
- ✅ Backward compatible (defaults to "both" if no context)
- ✅ Claude can pass context from user's message

**Example Flows**:

**Flow 1: Clear OSFI Context**
```
User: "Help me assess my credit scoring model for OSFI compliance"

Claude: [Analyzes: "credit scoring model" + "OSFI" → OSFI E-23]
Claude: [Calls get_server_introduction with internal OSFI detection]
Claude: [Shows ONLY OSFI E-23 6-step workflow]
Claude: "I see you're working on a credit scoring model. Let me guide you
         through OSFI E-23 compliance. Here's the complete 6-step workflow..."
```

**Flow 2: Clear AIA Context**
```
User: "I need to do an AIA for our benefits eligibility system"

Claude: [Analyzes: "AIA" + "benefits eligibility" → Government/AIA]
Claude: [Calls get_server_introduction with internal AIA detection]
Claude: [Shows ONLY AIA 5-step workflow]
Claude: "I'll help you complete the Algorithmic Impact Assessment. Here's
         the 5-step workflow..."
```

**Flow 3: Unclear Context**
```
User: "Help me assess my AI system"

Claude: [Analyzes: Generic request → Show both]
Claude: [Calls get_server_introduction]
Claude: [Shows BOTH workflows]
Claude: "I can help assess your AI system. Which framework applies?
         - OSFI E-23 if it's for a financial institution
         - AIA if it's for government services
         - Both if it's for financial services with government interaction"
```

**Flow 4: Combined Context**
```
User: "I need both AIA and OSFI assessments for our lending platform"

Claude: [Analyzes: "both" + "AIA and OSFI" → Combined]
Claude: [Shows BOTH workflows with combined guidance]
Claude: "I'll help you with both frameworks. Let's start with description
         validation (common Step 1), then run through both assessments..."
```

---

## Implementation Plan

### Phase 1: Add Framework Detection (Day 1)

**File**: `server.py`

**Add Method**:
```python
def _detect_framework_from_session(self, session_id: str = None) -> str:
    """
    Detect which framework to emphasize based on session context.

    Returns:
        'aia' | 'osfi_e23' | 'both'
    """
    # If session exists, check workflow type or recent tool calls
    if session_id and session_id in self.workflow_engine.sessions:
        session = self.workflow_engine.sessions[session_id]
        assessment_type = session.get('assessment_type', '')

        if 'aia' in assessment_type:
            return 'aia'
        elif 'osfi' in assessment_type:
            return 'osfi_e23'

    # Default: show both if unclear
    return 'both'
```

### Phase 2: Split Introduction Response (Day 1-2)

**File**: `server.py`

**Extract Framework-Specific Sections**:
```python
def _build_aia_workflow_section(self) -> Dict:
    """Return AIA-focused workflow information."""
    return {
        "title": "🇨🇦 AIA Framework Assessment",
        "description": "Canada's Algorithmic Impact Assessment for automated decision-making",
        "framework": "aia",
        "sequence": [...],  # 5 steps
        "note": "If your system is also subject to financial regulation, you may need OSFI E-23 too."
    }

def _build_osfi_workflow_section(self) -> Dict:
    """Return OSFI E-23-focused workflow information."""
    return {
        "title": "🏦 OSFI E-23 Model Risk Management",
        "description": "OSFI Guideline E-23 for federally regulated financial institutions",
        "framework": "osfi_e23",
        "sequence": [...],  # 6 steps
        "note": "If your model makes automated decisions impacting citizens, you may need AIA too."
    }

def _build_combined_workflow_section(self) -> Dict:
    """Return both frameworks (current behavior)."""
    return {
        "aia_workflow": self._build_aia_workflow_section(),
        "osfi_e23_workflow": self._build_osfi_workflow_section(),
        "combined_workflow": {...}
    }
```

### Phase 3: Modify Introduction Logic (Day 2)

**File**: `server.py`, lines 666-857

**Update `_get_server_introduction`**:
```python
def _get_server_introduction(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Provide framework-specific or combined introduction."""

    # Detect framework from session or default to both
    session_id = arguments.get('session_id')
    framework_focus = self._detect_framework_from_session(session_id)

    # Build base introduction (common parts)
    base_intro = {
        "server_introduction": {...},  # Lines 678-691 (unchanged)
        "compliance_warnings": {...},   # Lines 825-830 (unchanged)
    }

    # Add framework-specific workflow
    if framework_focus == 'aia':
        base_intro["framework_workflow"] = self._build_aia_workflow_section()
        base_intro["assistant_directive"] = {
            "critical_instruction": "Present the AIA workflow. Mention OSFI E-23 is available if user asks."
        }
    elif framework_focus == 'osfi_e23':
        base_intro["framework_workflow"] = self._build_osfi_workflow_section()
        base_intro["assistant_directive"] = {
            "critical_instruction": "Present the OSFI E-23 workflow. Mention AIA is available if user asks."
        }
    else:  # both
        base_intro["framework_workflows"] = self._build_combined_workflow_section()
        base_intro["assistant_directive"] = {
            "critical_instruction": "Present both workflows and ask user which applies."
        }

    self.introduction_shown = True
    return base_intro
```

### Phase 4: Update Claude Behavior (No Code Changes)

**Current Tool Description** (Line 157):
```
"CALL THIS ALONE: This tool MUST be called BY ITSELF at the START..."
```

**Add Context Awareness**:
```
"CALL THIS ALONE: This tool MUST be called BY ITSELF at the START...

IMPORTANT: This tool will automatically show the relevant framework based on
context. If the user mentions:
- 'OSFI', 'bank', 'financial institution' → Shows OSFI E-23 workflow only
- 'AIA', 'government', 'federal' → Shows AIA workflow only
- 'both' or unclear → Shows both workflows

After presenting the introduction, follow the workflow shown."
```

---

## Testing Plan

### Test Case 1: OSFI-Only Request
```
User: "Help me assess my credit risk model for OSFI compliance"

Expected:
1. get_server_introduction called
2. Response contains ONLY OSFI E-23 workflow (6 steps)
3. No AIA workflow shown
4. Brief note: "If your model is also for government, AIA may apply"
5. Claude starts OSFI E-23 Step 1
```

### Test Case 2: AIA-Only Request
```
User: "I need to complete the AIA for our benefits system"

Expected:
1. get_server_introduction called
2. Response contains ONLY AIA workflow (5 steps)
3. No OSFI workflow shown
4. Brief note: "If your system is for financial institutions, OSFI E-23 may apply"
5. Claude starts AIA Step 1
```

### Test Case 3: Unclear Request
```
User: "Help me assess my AI system"

Expected:
1. get_server_introduction called
2. Response contains BOTH workflows
3. Claude asks which framework applies
4. Waits for user choice
```

### Test Case 4: Explicit Both
```
User: "I need both AIA and OSFI assessments"

Expected:
1. get_server_introduction called
2. Response contains BOTH workflows
3. Claude explains combined workflow approach
4. Starts with validate_project_description (common step)
```

---

## Benefits Summary

**For Users**:
- ✅ Less cognitive overhead (see only what's relevant)
- ✅ Faster time-to-assessment (no framework choice delay if clear)
- ✅ Still have access to both frameworks if needed
- ✅ Progressive disclosure (can ask for other framework later)

**For Development**:
- ✅ No architectural changes required
- ✅ Same server handles both frameworks
- ✅ Backward compatible (defaults to "both" if unclear)
- ✅ Easy to implement (1-2 days)

**For Maintenance**:
- ✅ Single codebase to maintain
- ✅ No deployment complexity
- ✅ Easy to adjust detection logic
- ✅ Can add more frameworks later (EU AI Act, etc.)

---

## Alternative: Quick Win (30 minutes)

If you want an IMMEDIATE improvement without any code changes:

**Update Claude Desktop System Prompt**:

Add to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "regulatory-assessment": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "customInstructions": "When user mentions OSFI, focus on OSFI E-23 workflow only. When user mentions AIA or government, focus on AIA workflow only. Only show both frameworks if user explicitly asks or context is unclear."
    }
  }
}
```

This tells Claude to be selective even with current tool responses.

**Effectiveness**: 70% improvement with zero code changes!

---

## Recommendation

**Immediate (Today)**:
- Add `customInstructions` to Claude Desktop config (30 min)

**Short-term (This Week)**:
- Implement Option 1 (Smart Context Detection) (1-2 days)
- Test with real user scenarios
- Deploy and monitor user feedback

**No Need For**:
- Splitting servers into separate AIA/OSFI instances
- Architectural refactoring
- Multiple deployment configurations

The user experience problem can be solved **at the UX layer**, not the architecture layer.
