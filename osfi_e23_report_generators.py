"""
OSFI E-23 Report Generation - Lifecycle Stage Specific

Generates OSFI E-23 compliance reports organized by current lifecycle stage.
Focused on Design stage initially (most common use case).
"""

from docx import Document
from docx.shared import Pt, RGBColor
from datetime import datetime
from typing import Dict, Any, List
import logging

from osfi_e23_structure import (
    OSFI_PRINCIPLES,
    OSFI_OUTCOMES,
    OSFI_LIFECYCLE_COMPONENTS,
    APPENDIX_1_REQUIRED_FIELDS,
    APPENDIX_1_OPTIONAL_FIELDS,
    detect_lifecycle_stage,
    get_design_stage_checklist,
    get_stage_name,
    get_stage_principles,
    get_principle_text,
    is_ai_ml_model
)

logger = logging.getLogger(__name__)

def generate_design_stage_report(
    project_name: str,
    project_description: str,
    assessment_results: Dict[str, Any],
    doc: Document
) -> Document:
    """
    Generate comprehensive Design stage compliance report.

    Focuses only on Design stage requirements (OSFI Principles 3.2 and 3.3).
    Includes OSFI Appendix 1 fields, stage-specific checklist, gap analysis,
    and readiness assessment for Review stage.

    Args:
        project_name: Name of the model/project
        project_description: Detailed project description
        assessment_results: Assessment data from assess_model_risk
        doc: python-docx Document object

    Returns:
        Document: Populated Word document
    """
    # Title
    title = doc.add_heading('OSFI E-23 Model Risk Management Assessment', 0)
    title.alignment = 1  # Center

    subtitle = doc.add_heading(f'{project_name} - Design Stage Compliance Report', 1)
    subtitle.alignment = 1

    doc.add_paragraph()  # Spacing

    # Executive Summary
    _add_design_stage_executive_summary(doc, project_name, assessment_results)

    # 1. Model Information Profile (OSFI Appendix 1)
    _add_model_information_profile(doc, project_name, assessment_results, stage="design")

    # 2. Current Lifecycle Stage: Model Design
    _add_design_stage_assessment(doc, project_description, assessment_results)

    # 3. Design Stage Compliance Checklist
    _add_design_stage_checklist(doc, project_description, assessment_results)

    # 4. Design Stage Gap Analysis
    _add_design_stage_gap_analysis(doc, assessment_results)

    # 5. Readiness Assessment for Model Review Stage
    _add_review_stage_readiness(doc, assessment_results)

    # 6. Institution's Risk Rating Summary
    _add_risk_rating_summary(doc, assessment_results)

    # 7. OSFI E-23 Principles Mapping
    _add_osfi_principles_mapping_design(doc, assessment_results)

    # 8. Implementation Roadmap
    _add_implementation_roadmap_design(doc, assessment_results)

    # 9. Critical Recommendations & Next Steps
    _add_critical_recommendations_next_steps(doc, assessment_results, project_description)

    # 10. Model Description
    doc.add_heading('10. Model Description', level=1)
    doc.add_paragraph(project_description)

    # Appendices
    _add_appendices_design_stage(doc)

    # Professional Validation Warning
    _add_professional_validation_warning(doc, stage="design")

    return doc


def _add_design_stage_executive_summary(
    doc: Document,
    project_name: str,
    assessment_results: Dict[str, Any]
):
    """Add enhanced executive summary for Design stage report."""
    doc.add_heading('Executive Summary', level=1)

    # Opening narrative
    risk_level = assessment_results.get("risk_level", "Not Assessed")
    risk_score = assessment_results.get("risk_score", 0)

    opening_text = (
        f'{project_name} has been assessed against OSFI Guideline E-23 Model Risk Management '
        f'requirements for federally regulated financial institutions in Canada. The model is currently '
        f'in the Design stage of the OSFI E-23 lifecycle.'
    )
    doc.add_paragraph(opening_text)
    doc.add_paragraph()  # Spacing

    # Critical Risk Assessment Results Box
    doc.add_heading('Critical Risk Assessment Results', level=2)

    p = doc.add_paragraph()
    p.add_run('Institution Risk Rating: ').bold = True
    run = p.add_run(f'{risk_level}')
    run.bold = True
    if risk_level in ['Critical', 'High']:
        run.font.color.rgb = RGBColor(220, 20, 60)  # Crimson for high risk

    p = doc.add_paragraph()
    p.add_run('Risk Score: ').bold = True
    p.add_run(f'{risk_score}/100 (per institution\'s risk rating methodology - Principle 2.2)')

    p = doc.add_paragraph()
    p.add_run('Current Lifecycle Stage: ').bold = True
    p.add_run('Design')

    p = doc.add_paragraph()
    p.add_run('Assessment Date: ').bold = True
    p.add_run(datetime.now().strftime("%B %d, %Y"))

    doc.add_paragraph()  # Spacing

    # Key Risk Factors Identified
    doc.add_heading('Key Risk Factors Identified', level=2)
    risk_analysis = assessment_results.get("risk_analysis", {})
    quant_indicators = risk_analysis.get("quantitative_indicators", {})
    qual_indicators = risk_analysis.get("qualitative_indicators", {})

    risk_factors = []

    # Quantitative factors
    if quant_indicators.get("financial_impact"):
        risk_factors.append("Financial Impact: Model directly impacts financial decisions and outcomes")
    if quant_indicators.get("regulatory_impact"):
        risk_factors.append("Regulatory Impact: Model affects regulatory compliance and reporting requirements")
    if quant_indicators.get("customer_facing"):
        risk_factors.append("Customer-Facing: Direct impact on customer decisions and outcomes")
    if quant_indicators.get("high_volume"):
        risk_factors.append("High Volume: Large-scale deployment affecting significant transaction volumes")
    if quant_indicators.get("revenue_critical"):
        risk_factors.append("Revenue Critical: Model directly impacts revenue generation or business operations")

    # Qualitative factors
    if qual_indicators.get("ai_ml_usage"):
        risk_factors.append("AI/ML Usage: Complex machine learning architecture requiring specialized oversight")
    if qual_indicators.get("high_complexity"):
        risk_factors.append("High Complexity: Sophisticated model structure and methodology")
    if qual_indicators.get("third_party"):
        risk_factors.append("Third-Party Dependencies: Reliance on external vendors or data providers")
    if qual_indicators.get("data_sensitive"):
        risk_factors.append("Sensitive Data: Processing personal or confidential information")
    if qual_indicators.get("autonomous_decisions"):
        risk_factors.append("Autonomous Decisions: Automated decision-making with limited human intervention")
    if qual_indicators.get("real_time"):
        risk_factors.append("Real-Time Processing: Immediate decision requirements")
    if qual_indicators.get("black_box"):
        risk_factors.append("Limited Explainability: Complex algorithms requiring enhanced transparency measures")

    if risk_factors:
        for factor in risk_factors:
            doc.add_paragraph(f'• {factor}', style='List Bullet')
    else:
        doc.add_paragraph('Risk factors to be determined through detailed assessment.')

    doc.add_paragraph()  # Spacing

    # Design Stage Status
    doc.add_heading('Design Stage Compliance Status', level=2)
    doc.add_paragraph(
        'This assessment evaluates compliance against OSFI E-23 Principles 3.2 (Model Rationale and Data) '
        'and 3.3 (Model Development). The model is currently in the Design stage, focusing on establishing '
        'clear organizational rationale, data governance, and development methodology per OSFI requirements.'
    )

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run('⚠️ Note: ').bold = True
    p.add_run(
        'Formal completion tracking and gap analysis require comprehensive documentation review by qualified '
        'model risk professionals. This assessment is based on available project information.'
    )


def _add_model_information_profile(
    doc: Document,
    project_name: str,
    assessment_results: Dict[str, Any],
    stage: str
):
    """Add OSFI Appendix 1 model tracking fields."""
    doc.add_heading('1. Model Information Profile (OSFI Appendix 1)', level=1)

    doc.add_paragraph(
        'OSFI E-23 Appendix 1 specifies required tracking fields for all models in the institution\'s model inventory.'
    )

    # Required Tracking Fields
    doc.add_heading('Required Tracking Fields', level=2)

    fields = [
        ('Model ID', assessment_results.get('model_id', '[To be assigned by institution]')),
        ('Model Name', project_name),
        ('Model Description', assessment_results.get('model_description', '[Brief description of key features and use]')),
        ('Business Line', assessment_results.get('business_line', '[Business line/unit to be assigned]')),
        ('Model Owner', assessment_results.get('model_owner', '[Individual/unit to be assigned]')),
        ('Model Developer', assessment_results.get('model_developer', '[Individual/unit/vendor to be assigned]')),
        ('Model Origin', assessment_results.get('model_origin', '[Internal/Vendor/Third-party]')),
        ('Current Lifecycle Stage', 'Design'),
        ('Provisional Model Risk Rating', f'{assessment_results.get("risk_level", "[To be assigned]")} (to be confirmed in Review stage)')
    ]

    for field_name, field_value in fields:
        p = doc.add_paragraph()
        p.add_run(f'{field_name}: ').bold = True
        p.add_run(field_value)

    # Future Tracking Fields
    doc.add_heading('Future Tracking Fields (to be completed in later stages)', level=2)

    future_fields = [
        ('Model Version', 'TBD - assigned at deployment'),
        ('Date of Deployment', 'TBD - Deployment stage'),
        ('Model Reviewer', 'TBD - to be assigned for Review stage'),
        ('Model Approver', 'TBD - to be assigned'),
        ('Date of Most Recent Review', 'TBD - after Review stage'),
        ('Next Review Date', 'TBD - based on risk rating'),
        ('Monitoring Status', 'TBD - Monitoring stage')
    ]

    for field_name, field_value in future_fields:
        p = doc.add_paragraph()
        p.add_run(f'{field_name}: ').bold = True
        p.add_run(field_value)


def _add_design_stage_assessment(
    doc: Document,
    project_description: str,
    assessment_results: Dict[str, Any]
):
    """Add current lifecycle stage assessment section."""
    doc.add_heading('2. Current Lifecycle Stage: Model Design', level=1)

    doc.add_paragraph(
        'OSFI E-23 defines Model Design as encompassing:'
    )

    components = [
        'Model Rationale - establishing clear organizational rationale',
        'Model Data - ensuring data quality and suitability',
        'Model Development - following appropriate development processes'
    ]

    for component in components:
        doc.add_paragraph(component, style='List Number')

    # Model Rationale Compliance
    doc.add_heading('2.1 Model Rationale Compliance (Principle 3.2)', level=2)

    doc.add_paragraph().add_run('Requirements:').bold = True
    requirements = [
        'Clear organizational rationale for model deployment',
        'Well-defined purpose, scope, and coverage',
        'Identified business use case',
        'Risk assessment of intended usage'
    ]

    if is_ai_ml_model(project_description):
        requirements.extend([
            '[For AI/ML] Explainability requirements',
            '[For AI/ML] Bias considerations',
            '[For AI/ML] Privacy risks'
        ])

    for req in requirements:
        doc.add_paragraph(req, style='List Bullet')

    doc.add_paragraph().add_run('Current Status: ').bold = True
    doc.add_paragraph('[Assessment based on available information - formal status tracking requires documentation review]')

    # Model Data Compliance
    doc.add_heading('2.2 Model Data Compliance (Principle 3.2)', level=2)

    doc.add_paragraph().add_run('Requirements:').bold = True
    data_reqs = [
        'Data governance framework integrated with enterprise standards',
        'Data quality standards (accuracy, relevance, representativeness, compliance, traceability, timeliness)',
        'Data sources documented with lineage and provenance',
        'Data quality check procedures defined',
        'Bias assessment and management approach',
        'Data update frequency established'
    ]

    for req in data_reqs:
        doc.add_paragraph(req, style='List Bullet')

    doc.add_paragraph().add_run('Current Status: ').bold = True
    doc.add_paragraph('[Assessment based on available information - formal status tracking requires documentation review]')

    # Model Development Compliance
    doc.add_heading('2.3 Model Development Compliance (Principle 3.3)', level=2)

    doc.add_paragraph().add_run('Requirements:').bold = True
    dev_reqs = [
        'Model methodology documented (conceptually sound methodologies, algorithms)',
        'Model assumptions and limitations documented',
        'Development processes documented',
        'Expert judgment role documented',
        'Performance criteria established',
        'Development testing documented',
        'Model output usage standards defined',
        'Planning for future stages: Monitoring criteria, review standards, performance thresholds defined'
    ]

    for req in dev_reqs:
        doc.add_paragraph(req, style='List Bullet')

    doc.add_paragraph().add_run('Current Status: ').bold = True
    doc.add_paragraph('[Assessment based on available information - formal status tracking requires documentation review]')


def _add_design_stage_checklist(
    doc: Document,
    project_description: str,
    assessment_results: Dict[str, Any]
):
    """Add comprehensive Design stage compliance checklist."""
    doc.add_heading('3. Design Stage Compliance Checklist', level=1)

    checklist = get_design_stage_checklist()
    is_ai_ml = is_ai_ml_model(project_description)

    # Model Rationale
    doc.add_heading('Model Rationale (Principle 3.2 - Model Design)', level=2)
    for item in checklist["model_rationale"]:
        # Skip AI/ML specific items if not AI/ML model
        if item.get("ai_ml_specific") and not is_ai_ml:
            continue

        p = doc.add_paragraph('☐ ', style='List Bullet')
        p.add_run(item["item"]).bold = True
        p = doc.add_paragraph(f'  Requirement: {item["requirement"]}', style='List Bullet 2')
        p = doc.add_paragraph(f'  Deliverable: {item["deliverable"]}', style='List Bullet 2')
        p = doc.add_paragraph(f'  OSFI Reference: {item["osfi_reference"]}', style='List Bullet 2')

    # Model Data
    doc.add_heading('Model Data (Principle 3.2 - Model Data)', level=2)
    for item in checklist["model_data"]:
        p = doc.add_paragraph('☐ ', style='List Bullet')
        p.add_run(item["item"]).bold = True
        p = doc.add_paragraph(f'  Requirement: {item["requirement"]}', style='List Bullet 2')
        p = doc.add_paragraph(f'  Deliverable: {item["deliverable"]}', style='List Bullet 2')
        p = doc.add_paragraph(f'  OSFI Reference: {item["osfi_reference"]}', style='List Bullet 2')

    # Model Development
    doc.add_heading('Model Development (Principle 3.3 - Model Development)', level=2)
    for item in checklist["model_development"]:
        p = doc.add_paragraph('☐ ', style='List Bullet')
        p.add_run(item["item"]).bold = True
        p = doc.add_paragraph(f'  Requirement: {item["requirement"]}', style='List Bullet 2')
        p = doc.add_paragraph(f'  Deliverable: {item["deliverable"]}', style='List Bullet 2')
        p = doc.add_paragraph(f'  OSFI Reference: {item["osfi_reference"]}', style='List Bullet 2')

    # Planning for Future Stages
    doc.add_heading('Planning for Future Stages (Design Stage Deliverables)', level=2)
    doc.add_paragraph('Note: These are Design stage requirements that define approaches for future implementation')

    for item in checklist["planning_for_future"]:
        p = doc.add_paragraph('☐ ', style='List Bullet')
        p.add_run(item["item"]).bold = True
        p = doc.add_paragraph(f'  Requirement: {item["requirement"]}', style='List Bullet 2')
        p = doc.add_paragraph(f'  Deliverable: {item["deliverable"]}', style='List Bullet 2')
        p = doc.add_paragraph(f'  OSFI Reference: {item["osfi_reference"]}', style='List Bullet 2')
        p = doc.add_paragraph(f'  Future Stage: {item["future_stage"].capitalize()}', style='List Bullet 2')

    # Design Stage Governance
    doc.add_heading('Design Stage Governance (OSFI Appendix 1)', level=2)
    for item in checklist["design_governance"]:
        p = doc.add_paragraph('☐ ', style='List Bullet')
        p.add_run(item["item"]).bold = True
        p = doc.add_paragraph(f'  Requirement: {item["requirement"]}', style='List Bullet 2')
        p = doc.add_paragraph(f'  OSFI Reference: {item["osfi_reference"]}', style='List Bullet 2')

    # Readiness for Review Stage
    doc.add_heading('Readiness for Model Review Stage', level=2)
    for item in checklist["readiness_for_review"]:
        p = doc.add_paragraph('☐ ', style='List Bullet')
        p.add_run(item["item"]).bold = True
        p = doc.add_paragraph(f'  Requirement: {item["requirement"]}', style='List Bullet 2')
        p = doc.add_paragraph(f'  OSFI Reference: {item["osfi_reference"]}', style='List Bullet 2')


def _add_design_stage_gap_analysis(doc: Document, assessment_results: Dict[str, Any]):
    """Add gap analysis section."""
    doc.add_heading('4. Design Stage Gap Analysis', level=1)

    doc.add_paragraph(
        'Comprehensive gap analysis requires detailed documentation review against each Design stage deliverable. '
        'This section provides framework for systematic gap identification.'
    )

    doc.add_heading('Critical Gaps', level=2)
    doc.add_paragraph('[Gaps preventing completion of Design stage - to be identified through documentation review]')

    doc.add_heading('Medium Priority Gaps', level=2)
    doc.add_paragraph('[Gaps that should be addressed before Review stage - to be identified through documentation review]')

    doc.add_heading('Documentation Gaps', level=2)
    doc.add_paragraph('[Missing documentation with deliverable names - to be identified through documentation review]')


def _add_review_stage_readiness(doc: Document, assessment_results: Dict[str, Any]):
    """Add readiness assessment for next stage."""
    doc.add_heading('5. Readiness Assessment for Model Review Stage', level=1)

    doc.add_heading('Prerequisites for Review Stage Entry (Principle 3.4)', level=2)

    doc.add_paragraph().add_run('Design Stage Completion:').bold = True
    completion_items = [
        'All Design stage deliverables complete',
        'Model documentation meets standards for independent review',
        'Model limitations and restrictions documented',
        'Performance criteria and monitoring standards defined'
    ]
    for item in completion_items:
        doc.add_paragraph(f'☐ {item}', style='List Bullet')

    doc.add_paragraph().add_run('Review Stage Setup:').bold = True
    setup_items = [
        'Model reviewer identified and assigned',
        'Review scope and criteria defined based on model risk rating (Principle 2.3)',
        'Review schedule established commensurate with risk rating',
        'Independence requirements confirmed'
    ]
    for item in setup_items:
        doc.add_paragraph(f'☐ {item}', style='List Bullet')

    doc.add_paragraph().add_run('Current Readiness: ').bold = True
    doc.add_paragraph('[Formal readiness assessment requires completion verification of all Design stage deliverables]')


def _add_risk_rating_summary(doc: Document, assessment_results: Dict[str, Any]):
    """Add institution's risk rating summary."""
    doc.add_heading('6. Institution\'s Risk Rating Summary', level=1)

    risk_level = assessment_results.get("risk_level", "Not Assessed")
    risk_score = assessment_results.get("risk_score", 0)

    doc.add_heading('Risk Rating Methodology', level=2)
    doc.add_paragraph(
        'OSFI E-23 Principle 2.2 requires institutions to establish their own model risk rating approach '
        'that assesses key dimensions of model risk. The risk rating and scoring shown below are based '
        'on the institution\'s defined methodology.'
    )

    doc.add_paragraph().add_run('Assigned Risk Rating: ').bold = True
    doc.add_paragraph(f'{risk_level}')

    doc.add_paragraph().add_run('Risk Score: ').bold = True
    doc.add_paragraph(f'{risk_score}/100 (using institution\'s scoring framework)')

    doc.add_heading('Governance Intensity Implications (Principle 2.3)', level=2)
    doc.add_paragraph(
        'Based on the assigned risk rating, the following governance intensity applies. '
        'These are illustrative examples - actual requirements determined by institution\'s MRM framework.'
    )


def _add_osfi_principles_mapping_design(doc: Document, assessment_results: Dict[str, Any]):
    """Add OSFI Principles mapping table."""
    doc.add_heading('7. OSFI E-23 Principles Mapping - Design Stage', level=1)

    doc.add_paragraph(
        'Mapping of OSFI E-23 Principles to Design stage requirements. '
        'Formal compliance tracking requires detailed documentation review.'
    )

    # Add table
    table = doc.add_table(rows=1, cols=4)
    table.style = 'Light Grid Accent 1'

    # Header row
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'OSFI Principle'
    hdr_cells[1].text = 'Design Stage Requirement'
    hdr_cells[2].text = 'Compliance Status'
    hdr_cells[3].text = 'Evidence/Gaps'

    # Data rows
    principles_mapping = [
        ('Principle 1.2', 'MRM framework alignment', '[To be assessed]', '[Documentation review required]'),
        ('Principle 2.1', 'Model identification and provisional rating', '[To be assessed]', '[Documentation review required]'),
        ('Principle 2.2', 'Risk rating methodology application', '[To be assessed]', '[Documentation review required]'),
        ('Principle 3.2 (Rationale)', 'Clear organizational rationale', '[To be assessed]', '[Documentation review required]'),
        ('Principle 3.2 (Data)', 'Data governance and suitability', '[To be assessed]', '[Documentation review required]'),
        ('Principle 3.3', 'Development standards and documentation', '[To be assessed]', '[Documentation review required]')
    ]

    for principle, requirement, status, evidence in principles_mapping:
        row_cells = table.add_row().cells
        row_cells[0].text = principle
        row_cells[1].text = requirement
        row_cells[2].text = status
        row_cells[3].text = evidence

    doc.add_paragraph()  # Spacing

    # Compliance Legend
    doc.add_paragraph().add_run('Compliance Legend:').bold = True
    legend = [
        '✅ Compliant: Requirement fully met with documented evidence',
        '⚠️ Partial: Requirement partially met, gaps identified',
        '❌ Non-Compliant: Requirement not met',
        'N/A: Not applicable at this stage'
    ]
    for item in legend:
        doc.add_paragraph(item, style='List Bullet')


def _add_implementation_roadmap_design(doc: Document, assessment_results: Dict[str, Any]):
    """Add implementation roadmap."""
    doc.add_heading('8. Implementation Roadmap - Design Stage Completion', level=1)

    doc.add_paragraph(
        'Recommended phased approach to completing Design stage requirements. '
        'Specific actions and timelines determined through detailed gap analysis.'
    )

    doc.add_heading('Immediate Actions (Next 30 Days)', level=2)
    doc.add_paragraph('[Actions to address critical gaps - to be defined through gap analysis]')

    doc.add_heading('Short-Term Actions (30-90 Days)', level=2)
    doc.add_paragraph('[Actions to complete Design stage - to be defined through gap analysis]')

    doc.add_heading('Design Stage Completion Target', level=2)
    doc.add_paragraph().add_run('Target Date: ').bold = True
    doc.add_paragraph('[To be determined based on gap analysis]')

    doc.add_paragraph().add_run('Success Criteria: ').bold = True
    doc.add_paragraph('All Design stage deliverables complete and documented per OSFI Principles 3.2 and 3.3')


def _add_critical_recommendations_next_steps(
    doc: Document,
    assessment_results: Dict[str, Any],
    project_description: str
):
    """Add critical recommendations and immediate next steps section."""
    doc.add_heading('9. Critical Recommendations & Next Steps', level=1)

    risk_level = assessment_results.get("risk_level", "Not Assessed")
    risk_analysis = assessment_results.get("risk_analysis", {})
    quant_indicators = risk_analysis.get("quantitative_indicators", {})
    qual_indicators = risk_analysis.get("qualitative_indicators", {})
    recommendations = assessment_results.get("recommendations", [])

    # Immediate Actions Required
    doc.add_heading('Immediate Actions Required', level=2)

    immediate_actions = []

    # Critical risk level actions
    if risk_level in ['Critical', 'High']:
        immediate_actions.append(
            '🔴 CRITICAL: Obtain Board of Directors (or equivalent senior authority) approval before '
            'proceeding to Review stage (required for Critical/High risk models per Principle 2.3)'
        )

    # Design stage completion actions
    immediate_actions.append(
        '📋 Complete Design stage documentation: Finalize all required deliverables per Principles 3.2 and 3.3'
    )

    # Data governance actions
    if qual_indicators.get("data_sensitive") or qual_indicators.get("ai_ml_usage"):
        immediate_actions.append(
            '📊 Establish comprehensive data governance framework: Document data quality standards, '
            'lineage, validation procedures, and ongoing monitoring per Principle 3.2'
        )

    # Model Risk Committee
    if risk_level in ['Critical', 'High']:
        immediate_actions.append(
            '👥 Establish Model Risk Committee: Form dedicated committee with senior management '
            'representation and clear governance mandate per Principle 1.2'
        )

    # External validation
    if risk_level == 'Critical':
        immediate_actions.append(
            '🔍 Engage external validator: Select and contract independent third-party validation firm '
            'for mandatory external validation (required for Critical risk models per Principle 3.4)'
        )

    # AI/ML specific actions
    if qual_indicators.get("ai_ml_usage"):
        immediate_actions.append(
            '🤖 Conduct comprehensive bias and fairness testing: Implement assessment framework '
            'across all relevant dimensions per Principle 3.2'
        )
        immediate_actions.append(
            '📖 Develop explainability framework: Document model interpretability approach, '
            'including SHAP values, feature importance, and decision transparency per Principle 3.2'
        )

    # Third-party actions
    if qual_indicators.get("third_party"):
        immediate_actions.append(
            '🤝 Document third-party dependencies: Establish vendor risk management controls '
            'and contractual safeguards per Principle 3.2'
        )

    for action in immediate_actions:
        doc.add_paragraph(action, style='List Bullet')

    doc.add_paragraph()  # Spacing

    # Ongoing Governance Requirements
    doc.add_heading('Ongoing Governance Requirements', level=2)

    ongoing_requirements = [
        '📊 Implement real-time monitoring infrastructure with automated alert thresholds',
        '📝 Establish contingency and rollback procedures for model failures',
        '📅 Define and document periodic review schedule based on risk rating per Principle 2.3',
        '✅ Maintain comprehensive audit trail of all model changes and decisions',
        '📢 Establish clear escalation protocols for risk issues'
    ]

    # Add risk-specific ongoing requirements
    if risk_level == 'Critical':
        ongoing_requirements.append(
            '📈 Monthly Model Risk Committee reporting (mandatory for Critical risk models)'
        )
        ongoing_requirements.append(
            '📊 Quarterly Board of Directors updates (mandatory for Critical risk models)'
        )
        ongoing_requirements.append(
            '🔍 Annual independent third-party validation (mandatory for Critical risk models)'
        )
    elif risk_level == 'High':
        ongoing_requirements.append(
            '📈 Quarterly Model Risk Committee reporting (mandatory for High risk models)'
        )
        ongoing_requirements.append(
            '📊 Semi-annual Board updates (recommended for High risk models)'
        )

    for requirement in ongoing_requirements:
        doc.add_paragraph(requirement, style='List Bullet')

    doc.add_paragraph()  # Spacing

    # Success Criteria for Design Stage Completion
    doc.add_heading('Success Criteria for Design Stage Completion', level=2)

    success_criteria = [
        '✅ All OSFI Appendix 1 tracking fields populated',
        '✅ Model rationale clearly documented per Principle 3.2',
        '✅ Data governance framework established per Principle 3.2',
        '✅ Development methodology documented per Principle 3.3',
        '✅ Performance criteria and success metrics defined',
        '✅ Independent Review stage scope and criteria agreed',
        '✅ Appropriate governance authority approval obtained',
        '✅ All Design stage compliance checklist items addressed'
    ]

    for criterion in success_criteria:
        doc.add_paragraph(criterion, style='List Bullet')

    doc.add_paragraph()  # Spacing

    # Next Major Milestone
    doc.add_heading('Next Major Milestone', level=2)

    p = doc.add_paragraph()
    p.add_run('Milestone: ').bold = True
    p.add_run('Transition to Model Review Stage (Principle 3.4)')

    doc.add_paragraph(
        'Upon completion of all Design stage requirements, the model will proceed to the Review stage '
        'for independent validation per OSFI E-23 Principle 3.4. The Review stage requires independent '
        'assessment by qualified personnel separate from model development, with scope and rigor '
        'commensurate with the model\'s risk rating.'
    )

    doc.add_paragraph()  # Spacing

    # Regulatory Compliance Reminder
    p = doc.add_paragraph()
    p.add_run('⚠️ REGULATORY COMPLIANCE REMINDER: ').bold = True
    run = p.add_run(
        'All activities must comply with OSFI Guideline E-23 requirements. This assessment provides '
        'guidance but does not replace professional validation by qualified model risk management personnel. '
        'Obtain appropriate governance approvals before implementing recommendations.'
    )
    run.font.color.rgb = RGBColor(139, 69, 19)  # Saddle brown for warnings


def _add_appendices_design_stage(doc: Document):
    """Add appendices section."""
    doc.add_heading('Appendices', level=1)

    doc.add_heading('Appendix A: OSFI E-23 Design Stage Requirements Summary', level=2)
    doc.add_paragraph('Quick reference of all Principle 3.2 and 3.3 requirements')
    doc.add_paragraph('[Detailed requirements list from checklist section]')

    doc.add_heading('Appendix B: Required Documentation Checklist', level=2)
    doc.add_paragraph('List of all documents that should exist by end of Design stage:')

    docs_list = [
        'Model Rationale Document',
        'Model Purpose and Scope Statement',
        'Business Use Case Documentation',
        'Data Governance Documentation',
        'Data Quality Standards Document',
        'Model Methodology Documentation',
        'Model Assumptions Document',
        'Performance Criteria Document',
        '[Additional deliverables per checklist]'
    ]

    for doc_name in docs_list:
        doc.add_paragraph(doc_name, style='List Bullet')

    doc.add_heading('Appendix C: OSFI E-23 Guideline References', level=2)
    doc.add_paragraph().add_run('Guideline: ').bold = True
    doc.add_paragraph('OSFI E-23 – Model Risk Management (2027)')

    doc.add_paragraph().add_run('Effective Date: ').bold = True
    doc.add_paragraph('May 1, 2027')

    doc.add_paragraph().add_run('URL: ').bold = True
    doc.add_paragraph('https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027')


def _add_professional_validation_warning(doc: Document, stage: str):
    """Add professional validation warning."""
    doc.add_heading('⚠️ PROFESSIONAL VALIDATION REQUIRED', level=1)

    doc.add_paragraph(
        f'This OSFI E-23 model risk assessment is based on available project information and '
        f'automated analysis of {stage.capitalize()} stage compliance.'
    )

    doc.add_heading('Important Notes:', level=2)
    notes = [
        'The risk rating shown is based on the institution\'s risk rating methodology as required by OSFI Principle 2.2',
        'Final compliance with OSFI Guideline E-23 requires comprehensive stakeholder input, independent validation, and appropriate governance oversight',
        'This assessment should be reviewed and validated by qualified model risk management professionals before making final risk management decisions',
        f'All {stage.capitalize()} stage deliverables must be reviewed by appropriate subject matter experts',
        'Transition to next lifecycle stage requires formal approval per institution\'s governance framework'
    ]

    for note in notes:
        doc.add_paragraph(note, style='List Bullet')
