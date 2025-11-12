# OSFI E-23 Lifecycle and Terminology Fix - Implementation Plan

## Overview

Complete refactoring of `export_e23_report` to use official OSFI E-23 terminology and organize reports by lifecycle stage.

## Critical Issues to Fix

1. **Incorrect Terminology** - Currently uses "Section X.X", should use "Principle X.X"
2. **No Lifecycle Stage Detection** - Doesn't determine current stage from project description
3. **Mixed Stage Content** - Shows all stages together instead of current stage only
4. **Missing OSFI Appendix 1 Fields** - Model tracking fields not included
5. **Generic Checklists** - Not stage-specific (Design/Review/Deployment/Monitoring/Decommission)

## Implementation Approach

### Phase 1: Create OSFI E-23 Data Structures
**File:** `osfi_e23_structure.py` (new module)

```python
# OSFI E-23 Principles (complete list)
OSFI_PRINCIPLES = {
    "1.1": "Effective reporting structures and proper resourcing...",
    "1.2": "The MRM framework should align risk-taking activities...",
    # ... all 12 principles
}

# OSFI E-23 Outcomes
OSFI_OUTCOMES = {
    "1": "Model risk is well understood and managed across the enterprise",
    "2": "Model risk is managed using a risk-based approach",
    "3": "Model governance covers the entire model lifecycle"
}

# Lifecycle components with principles mapping
OSFI_LIFECYCLE_COMPONENTS = {
    "design": {
        "name": "Model Design",
        "subcomponents": ["Model Rationale", "Model Data", "Model Development"],
        "principles": ["3.2", "3.3"]
    },
    # ... all 5 stages
}

# OSFI Appendix 1 tracking fields
APPENDIX_1_REQUIRED_FIELDS = [
    "model_id", "model_name", "model_description",
    "model_owner", "model_developer", "model_origin"
]

APPENDIX_1_LIFECYCLE_FIELDS = {
    "design": ["provisional_risk_rating", "target_review_date"],
    "review": ["model_reviewer", "review_scope"],
    # ... stage-specific fields
}
```

### Phase 2: Implement Lifecycle Stage Detection
**File:** `osfi_e23_structure.py`

```python
def detect_lifecycle_stage(project_description: str) -> str:
    """
    Detect current lifecycle stage from project description.

    Returns: 'design', 'review', 'deployment', 'monitoring', or 'decommission'
    """
    description_lower = project_description.lower()

    # Priority order checking (most specific first)
    stage_indicators = {
        "decommission": ["retiring", "decommission", "sunsetting", "end of life"],
        "monitoring": ["deployed", "in production", "live", "monitoring"],
        "deployment": ["deploying", "implementing", "go-live", "rollout"],
        "review": ["review", "validation", "validating", "under review"],
        "design": ["design", "developing", "planning", "creating"]
    }

    for stage, indicators in stage_indicators.items():
        if any(indicator in description_lower for indicator in indicators):
            return stage

    return 'design'  # Default
```

### Phase 3: Create Stage-Specific Checklist Generators
**File:** `osfi_e23_structure.py`

```python
def get_design_stage_checklist() -> dict:
    """Return Design stage specific checklist with OSFI Principle references."""
    return {
        "model_rationale": [
            {
                "item": "Clear organizational rationale documented",
                "requirement": "Establish why this model is needed and its business purpose",
                "deliverable": "Model Rationale Document",
                "osfi_reference": "Principle 3.2 (Model Rationale)",
                "category": "design"
            },
            # ... all Design stage items
        ],
        "model_data": [...],
        "model_development": [...],
        "planning_for_future": [...],
        "design_governance": [...],
        "readiness_for_review": [...]
    }

def get_review_stage_checklist() -> dict:
    """Return Review stage specific checklist."""
    # ... Review stage items referencing Principle 3.4

def get_monitoring_stage_checklist() -> dict:
    """Return Monitoring stage specific checklist."""
    # ... Monitoring stage items referencing Principle 3.6

# ... other stages
```

### Phase 4: Create Stage-Specific Report Generators
**File:** `osfi_e23_structure.py`

```python
def generate_design_stage_report(
    project_name: str,
    project_description: str,
    assessment_results: dict,
    doc: Document
) -> Document:
    """
    Generate Design stage compliance report.
    Focus only on Design stage requirements (Principles 3.2, 3.3).
    """
    # Title with stage
    doc.add_heading(
        f"OSFI E-23 Model Risk Management Assessment",
        0
    )
    doc.add_heading(
        f"{project_name} - Design Stage Compliance Report",
        1
    )

    # Executive Summary with stage status
    add_executive_summary_design_stage(doc, assessment_results)

    # Model Information Profile (OSFI Appendix 1)
    add_appendix_1_fields(doc, assessment_results, stage="design")

    # Current Lifecycle Stage Assessment
    add_design_stage_assessment(doc, assessment_results)

    # Design Stage Compliance Checklist
    add_design_stage_checklist(doc, assessment_results)

    # Design Stage Gap Analysis
    add_gap_analysis(doc, assessment_results, stage="design")

    # Readiness for Review Stage
    add_review_stage_readiness(doc, assessment_results)

    # Risk Rating Summary (institution-defined)
    add_risk_rating_summary(doc, assessment_results)

    # OSFI Principles Mapping (Design stage)
    add_principles_mapping_design(doc, assessment_results)

    # Implementation Roadmap (Design stage completion)
    add_implementation_roadmap(doc, assessment_results, stage="design")

    # Model Description
    add_model_description(doc, project_description)

    # Appendices
    add_appendices_design_stage(doc)

    # Professional validation warning
    add_professional_validation_warning(doc, stage="design")

    return doc

# Similar functions for other stages
def generate_review_stage_report(...):
def generate_monitoring_stage_report(...):
```

### Phase 5: Refactor Main Export Function
**File:** `server.py` (modify existing `_export_e23_report`)

```python
def _export_e23_report(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Export lifecycle-focused OSFI E-23 report."""
    project_name = arguments.get("project_name", "")
    project_description = arguments.get("project_description", "")
    assessment_results = arguments.get("assessment_results", {})

    # ... existing validation checks ...

    try:
        # Detect lifecycle stage
        from osfi_e23_structure import detect_lifecycle_stage
        current_stage = detect_lifecycle_stage(project_description)

        logger.info(f"Detected lifecycle stage: {current_stage}")

        # Create document
        doc = Document()

        # Generate stage-specific report
        if current_stage == 'design':
            from osfi_e23_structure import generate_design_stage_report
            doc = generate_design_stage_report(
                project_name, project_description, assessment_results, doc
            )
        elif current_stage == 'review':
            from osfi_e23_structure import generate_review_stage_report
            doc = generate_review_stage_report(
                project_name, project_description, assessment_results, doc
            )
        # ... other stages

        # Save document
        doc.save(file_path)

        return {
            "success": True,
            "file_path": file_path,
            "lifecycle_stage": current_stage,
            "message": f"OSFI E-23 {current_stage.capitalize()} Stage compliance report generated"
        }
```

### Phase 6: Create Comprehensive Tests
**File:** `test_osfi_e23_lifecycle.py` (new)

```python
def test_lifecycle_stage_detection():
    """Test stage detection from project descriptions."""

    # Test Design stage detection
    design_desc = "We are developing a credit risk model..."
    assert detect_lifecycle_stage(design_desc) == 'design'

    # Test Review stage detection
    review_desc = "Our model is under independent validation..."
    assert detect_lifecycle_stage(review_desc) == 'review'

    # Test Monitoring stage detection
    monitoring_desc = "Our model is deployed in production..."
    assert detect_lifecycle_stage(monitoring_desc) == 'monitoring'

def test_design_stage_report_structure():
    """Test Design stage report contains correct sections."""
    # ... test that report includes Design stage checklist only
    # ... test that report references Principles 3.2 and 3.3
    # ... test that report includes OSFI Appendix 1 fields
    # ... test NO detailed Review/Deployment/Monitoring checklists

def test_osfi_terminology():
    """Test that reports use Principle X.X not Section X.X."""
    # ... test no "Section" references
    # ... test all "Principle" references are valid (1.1-3.6)

def test_appendix_1_fields():
    """Test all OSFI Appendix 1 tracking fields included."""
    # ... test required fields present
    # ... test stage-specific fields present
    # ... test future fields marked as TBD
```

## File Structure Changes

### New Files
```
osfi_e23_structure.py (new module)
├── OSFI_PRINCIPLES (dict)
├── OSFI_OUTCOMES (dict)
├── OSFI_LIFECYCLE_COMPONENTS (dict)
├── APPENDIX_1_FIELDS (lists)
├── detect_lifecycle_stage(description) -> str
├── get_design_stage_checklist() -> dict
├── get_review_stage_checklist() -> dict
├── get_monitoring_stage_checklist() -> dict
├── generate_design_stage_report(...) -> Document
├── generate_review_stage_report(...) -> Document
├── generate_monitoring_stage_report(...) -> Document
└── helper functions for sections

test_osfi_e23_lifecycle.py (new tests)
├── test_lifecycle_stage_detection()
├── test_design_stage_report_structure()
├── test_review_stage_report_structure()
├── test_monitoring_stage_report_structure()
├── test_osfi_terminology()
├── test_appendix_1_fields()
└── test_stage_specific_checklists()
```

### Modified Files
```
server.py
└── _export_e23_report() - refactored to use osfi_e23_structure module

CLAUDE.md
└── Updated with lifecycle-focused reports, validation fixes, export fixes
```

## Testing Strategy

### Unit Tests
- Stage detection logic
- Checklist generation for each stage
- OSFI Principle references
- Appendix 1 field inclusion

### Integration Tests
- Full report generation for Design stage
- Full report generation for Review stage
- Full report generation for Monitoring stage
- Terminology validation
- No "Section" references
- All "Principle" references valid

### Verification Tests
- Design stage project -> only Design checklist
- Review stage project -> only Review checklist
- Monitoring stage project -> only Monitoring checklist
- All reports include OSFI Appendix 1
- All reports use Principle X.X format

## Success Criteria

✅ All reports use "Principle X.X" not "Section X.X"
✅ Lifecycle stage correctly detected from description
✅ Reports organized by current stage only
✅ Design stage reports show ONLY Design requirements
✅ All OSFI Appendix 1 fields included
✅ "Planning for future stages" in Design (not implementation details)
✅ References map to actual OSFI E-23 structure
✅ Risk rating labeled as institution-defined
✅ Professional validation warnings included
✅ All tests passing

## Implementation Order

1. ✅ Update CLAUDE.md documentation
2. ⏳ Create `osfi_e23_structure.py` with data structures
3. ⏳ Implement lifecycle stage detection
4. ⏳ Create Design stage checklist generator
5. ⏳ Create Design stage report generator
6. ⏳ Refactor `_export_e23_report` in server.py
7. ⏳ Create test suite
8. ⏳ Run tests and verify
9. ⏳ Create Review/Monitoring stage generators (if time permits)
10. ⏳ Commit and push all changes

## Notes

- Risk scoring mechanism remains unchanged (institution-defined)
- Focus initially on Design stage (most common use case)
- Review/Monitoring stages can follow same pattern
- Complete OSFI Appendix 1 implementation
- Stage detection is rule-based (keyword matching)

---

**Implementation Start:** 2025-11-04
**Target Completion:** Same day
**Priority:** HIGH - Critical OSFI E-23 compliance issue
