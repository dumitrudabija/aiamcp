"""
OSFI E-23 Report Generation - v3.0 Risk Dimensions Framework

Generates concise, professional OSFI E-23 compliance reports using:
- 6 Risk Dimensions for assessment display
- LIFECYCLE_REQUIREMENTS_BY_RISK for governance checklists
- Risk-scaled requirements based on assessed risk level
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
from typing import Dict, Any, List
import logging

from osfi_e23_structure import (
    LIFECYCLE_REQUIREMENTS_BY_RISK,
    get_lifecycle_requirements_for_risk_level,
    OSFI_LIFECYCLE_COMPONENTS,
    OSFI_PRINCIPLES
)
from osfi_e23_risk_dimensions import (
    RISK_DIMENSIONS,
    DIMENSION_ORDER,
    get_dimension,
    get_dimension_factors
)

logger = logging.getLogger(__name__)


def generate_osfi_e23_report(
    project_name: str,
    project_description: str,
    assessment_results: Dict[str, Any],
    doc: Document,
    current_stage: str = "design"
) -> Document:
    """
    Generate OSFI E-23 compliance report using v3.0 Risk Dimensions framework.

    Report Structure:
    1. Executive Summary
    2. Risk Assessment by Dimension (6 dimensions summary)
    3. [STAGE] Lifecycle Requirements (with 1-2 checklist items each)
    Annex A: Detailed Factor Assessment (6 tables, one per dimension)
    Annex B: OSFI E-23 Principles

    Target: ~6-8 pages with professional formatting.
    """
    # Extract key data
    risk_level = assessment_results.get("risk_level", "Medium")
    risk_score = assessment_results.get("risk_score", 50)
    dimension_assessments = assessment_results.get("dimension_assessments", {})
    factor_scores = assessment_results.get("factor_scores", {})
    validated_extraction = assessment_results.get("validated_extraction", {})
    assessment_date = datetime.now().strftime("%B %d, %Y")

    # Stage display name
    stage_display = current_stage.capitalize()

    # Title page
    title = doc.add_heading('OSFI E-23 Model Risk Assessment', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    subtitle = doc.add_heading(project_name, level=1)
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Metadata
    doc.add_paragraph()
    _add_metadata(doc, assessment_date, risk_level, risk_score, stage_display)

    # Data source transparency
    doc.add_paragraph()
    _add_data_source_transparency(doc)

    # Professional validation disclaimer
    _add_professional_validation_disclaimer(doc)

    doc.add_page_break()

    # 1. Executive Summary
    _add_executive_summary(doc, project_name, risk_level, risk_score, stage_display, dimension_assessments)

    # 2. Risk Assessment by Dimension
    _add_dimension_assessment(doc, dimension_assessments, risk_level, risk_score)

    # 3. Lifecycle Requirements for Current Stage
    _add_lifecycle_requirements(doc, current_stage, stage_display, risk_level)

    doc.add_page_break()

    # Annex A: Detailed Factor Assessment
    _add_annex_factor_assessment(doc, dimension_assessments, factor_scores, validated_extraction)

    doc.add_page_break()

    # Annex B: OSFI E-23 Principles
    _add_annex_principles(doc)

    return doc


def _add_metadata(doc: Document, assessment_date: str, risk_level: str, risk_score: int, stage_display: str):
    """Add assessment metadata section."""
    p = doc.add_paragraph()
    p.add_run('Assessment Date: ').bold = True
    p.add_run(assessment_date)

    p = doc.add_paragraph()
    p.add_run('Current Lifecycle Stage: ').bold = True
    p.add_run(stage_display)

    p = doc.add_paragraph()
    p.add_run('Risk Rating: ').bold = True
    run = p.add_run(f'{risk_level} ({risk_score}/100)')

    # Color code by risk level
    risk_colors = {
        "Critical": RGBColor(192, 0, 0),
        "High": RGBColor(255, 102, 0),
        "Medium": RGBColor(255, 192, 0),
        "Low": RGBColor(0, 128, 0)
    }
    run.font.color.rgb = risk_colors.get(risk_level, RGBColor(0, 0, 0))
    run.bold = True


def _add_data_source_transparency(doc: Document):
    """Add data source and methodology transparency notice."""
    p = doc.add_paragraph()
    run = p.add_run('DATA SOURCE TRANSPARENCY')
    run.bold = True
    run.font.size = Pt(11)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph()
    run = p.add_run('🔧 MCP SERVER OUTPUT: ')
    run.bold = True
    p.add_run(
        'Risk scores calculated using 6 Risk Dimensions with deterministic factor assessment. '
        'Governance requirements derived from risk-level-based lookup tables. '
        'All scoring weights and thresholds are tunable parameters for institutional customization.'
    )
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.space_after = Pt(12)


def _add_professional_validation_disclaimer(doc: Document):
    """Add professional validation requirement disclaimer."""
    doc.add_paragraph()

    p = doc.add_paragraph()
    run = p.add_run('⚠️ PROFESSIONAL VALIDATION REQUIRED')
    run.bold = True
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(192, 0, 0)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.right_indent = Inches(0.5)
    p.paragraph_format.space_after = Pt(12)

    disclaimer_text = (
        'This assessment provides automated preliminary analysis based on the OSFI E-23 framework. '
        'All findings, risk ratings, and governance recommendations MUST be validated by qualified '
        'model risk management professionals before regulatory compliance use.\n\n'
        'Required validation includes:\n'
        '• Independent review by qualified MRM professionals\n'
        '• Verification by senior management or risk committees\n'
        '• Legal and compliance review of regulatory interpretations'
    )
    run = p.add_run(disclaimer_text)
    run.font.size = Pt(9)
    run.italic = True


def _add_executive_summary(doc: Document, project_name: str, risk_level: str,
                          risk_score: int, stage_display: str,
                          dimension_assessments: Dict[str, Any]):
    """Add executive summary section."""
    doc.add_heading('1. EXECUTIVE SUMMARY', level=1)

    # Governance intensity by risk level
    governance_req = {
        "Critical": "board-level oversight, external validation, and continuous monitoring",
        "High": "senior management oversight, enhanced controls, and regular independent review",
        "Medium": "standard governance with periodic review and appropriate documentation",
        "Low": "basic governance procedures with annual review cycles"
    }.get(risk_level, "standard governance procedures")

    # Build summary
    summary_parts = [
        f"This model has been assessed as {risk_level} risk ({risk_score}/100) under OSFI E-23 guidelines.",
        f"This classification requires {governance_req}.",
        f"Currently at {stage_display} stage with corresponding lifecycle requirements."
    ]

    # Add key dimension drivers if available
    if dimension_assessments:
        high_risk_dims = [
            dim_id for dim_id, assessment in dimension_assessments.items()
            if assessment.get("risk_level") in ["High", "Critical"]
        ]
        if high_risk_dims:
            dim_names = [RISK_DIMENSIONS.get(d, {}).get("name", d) for d in high_risk_dims[:3]]
            summary_parts.append(f"Key risk drivers: {', '.join(dim_names)}.")

    doc.add_paragraph(" ".join(summary_parts))


def _add_dimension_assessment(doc: Document, dimension_assessments: Dict[str, Any],
                              risk_level: str, risk_score: int):
    """Add risk assessment by dimension section."""
    doc.add_heading('2. RISK ASSESSMENT BY DIMENSION', level=1)

    # Important note about tunable parameters
    p = doc.add_paragraph()
    run = p.add_run('NOTE: ')
    run.bold = True
    p.add_run(
        'Risk dimensions and scoring weights below are exemplification. '
        'Institutions should tune these parameters to their risk appetite and governance framework.'
    )
    p.paragraph_format.space_after = Pt(12)

    # Create dimension assessment table
    table = doc.add_table(rows=7, cols=3)
    table.style = 'Light Grid Accent 1'

    # Header row
    table.rows[0].cells[0].text = 'Risk Dimension'
    table.rows[0].cells[1].text = 'Assessment'
    table.rows[0].cells[2].text = 'Core Question'

    # Data rows for each dimension
    for idx, dim_id in enumerate(DIMENSION_ORDER, 1):
        dim_info = get_dimension(dim_id)
        if not dim_info:
            continue

        dim_name = dim_info.get("name", dim_id)
        core_question = dim_info.get("core_question", "")

        # Get assessment for this dimension
        dim_assessment = dimension_assessments.get(dim_id, {})
        assessed_level = dim_assessment.get("risk_level", "Not Assessed")

        table.rows[idx].cells[0].text = dim_name
        table.rows[idx].cells[1].text = assessed_level
        table.rows[idx].cells[2].text = core_question

    doc.add_paragraph()

    # Overall score summary
    p = doc.add_paragraph()
    p.add_run('Overall Risk Score: ').bold = True
    run = p.add_run(f'{risk_score}/100 → {risk_level.upper()}')
    run.bold = True

    risk_colors = {
        "Critical": RGBColor(192, 0, 0),
        "High": RGBColor(255, 102, 0),
        "Medium": RGBColor(255, 192, 0),
        "Low": RGBColor(0, 128, 0)
    }
    run.font.color.rgb = risk_colors.get(risk_level, RGBColor(0, 0, 0))


def _add_lifecycle_requirements(doc: Document, current_stage: str,
                                stage_display: str, risk_level: str):
    """Add lifecycle requirements with checklist items for current stage."""
    doc.add_heading(f'3. {stage_display.upper()} STAGE REQUIREMENTS', level=1)

    # Get requirements for this stage and risk level
    stage_requirements = get_lifecycle_requirements_for_risk_level(current_stage, risk_level)

    if not stage_requirements:
        doc.add_paragraph(f'No specific requirements defined for {stage_display} stage.')
        return

    # Important note
    p = doc.add_paragraph()
    run = p.add_run('GOVERNANCE INTENSITY: ')
    run.bold = True
    p.add_run(
        f'Requirements below are scaled to {risk_level} risk level per OSFI Principle 2.3. '
        f'Higher risk models require more rigorous governance controls.'
    )
    p.paragraph_format.space_after = Pt(12)

    # Checklist items for each requirement area
    checklist_items = _get_checklist_items_for_stage(current_stage)

    for req_name, req_value in stage_requirements.items():
        # Format requirement name
        req_display = req_name.replace('_', ' ').title()

        # Add requirement heading
        p = doc.add_paragraph()
        p.add_run(f'{req_display}: ').bold = True
        p.add_run(req_value)

        # Add 1-2 checklist items for this requirement
        items = checklist_items.get(req_name, [])
        for item in items[:2]:  # Max 2 items per requirement
            p = doc.add_paragraph()
            p.add_run('☐ ').font.size = Pt(12)
            p.add_run(item)
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.space_after = Pt(4)

        doc.add_paragraph()

    # Stage transition note
    doc.add_paragraph()
    p = doc.add_paragraph()
    run = p.add_run('STAGE TRANSITION: ')
    run.bold = True
    run.font.color.rgb = RGBColor(192, 0, 0)

    next_stage = _get_next_stage(current_stage)
    if next_stage:
        p.add_run(
            f'Complete all {stage_display} requirements above before transitioning to {next_stage.capitalize()} stage.'
        )
    else:
        p.add_run('This is the final lifecycle stage. Ensure all decommission requirements are met.')


def _get_checklist_items_for_stage(stage: str) -> Dict[str, List[str]]:
    """Get checklist items for each requirement area in a stage."""

    # Define 1-2 checklist items per requirement area
    checklist_by_stage = {
        "design": {
            "documentation_depth": [
                "Document model rationale and business purpose",
                "Record design alternatives considered"
            ],
            "data_quality_assessment": [
                "Verify data sources meet quality standards",
                "Document data lineage and provenance"
            ],
            "bias_fairness_analysis": [
                "Screen for potential bias in training data",
                "Document fairness considerations"
            ],
            "approval_authority": [
                "Obtain required design approval",
                "Document approval in model inventory"
            ]
        },
        "review": {
            "validation_independence": [
                "Assign independent reviewer",
                "Document reviewer qualifications"
            ],
            "testing_scope": [
                "Execute required test suite",
                "Document test results and findings"
            ],
            "challenger_model": [
                "Develop challenger model (if required)",
                "Compare performance against primary model"
            ],
            "explainability_review": [
                "Validate model explainability",
                "Document explanation methodology"
            ],
            "approval_authority": [
                "Obtain validation sign-off",
                "Document approval for deployment"
            ]
        },
        "deployment": {
            "environment_verification": [
                "Verify production environment configuration",
                "Confirm integration points tested"
            ],
            "parallel_run_period": [
                "Execute parallel run (if required)",
                "Document parallel run results"
            ],
            "rollback_capability": [
                "Test rollback procedures",
                "Document rollback instructions"
            ],
            "human_override_controls": [
                "Implement override mechanisms",
                "Document override procedures"
            ],
            "go_live_approval": [
                "Obtain go-live approval",
                "Document deployment date and approver"
            ]
        },
        "monitoring": {
            "performance_review_frequency": [
                "Establish monitoring schedule",
                "Configure performance dashboards"
            ],
            "drift_monitoring": [
                "Implement drift detection",
                "Set drift alert thresholds"
            ],
            "fairness_monitoring": [
                "Monitor for disparate impact",
                "Track fairness metrics"
            ],
            "incident_escalation_time": [
                "Define escalation procedures",
                "Document escalation contacts"
            ],
            "revalidation_trigger": [
                "Define revalidation triggers",
                "Schedule periodic revalidation"
            ]
        },
        "decommission": {
            "retention_period": [
                "Archive model artifacts per retention policy",
                "Document retention start date"
            ],
            "documentation_to_retain": [
                "Compile final documentation package",
                "Store in approved archive location"
            ],
            "stakeholder_notification": [
                "Notify all stakeholders of retirement",
                "Document notification confirmations"
            ],
            "downstream_impact_review": [
                "Assess downstream system impacts",
                "Verify no residual dependencies"
            ]
        }
    }

    return checklist_by_stage.get(stage, {})


def _get_next_stage(current_stage: str) -> str:
    """Get the next lifecycle stage."""
    stage_order = ["design", "review", "deployment", "monitoring", "decommission"]
    try:
        idx = stage_order.index(current_stage)
        if idx < len(stage_order) - 1:
            return stage_order[idx + 1]
    except ValueError:
        pass
    return ""


def _add_annex_factor_assessment(doc: Document, dimension_assessments: Dict[str, Any],
                                  factor_scores: Dict[str, List[Dict[str, Any]]],
                                  validated_extraction: Dict[str, Any]):
    """
    Add Annex A with detailed factor assessment tables.

    Creates one table per dimension showing:
    - Factor name
    - Scoring matrix (Low/Medium/High/Critical thresholds)
    - Determined value with risk level
    - Evidence from project description
    """
    doc.add_heading('ANNEX A: DETAILED FACTOR ASSESSMENT', level=1)

    p = doc.add_paragraph()
    p.add_run(
        'This annex provides full transparency into the risk assessment by showing each factor, '
        'the scoring criteria, the determined value, and the evidence extracted from the project description.'
    )
    p.paragraph_format.space_after = Pt(12)

    # Get extracted dimensions data
    extracted_dims = validated_extraction.get("dimensions", {})

    # Create a table for each dimension
    for dim_id in DIMENSION_ORDER:
        dim_info = get_dimension(dim_id)
        if not dim_info:
            continue

        dim_name = dim_info.get("name", dim_id)
        dim_assessment = dimension_assessments.get(dim_id, {})
        dim_risk_level = dim_assessment.get("risk_level", "Not Assessed")
        dim_score = dim_assessment.get("numeric_score", 0)
        not_stated_count = dim_assessment.get("not_stated_count", 0)

        # Dimension header
        doc.add_heading(f'{dim_name}', level=2)

        # Dimension summary
        p = doc.add_paragraph()
        p.add_run('Dimension Risk Level: ').bold = True
        run = p.add_run(f'{dim_risk_level}')
        run.bold = True
        risk_colors = {
            "Critical": RGBColor(192, 0, 0),
            "High": RGBColor(255, 102, 0),
            "Medium": RGBColor(255, 192, 0),
            "Low": RGBColor(0, 128, 0)
        }
        run.font.color.rgb = risk_colors.get(dim_risk_level, RGBColor(0, 0, 0))

        if not_stated_count > 0:
            p.add_run(f' ({not_stated_count} factor(s) NOT_STATED, defaulted to Medium)')

        p.paragraph_format.space_after = Pt(8)

        # Get factors for this dimension
        factors = get_dimension_factors(dim_id)
        if not factors:
            doc.add_paragraph('No factors defined for this dimension.')
            continue

        # Get factor scores for this dimension
        dim_factor_scores = factor_scores.get(dim_id, [])
        # Get extracted values for this dimension
        dim_extracted = extracted_dims.get(dim_id, {})

        # DIAGNOSTIC: Log factor scores for this dimension
        logger.info(f"Annex A - {dim_id}: dim_factor_scores has {len(dim_factor_scores)} items")
        if dim_factor_scores:
            factor_ids_in_scores = [fs.get("factor_id") for fs in dim_factor_scores]
            logger.info(f"  Factor IDs in scores: {factor_ids_in_scores}")

        # Create factor table
        # Columns: Factor | Scoring Matrix | Determined Value | Evidence
        table = doc.add_table(rows=len(factors) + 1, cols=4)
        table.style = 'Light Grid Accent 1'

        # Header row
        header_cells = table.rows[0].cells
        header_cells[0].text = 'Factor'
        header_cells[1].text = 'Scoring Matrix'
        header_cells[2].text = 'Determined Value'
        header_cells[3].text = 'Evidence'

        # Make headers bold
        for cell in header_cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.bold = True

        # Data rows
        for idx, factor in enumerate(factors, 1):
            factor_id = factor.get("id", "")
            factor_name = factor.get("name", factor_id)
            factor_type = factor.get("type", "qualitative")

            # Build scoring matrix text
            if factor_type == "quantitative":
                thresholds = factor.get("thresholds", {})
                matrix_parts = []
                for level in ["low", "medium", "high", "critical"]:
                    thresh = thresholds.get(level, {})
                    desc = thresh.get("description", "N/A")
                    matrix_parts.append(f"{level.title()}: {desc}")
                scoring_matrix = "\n".join(matrix_parts)
            else:
                levels = factor.get("levels", {})
                matrix_parts = []
                for level in ["low", "medium", "high", "critical"]:
                    desc = levels.get(level, "N/A")
                    matrix_parts.append(f"{level.title()}: {desc}")
                scoring_matrix = "\n".join(matrix_parts)

            # Get determined value from factor scores
            factor_score_data = None
            for fs in dim_factor_scores:
                if fs.get("factor_id") == factor_id:
                    factor_score_data = fs
                    break

            if factor_score_data:
                # Note: factor_score_data uses "value" key (not "extracted_value")
                extracted_value = factor_score_data.get("value")
                is_not_stated = factor_score_data.get("is_not_stated", False)
                risk_level = factor_score_data.get("risk_level", "medium")

                if is_not_stated or extracted_value is None:
                    determined_value = "NOT_STATED\n(Medium - default)"
                else:
                    determined_value = f"{extracted_value}\n({risk_level.title()})"

                # Evidence is stored directly in factor_score_data (added during scoring)
                evidence = factor_score_data.get("evidence", "")
            else:
                determined_value = "Not Assessed"
                evidence = ""

            # Fallback: also check validated_extraction if evidence not in factor_score
            if not evidence:
                # validated_extraction has structure: dimensions[dim_id].factors[factor_id]
                dim_factors = dim_extracted.get("factors", {})
                factor_extracted = dim_factors.get(factor_id, {})
                evidence = factor_extracted.get("evidence", "")

            # Populate row
            row_cells = table.rows[idx].cells
            row_cells[0].text = factor_name
            row_cells[1].text = scoring_matrix
            row_cells[2].text = determined_value
            row_cells[3].text = evidence if evidence else ""

            # Set smaller font for scoring matrix column
            for paragraph in row_cells[1].paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(8)

        doc.add_paragraph()  # Space between dimension tables


def _add_annex_principles(doc: Document):
    """Add Annex B with OSFI E-23 principles."""
    doc.add_heading('ANNEX B: OSFI E-23 PRINCIPLES', level=1)

    p = doc.add_paragraph()
    run = p.add_run('Reference: ')
    run.bold = True
    p.add_run('OSFI Guideline E-23 – Model Risk Management (2027)')
    p.paragraph_format.space_after = Pt(12)

    # Organize principles by Outcome
    outcomes = {
        "1": ["1.1", "1.2", "1.3"],
        "2": ["2.1", "2.2", "2.3"],
        "3": ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6"]
    }

    outcome_titles = {
        "1": "Model risk is well understood and managed across the enterprise",
        "2": "Model risk is managed using a risk-based approach",
        "3": "Model governance covers the entire model lifecycle"
    }

    for outcome_num, principles in outcomes.items():
        # Outcome header
        p = doc.add_paragraph()
        run = p.add_run(f'OUTCOME {outcome_num}: {outcome_titles[outcome_num]}')
        run.bold = True
        run.font.size = Pt(11)
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)

        # Principles under this outcome
        for principle_num in principles:
            principle_text = OSFI_PRINCIPLES.get(principle_num, "")
            p = doc.add_paragraph()
            p.add_run(f'Principle {principle_num}: ').bold = True
            p.add_run(principle_text)
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.space_after = Pt(4)

    doc.add_paragraph()


# Backwards compatibility wrapper
def generate_design_stage_report(
    project_name: str,
    project_description: str,
    assessment_results: Dict[str, Any],
    doc: Document
) -> Document:
    """Backwards compatibility wrapper - defaults to Design stage."""
    return generate_osfi_e23_report(
        project_name=project_name,
        project_description=project_description,
        assessment_results=assessment_results,
        doc=doc,
        current_stage="design"
    )
