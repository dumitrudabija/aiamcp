# OSFI E-23 MCP Server: Explainer Video Narrative

**Purpose**: This document provides the narrative structure for a 3-4 minute explainer video about the OSFI E-23 Model Risk Management MCP Server.

**Target Audience**: Mixed - executives, technical teams, and compliance professionals

**Key Takeaway**: "I understand what was built and how it's helpful"

---

## VIDEO STRUCTURE (3-4 Minutes)

---

### SECTION 1: THE PROBLEM (30-45 seconds)

**Opening Hook:**

Banks and financial institutions face a significant challenge: Canada's OSFI Guideline E-23 requires them to assess and manage model risk - but the guideline is *principles-based*, not prescriptive.

**The Challenge:**

OSFI E-23 tells institutions WHAT they must do:
- Rate every model for risk (using quantitative AND qualitative factors)
- Govern models throughout their lifecycle (Design → Review → Deployment → Monitoring → Decommission)
- Scale governance intensity based on risk level

But OSFI deliberately does NOT tell institutions HOW to do it:
- No specific scoring formulas
- No prescribed risk thresholds
- No mandated approval hierarchies
- No standard templates

**The Result:**

Each bank must design their own methodology - which is time-consuming, requires specialized expertise, and creates inconsistency across the industry.

---

### SECTION 2: THE SOLUTION (60-90 seconds)

**What We Built:**

An AI-powered regulatory assessment tool that demonstrates how OSFI E-23 compliance can be operationalized through intelligent automation.

**How It Works - Three Actors:**

```
USER (Human)          CLAUDE (AI Assistant)       PYTHON LOGIC (Regulatory Engine)
     │                        │                              │
     │ Provides project       │ Orchestrates                │ Does ALL the work:
     │ description            │ conversation                │ - Risk scoring
     │                        │                              │ - Keyword detection
     │ Reviews results        │ Presents results            │ - Compliance checking
     │                        │ in plain language           │ - Document generation
     │ Makes decisions        │                              │
```

**The 5-Step Workflow:**

1. **Validate** - Ensure project description has adequate detail
2. **Assess Risk** - Calculate risk score using quantitative and qualitative factors
3. **Check Coverage** - Identify which OSFI requirements are addressed
4. **Create Framework** - Generate governance requirements based on risk level
5. **Export Report** - Produce a professional Word document

**Key Innovation:**

The regulatory intelligence is 100% rule-based Python code - NOT AI interpretation. Claude provides the conversational interface, but all scoring, thresholds, and compliance determinations come from transparent, auditable logic.

---

### SECTION 3: THE FLEXIBILITY (60-90 seconds)

**The Critical Distinction:**

This tool clearly separates:

| OFFICIAL (From OSFI E-23) | PROOF OF CONCEPT (Our Implementation) |
|---------------------------|---------------------------------------|
| Must have risk rating methodology | 13 specific risk factors |
| Must use quantitative + qualitative factors | 10/8 point weighting |
| Must scale governance by risk | 4 risk levels with specific thresholds |
| 5 lifecycle stages | Keyword detection methodology |
| Risk-based governance intensity | Specific approval authorities |

**Why This Matters:**

Every parameter in our implementation is **explicitly documented as customizable**:

- **Risk Factors**: Add, remove, or rename the 13 factors to match your institution
- **Scoring Weights**: Change 10/8 points to 12/6 or any ratio that fits your risk appetite
- **Thresholds**: Adjust Low/Medium/High/Critical boundaries
- **Amplification Logic**: Modify which risk combinations trigger elevated scores
- **Governance Mapping**: Align approval authorities with your organizational structure
- **Keywords**: Add industry-specific terms for your business model

**The Value Proposition:**

Banks don't have to start from zero. They can:
1. Use this implementation as a **starting point**
2. Validate against their existing risk framework
3. Customize parameters to match institutional requirements
4. Deploy a working solution faster than building from scratch

---

### SECTION 4: THE OUTCOME (30-45 seconds)

**What This Demonstrates:**

1. **OSFI E-23 compliance is achievable through automation** - The principles-based guideline can be operationalized with concrete, auditable logic

2. **Standardization WITH flexibility** - The MCP framework provides consistent structure while allowing institutional customization

3. **Transparency is built-in** - Every calculation is rule-based, documented, and auditable - no "black box" AI decisions in regulatory assessments

4. **Professional validation remains essential** - The tool explicitly requires human oversight and governance approval before regulatory use

**The Bottom Line:**

This proof of concept shows that banks can leverage AI assistants for regulatory compliance while maintaining full control over their risk methodology - combining the efficiency of automation with the rigor of institutional expertise.

---

## KEY MESSAGES TO EMPHASIZE

### For Executives:
- "Faster path to OSFI E-23 compliance without sacrificing control"
- "Customize to your risk appetite, not a one-size-fits-all approach"

### For Technical Teams:
- "Modular architecture - 6 specialized modules with clear separation of concerns"
- "All regulatory logic in Python - testable, auditable, maintainable"

### For Compliance Professionals:
- "Official OSFI requirements vs. implementation choices clearly documented"
- "Built-in professional validation requirements throughout"

---

## SUPPORTING VISUALS SUGGESTIONS

1. **Problem Slide**: OSFI E-23 document with "WHAT" highlighted, empty space for "HOW"

2. **Three-Actor Diagram**: User → Claude → Python with arrows showing data flow

3. **5-Step Workflow**: Visual flowchart with icons for each step

4. **Customization Table**: Side-by-side showing "Default" vs "Your Institution"

5. **Report Sample**: Screenshot of generated Word document

6. **Architecture Diagram**: From LOGICAL_ARCHITECTURE.md showing session persistence

---

## DOCUMENTS FOR DEEPER REFERENCE

After the video, viewers wanting more detail should be directed to:

| Topic | Document |
|-------|----------|
| Complete feature list | README.md |
| How actors interact | LOGICAL_ARCHITECTURE.md |
| What can be customized | OSFI_E23_TUNABLE_PARAMETERS.md |
| Official vs. implementation choices | OSFI_E23_RISK_METHODOLOGY_IMPLEMENTATION_ANALYSIS.md |
| Technical architecture | ARCHITECTURE.md |

---

## SCRIPT NOTES FOR AI VIDEO TOOL

**Tone**: Professional but accessible. Avoid jargon where possible.

**Pacing**:
- Section 1 (Problem): Set up tension - "this is hard"
- Section 2 (Solution): Build understanding - "here's how it works"
- Section 3 (Flexibility): Deliver key insight - "this is why it's different"
- Section 4 (Outcome): Close with value - "this is what it means for you"

**Emphasis Points** (for AI voice modulation):
- "Principles-based, NOT prescriptive" (contrast)
- "WHAT they must do... HOW to do it" (contrast)
- "100% rule-based Python code" (credibility)
- "Explicitly documented as customizable" (key differentiator)
- "Starting point, not a final answer" (managing expectations)

---

*Document Version: 1.0*
*Created: 2025-11-28*
*For: Explainer Video Production*
