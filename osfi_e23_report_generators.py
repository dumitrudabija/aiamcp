"""
OSFI E-23 Report Generation - Streamlined Standard Structure (v2.0)

Generates concise, professional OSFI E-23 compliance reports following
the standardized 4-section structure with consistent formatting.
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def generate_osfi_e23_report(
    project_name: str,
    project_description: str,
    assessment_results: Dict[str, Any],
    doc: Document,
    current_stage: str = "design",
    lifecycle_compliance: Dict[str, Any] = None,
    compliance_framework: Dict[str, Any] = None
) -> Document:
    """
    Generate streamlined OSFI E-23 stage-specific compliance report.

    Follows standard structure:
    1. Executive Summary
    2. Risk Rating Methodology
    3. Lifecycle Coverage Assessment (from Step 3)
    4. Stage-Specific Compliance Checklist (from Step 4)
    5. Governance Structure (from Step 2 and Step 4)
       5.1 Governance Roles and Responsibilities
       5.2 Documentation Requirements
       5.3 Review and Approval Procedures
    6. Monitoring Framework (from Step 4, if applicable)
    7. Annex: OSFI E-23 Principles

    Target: ~4-6 pages with clear, professional formatting.
    Stage-specific content ensures report only shows current stage requirements.
    """
    # Extract key data
    risk_level = assessment_results.get("risk_level", "Unknown")
    risk_score = assessment_results.get("risk_score", 0)
    risk_analysis = assessment_results.get("risk_analysis", {})
    assessment_date = datetime.now().strftime("%B %d, %Y")

    # Stage display name
    stage_display_names = {
        "design": "Design",
        "review": "Review",
        "deployment": "Deployment",
        "monitoring": "Monitoring",
        "decommission": "Decommission"
    }
    stage_display = stage_display_names.get(current_stage, "Design")

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

    # Professional validation disclaimer (beginning)
    _add_professional_validation_disclaimer(doc, position="beginning")

    doc.add_page_break()

    # 1. Executive Summary
    _add_executive_summary_with_disclaimer(doc, project_name, project_description, risk_level, risk_score, risk_analysis, stage_display)

    # 2. Risk Rating Methodology
    _add_risk_methodology(doc, risk_analysis, risk_level, risk_score)

    # 3. Lifecycle Coverage Assessment (Step 3)
    if lifecycle_compliance:
        _add_lifecycle_coverage_section(doc, lifecycle_compliance, current_stage, stage_display)

    # 4. Stage-Specific Compliance Checklist (Step 5)
    if compliance_framework and compliance_framework.get("osfi_elements"):
        _add_stage_compliance_checklist(doc, compliance_framework, current_stage, stage_display, risk_level)
    else:
        # Fallback to hardcoded Design checklist if Step 5 data not available
        _add_compliance_checklist(doc, project_description, risk_level, risk_score, stage_display)

    # 5. Governance Structure (Step 5)
    if compliance_framework and compliance_framework.get("governance_structure"):
        _add_governance_structure_section(doc, compliance_framework, assessment_results, risk_level)

    # 6. Monitoring Framework (Step 5 - if applicable)
    if compliance_framework and compliance_framework.get("monitoring_framework"):
        _add_monitoring_framework_section(doc, compliance_framework.get("monitoring_framework"))

    doc.add_page_break()

    # Annex: OSFI E-23 Principles
    _add_annex_principles(doc, current_stage)

    # Professional validation disclaimer (end)
    doc.add_page_break()
    _add_professional_validation_disclaimer(doc, position="end")

    return doc


# Backwards compatibility wrapper
def generate_design_stage_report(
    project_name: str,
    project_description: str,
    assessment_results: Dict[str, Any],
    doc: Document
) -> Document:
    """
    Backwards compatibility wrapper for generate_osfi_e23_report.
    Defaults to Design stage with no Step 3/5 data.
    """
    return generate_osfi_e23_report(
        project_name=project_name,
        project_description=project_description,
        assessment_results=assessment_results,
        doc=doc,
        current_stage="design",
        lifecycle_compliance=None,
        compliance_framework=None
    )


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
    if risk_level == "Critical":
        run.font.color.rgb = RGBColor(192, 0, 0)
    elif risk_level == "High":
        run.font.color.rgb = RGBColor(255, 102, 0)
    elif risk_level == "Medium":
        run.font.color.rgb = RGBColor(255, 192, 0)
    else:
        run.font.color.rgb = RGBColor(0, 128, 0)
    run.bold = True


def _add_data_source_transparency(doc: Document):
    """Add data source and methodology transparency notice."""
    p = doc.add_paragraph()
    run = p.add_run('DATA SOURCE TRANSPARENCY')
    run.bold = True
    run.font.size = Pt(11)

    p_format = p.paragraph_format
    p_format.space_before = Pt(12)
    p_format.space_after = Pt(6)

    # MCP Server output
    p = doc.add_paragraph()
    run = p.add_run('🔧 MCP SERVER OUTPUT (Deterministic): ')
    run.bold = True
    p.add_run(
        'All content in this report is generated by rule-based code using deterministic algorithms. '
        'Risk scores are calculated using keyword detection and fixed mathematical formulas. '
        'Checklist items are based on hardcoded OSFI E-23 principles. No probabilistic AI models '
        'are used in generating this document.'
    )
    p_format = p.paragraph_format
    p_format.space_after = Pt(6)
    p_format.left_indent = Inches(0.25)

    # AI interpretation warning
    p = doc.add_paragraph()
    run = p.add_run('🧠 AI INTERPRETATION (Probabilistic): ')
    run.bold = True
    p.add_run(
        'If you received this report through an AI assistant (e.g., Claude), any additional '
        'explanations, recommendations, or analysis provided in conversation are AI-generated '
        'interpretations. Those should be distinguished from the deterministic calculations in this document.'
    )
    p_format = p.paragraph_format
    p_format.space_after = Pt(12)
    p_format.left_indent = Inches(0.25)


def _add_professional_validation_disclaimer(doc: Document, position: str = "beginning"):
    """Add professional validation requirement disclaimer."""
    doc.add_paragraph()

    p = doc.add_paragraph()
    run = p.add_run('⚠️ PROFESSIONAL VALIDATION REQUIRED')
    run.bold = True
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(192, 0, 0)  # Red color
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_format = p.paragraph_format
    p_format.space_before = Pt(12)
    p_format.space_after = Pt(6)

    # Add border-like effect with background shading
    p = doc.add_paragraph()
    p_format = p.paragraph_format
    p_format.left_indent = Inches(0.5)
    p_format.right_indent = Inches(0.5)
    p_format.space_after = Pt(12)

    disclaimer_text = (
        'This assessment tool provides an automated preliminary analysis based on keyword detection '
        'and standardized risk scoring methodology. However, all findings, risk ratings, compliance '
        'determinations, and governance recommendations in this report MUST be validated by qualified '
        'professionals before being used for regulatory compliance, governance decisions, or operational '
        'implementation.\n\n'
        'Required professional validation includes, but is not limited to:\n'
        '• Independent review by qualified model risk management professionals\n'
        '• Verification of risk rating accuracy by senior management or risk committees\n'
        '• Legal and compliance review of all regulatory interpretations\n'
        '• Assessment by subject matter experts familiar with the specific model and business context\n'
        '• Validation that governance recommendations align with institutional policies\n\n'
        'This automated assessment does not constitute professional advice and should not be relied upon '
        'as the sole basis for any compliance, governance, or risk management decisions. Users assume full '
        'responsibility for ensuring appropriate professional review and validation.'
    )

    run = p.add_run(disclaimer_text)
    run.font.size = Pt(9)
    run.italic = True


def _add_executive_summary_with_disclaimer(doc: Document, project_name: str, project_description: str,
                          risk_level: str, risk_score: int, risk_analysis: Dict[str, Any], stage_display: str):
    """Add executive summary section with data source transparency."""
    doc.add_heading('1. EXECUTIVE SUMMARY', level=1)

    # Chapter-specific transparency note
    p = doc.add_paragraph()
    run = p.add_run('🔧 DETERMINISTIC OUTPUT: ')
    run.bold = True
    run.font.size = Pt(9)
    run2 = p.add_run(
        'This summary is generated using rule-based keyword detection and fixed narrative templates.'
    )
    run2.font.size = Pt(9)
    run2.italic = True
    p_format = p.paragraph_format
    p_format.space_after = Pt(12)

    doc.add_paragraph()

    # Extract key risk drivers
    quant_indicators = risk_analysis.get("quantitative_indicators", {})
    qual_indicators = risk_analysis.get("qualitative_indicators", {})

    # Identify main risk factors (top 3-4)
    risk_factors = []
    if quant_indicators.get("financial_impact"):
        risk_factors.append("financial decision-making")
    if qual_indicators.get("ai_ml_usage"):
        risk_factors.append("AI/ML technology")
    if quant_indicators.get("customer_facing"):
        risk_factors.append("customer-facing operations")
    if qual_indicators.get("autonomous_decisions"):
        risk_factors.append("automated decision-making")
    if quant_indicators.get("regulatory_impact"):
        risk_factors.append("regulatory compliance impacts")

    # Build executive summary
    summary_parts = []

    # Opening statement
    governance_req = {
        "Critical": "board-level oversight, external validation, and comprehensive monitoring",
        "High": "senior management oversight, enhanced governance controls, and regular independent review",
        "Medium": "standard governance procedures with periodic review and appropriate documentation",
        "Low": "basic governance procedures with annual review cycles"
    }.get(risk_level, "standard governance procedures")

    summary_parts.append(
        f"This model has been assessed as {risk_level} risk with a score of {risk_score}/100 under "
        f"OSFI E-23 guidelines. This classification requires {governance_req}."
    )

    # Risk drivers
    if risk_factors:
        factors_text = ", ".join(risk_factors[:3])
        if len(risk_factors) > 3:
            factors_text += ", and other factors"
        summary_parts.append(f"The rating is driven by {factors_text}.")

    # Model functionality (extract from description)
    desc_lower = project_description.lower()
    capabilities = []
    if any(term in desc_lower for term in ['predict', 'forecast', 'estimate']):
        capabilities.append("predictive analytics")
    if any(term in desc_lower for term in ['decision', 'recommend', 'approve']):
        capabilities.append("decision support")
    if any(term in desc_lower for term in ['risk', 'credit', 'fraud']):
        capabilities.append("risk assessment")
    if any(term in desc_lower for term in ['pricing', 'valuation']):
        capabilities.append("pricing or valuation")

    if capabilities:
        cap_text = " and ".join(capabilities[:2])
        summary_parts.append(
            f"The model's core functionality includes {cap_text}, which contribute to its risk profile."
        )

    # Current stage status
    stage_next_steps = {
        "design": "requiring completion of all model rationale, data governance, and development documentation before transitioning to the Review stage",
        "review": "undergoing independent validation and conceptual soundness assessment before deployment approval",
        "deployment": "implementing production controls with quality assurance and change management processes",
        "monitoring": "requiring ongoing performance tracking, drift detection, and escalation procedures",
        "decommission": "following formal retirement procedures with stakeholder notification and documentation retention"
    }
    next_steps = stage_next_steps.get(stage_display.lower(), "requiring appropriate lifecycle controls per OSFI E-23 guidelines")
    summary_parts.append(f"Currently at {stage_display} stage, {next_steps}.")

    summary = " ".join(summary_parts)
    doc.add_paragraph(summary)


def _add_risk_methodology(doc: Document, risk_analysis: Dict[str, Any],
                         risk_level: str, risk_score: int):
    """Add risk rating methodology section."""
    doc.add_heading('2. RISK RATING METHODOLOGY', level=1)

    # Chapter-specific transparency note
    p = doc.add_paragraph()
    run = p.add_run('🔧 DETERMINISTIC OUTPUT: ')
    run.bold = True
    run.font.size = Pt(9)
    run2 = p.add_run(
        'All risk scores use fixed keyword detection and mathematical formulas. No AI interpretation.'
    )
    run2.font.size = Pt(9)
    run2.italic = True
    p_format = p.paragraph_format
    p_format.space_after = Pt(12)

    # Important note
    p = doc.add_paragraph()
    run = p.add_run(
        'IMPORTANT NOTE: '
    )
    run.bold = True
    p.add_run(
        'The weighting factors and formulas below are provided for exemplification purposes. '
        'These can be tuned to exact institutional specifications during implementation.'
    )
    p_format = p.paragraph_format
    p_format.space_after = Pt(12)

    # Formula section
    doc.add_heading('Risk Calculation Formula', level=2)

    doc.add_paragraph('Step 1: Base Score Calculation', style='List Number')
    doc.add_paragraph('Base Score = Quantitative Score + Qualitative Score')

    doc.add_paragraph('Step 2: Risk Amplification', style='List Number')
    doc.add_paragraph('Final Score = Base Score × Amplification Multiplier')
    doc.add_paragraph('Final Score = [capped at 100]')

    doc.add_paragraph('Step 3: Risk Rating Assignment', style='List Number')
    rating_table = doc.add_table(rows=5, cols=2)
    rating_table.style = 'Light Grid Accent 1'
    rating_table.rows[0].cells[0].text = 'Risk Level'
    rating_table.rows[0].cells[1].text = 'Score Range'
    rating_table.rows[1].cells[0].text = 'Low'
    rating_table.rows[1].cells[1].text = '0-25 points'
    rating_table.rows[2].cells[0].text = 'Medium'
    rating_table.rows[2].cells[1].text = '26-50 points'
    rating_table.rows[3].cells[0].text = 'High'
    rating_table.rows[3].cells[1].text = '51-75 points'
    rating_table.rows[4].cells[0].text = 'Critical'
    rating_table.rows[4].cells[1].text = '76-100 points'

    doc.add_paragraph()

    # Detailed scoring breakdown
    doc.add_heading('Detailed Scoring Breakdown', level=2)

    quant_indicators = risk_analysis.get("quantitative_indicators", {})
    qual_indicators = risk_analysis.get("qualitative_indicators", {})
    quant_score = risk_analysis.get("quantitative_score", 0)
    qual_score = risk_analysis.get("qualitative_score", 0)

    # Quantitative factors table
    doc.add_heading('Quantitative Risk Factors', level=3)

    quant_factors = [
        ("Financial Impact", "financial_impact", 10),
        ("Customer-Facing", "customer_facing", 10),
        ("Revenue Critical", "revenue_critical", 10),
        ("Regulatory Impact", "regulatory_impact", 10),
        ("High Volume", "high_volume", 10)
    ]

    quant_table = doc.add_table(rows=len(quant_factors) + 1, cols=4)
    quant_table.style = 'Light Grid Accent 1'

    # Header row
    quant_table.rows[0].cells[0].text = 'Risk Factor'
    quant_table.rows[0].cells[1].text = 'Weight'
    quant_table.rows[0].cells[2].text = 'Detected'
    quant_table.rows[0].cells[3].text = 'Points Awarded'

    # Data rows
    for idx, (name, key, weight) in enumerate(quant_factors, 1):
        detected = quant_indicators.get(key, False)
        quant_table.rows[idx].cells[0].text = name
        quant_table.rows[idx].cells[1].text = f'{weight} pts'
        quant_table.rows[idx].cells[2].text = '✓ Yes' if detected else '✗ No'
        quant_table.rows[idx].cells[3].text = f'{weight if detected else 0} pts'

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run('Quantitative Score = ').bold = True
    p.add_run(f'{quant_score} points')

    doc.add_paragraph()

    # Qualitative factors table
    doc.add_heading('Qualitative Risk Factors', level=3)

    qual_factors = [
        ("AI/ML Usage", "ai_ml_usage", 8),
        ("High Complexity", "high_complexity", 8),
        ("Autonomous Decisions", "autonomous_decisions", 8),
        ("Black Box", "black_box", 8),
        ("Third-Party Dependencies", "third_party", 8),
        ("Data Sensitive", "data_sensitive", 8),
        ("Real-Time Processing", "real_time", 8),
        ("Customer Impact", "customer_impact", 8)
    ]

    qual_table = doc.add_table(rows=len(qual_factors) + 1, cols=4)
    qual_table.style = 'Light Grid Accent 1'

    # Header row
    qual_table.rows[0].cells[0].text = 'Risk Factor'
    qual_table.rows[0].cells[1].text = 'Weight'
    qual_table.rows[0].cells[2].text = 'Detected'
    qual_table.rows[0].cells[3].text = 'Points Awarded'

    # Data rows
    for idx, (name, key, weight) in enumerate(qual_factors, 1):
        detected = qual_indicators.get(key, False)
        qual_table.rows[idx].cells[0].text = name
        qual_table.rows[idx].cells[1].text = f'{weight} pts'
        qual_table.rows[idx].cells[2].text = '✓ Yes' if detected else '✗ No'
        qual_table.rows[idx].cells[3].text = f'{weight if detected else 0} pts'

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.add_run('Qualitative Score = ').bold = True
    p.add_run(f'{qual_score} points')

    doc.add_paragraph()

    # Risk amplification analysis
    doc.add_heading('Risk Amplification Analysis', level=3)

    base_score = quant_score + qual_score

    p = doc.add_paragraph()
    p.add_run('Base Score: ').bold = True
    p.add_run(f'{base_score} points ({quant_score} quantitative + {qual_score} qualitative)')

    # Calculate amplification
    amplification = 1.0
    amplification_factors = []

    if quant_indicators.get('financial_impact') and qual_indicators.get('ai_ml_usage'):
        amplification += 0.3
        amplification_factors.append('AI/ML in financial decisions (+30%)')

    if quant_indicators.get('customer_facing') and qual_indicators.get('autonomous_decisions'):
        amplification += 0.2
        amplification_factors.append('Autonomous customer-facing decisions (+20%)')

    if qual_indicators.get('black_box') and quant_indicators.get('regulatory_impact'):
        amplification += 0.25
        amplification_factors.append('Unexplainable models with regulatory impact (+25%)')

    if qual_indicators.get('third_party') and quant_indicators.get('revenue_critical'):
        amplification += 0.15
        amplification_factors.append('Third-party dependency in critical systems (+15%)')

    if amplification_factors:
        p = doc.add_paragraph()
        p.add_run('Amplification Factors Detected:').bold = True
        for factor in amplification_factors:
            doc.add_paragraph(factor, style='List Bullet')
    else:
        doc.add_paragraph('No amplification factors detected.')

    p = doc.add_paragraph()
    p.add_run('Total Amplification Multiplier: ').bold = True
    p.add_run(f'{amplification:.2f}x')

    final_score = min(int(base_score * amplification), 100)

    p = doc.add_paragraph()
    p.add_run('Final Score: ').bold = True
    p.add_run(f'{base_score} × {amplification:.2f} = {final_score} points → ')
    run = p.add_run(f'{risk_level.upper()}')
    run.bold = True
    if risk_level == "Critical":
        run.font.color.rgb = RGBColor(192, 0, 0)
    elif risk_level == "High":
        run.font.color.rgb = RGBColor(255, 102, 0)
    elif risk_level == "Medium":
        run.font.color.rgb = RGBColor(255, 192, 0)
    else:
        run.font.color.rgb = RGBColor(0, 128, 0)


def _add_compliance_checklist(doc: Document, project_description: str,
                              risk_level: str, risk_score: int, stage_display: str = "Design"):
    """Add stage-specific compliance checklist (fallback - uses hardcoded Design items)."""
    doc.add_heading(f'3. {stage_display.upper()} PHASE COMPLIANCE CHECKLIST', level=1)

    # Chapter-specific transparency note
    p = doc.add_paragraph()
    run = p.add_run('🔧 DETERMINISTIC OUTPUT: ')
    run.bold = True
    run.font.size = Pt(9)
    run2 = p.add_run(
        'This checklist is hardcoded from OSFI E-23 principles. Items are not AI-generated.'
    )
    run2.font.size = Pt(9)
    run2.italic = True
    p_format = p.paragraph_format
    p_format.space_after = Pt(12)

    # Important note
    p = doc.add_paragraph()
    run = p.add_run('IMPORTANT NOTE: ')
    run.bold = True
    p.add_run(
        'This checklist represents an interpretation of OSFI E-23 principles and is provided '
        'for exemplification purposes. Each financial institution must design its own '
        'implementation based on their specific governance framework, risk appetite, and '
        'operational context. '
    )
    p_format = p.paragraph_format
    p_format.space_after = Pt(6)

    p2 = doc.add_paragraph()
    run2 = p2.add_run('Risk-Based Requirements: ')
    run2.bold = True
    p2.add_run(
        f'Per OSFI Principle 2.3, the level of rigor, documentation depth, and governance '
        f'oversight required varies based on the model\'s risk classification. This model\'s '
        f'{risk_level} risk rating ({risk_score}/100) determines the appropriate governance '
        f'intensity. Higher risk models require more comprehensive documentation, enhanced '
        f'review processes, and elevated approval authorities before transitioning between '
        f'lifecycle stages.'
    )
    p2_format = p2.paragraph_format
    p2_format.space_after = Pt(12)

    p3 = doc.add_paragraph()
    p3.add_run('Purpose: ').bold = True
    p3.add_run(
        'The items below outline Design stage requirements based on OSFI Principles 3.2 and 3.3. '
        'Institutions should customize this checklist to align with their model risk management framework.'
    )

    doc.add_paragraph()

    # Check if AI/ML model
    is_ai_ml = any(term in project_description.lower()
                   for term in ['ai', 'artificial intelligence', 'machine learning',
                               'neural', 'deep learning'])

    # 3.1 Model Rationale
    doc.add_heading('3.1 Model Rationale (OSFI Principle 3.2)', level=2)

    _add_checklist_item(doc, 'Clear organizational rationale documented',
                       'Model Rationale Document explaining business need and purpose')
    _add_checklist_item(doc, 'Well-defined model purpose and scope',
                       'Model Purpose and Scope Statement defining boundaries and coverage')
    _add_checklist_item(doc, 'Business use case identified and documented',
                       'Business Use Case Documentation with decision-making context')
    _add_checklist_item(doc, 'Risk of intended usage assessed',
                       'Usage Risk Assessment evaluating business context risks')

    if is_ai_ml:
        _add_checklist_item(doc, 'Explainability requirements defined (AI/ML models)',
                           'Explainability Requirements Document defining transparency levels')
        _add_checklist_item(doc, 'Bias and fairness considerations documented (AI/ML models)',
                           'Bias and Fairness Assessment for potential biased outcomes')
        _add_checklist_item(doc, 'Privacy risk assessment completed (AI/ML models)',
                           'Privacy Impact Assessment')

    # 3.2 Model Data
    doc.add_heading('3.2 Model Data (OSFI Principle 3.2)', level=2)

    _add_checklist_item(doc, 'Data governance framework established',
                       'Data Governance Documentation integrated with enterprise standards')
    _add_checklist_item(doc, 'Data quality standards defined',
                       'Data Quality Standards Document (accuracy, relevance, representativeness)')
    _add_checklist_item(doc, 'Data sources documented with lineage and provenance',
                       'Data Lineage and Provenance Documentation')
    _add_checklist_item(doc, 'Data compliance requirements addressed',
                       'Data Compliance Documentation (privacy, ethics, regulatory)')
    _add_checklist_item(doc, 'Data quality checks defined',
                       'Data Quality Check Procedures (outliers, missing values, consistency)')
    _add_checklist_item(doc, 'Bias assessment and management approach documented',
                       'Data Bias Management Plan')
    _add_checklist_item(doc, 'Data update frequency established',
                       'Data Refresh Schedule')

    # 3.3 Model Development
    doc.add_heading('3.3 Model Development (OSFI Principle 3.3)', level=2)

    _add_checklist_item(doc, 'Model methodology documented',
                       'Model Methodology Documentation (algorithms, transformations)')
    _add_checklist_item(doc, 'Model assumptions documented',
                       'Model Assumptions Document with limitations')
    _add_checklist_item(doc, 'Development processes documented',
                       'Development Process Documentation (setup, procedures)')
    _add_checklist_item(doc, 'Expert judgment role documented',
                       'Expert Judgment Documentation')
    _add_checklist_item(doc, 'Performance criteria established',
                       'Performance Criteria Document with evaluation metrics')
    _add_checklist_item(doc, 'Development testing documented',
                       'Development Testing Report')
    _add_checklist_item(doc, 'Model output usage standards defined',
                       'Output Usage Standards')

    # 3.4 Design Stage Governance
    doc.add_heading('3.4 Design Stage Governance (OSFI Appendix 1)', level=2)

    _add_checklist_item(doc, 'Model owner assigned',
                       'Designate accountable individual/unit')
    _add_checklist_item(doc, 'Model developer identified',
                       'Document who is developing the model')
    _add_checklist_item(doc, 'Model ID assigned',
                       'Unique identifier for model inventory')
    _add_checklist_item(doc, 'Provisional model risk rating assigned',
                       f'Assign initial risk rating ({risk_level} - {risk_score}/100)')

    # 3.5 Readiness for Review Stage
    doc.add_heading('3.5 Readiness for Review Stage', level=2)

    _add_checklist_item(doc, 'All Design stage deliverables complete',
                       'Complete all documentation per Principles 3.2 and 3.3')
    _add_checklist_item(doc, 'Model documentation meets standards for independent review',
                       'Documentation adequate for independent validation per Principle 3.4')
    _add_checklist_item(doc, 'Model reviewer identified and assigned',
                       'Independent reviewer assigned for validation stage')
    _add_checklist_item(doc, 'Review scope and criteria defined based on model risk rating',
                       f'Define review scope commensurate with {risk_level} risk rating per Principle 2.3')

    doc.add_paragraph()
    p = doc.add_paragraph()
    run = p.add_run('COMPLETION REQUIREMENT: ')
    run.bold = True
    run.font.color.rgb = RGBColor(192, 0, 0)
    p.add_run(
        'All items above must be addressed to transition from Design to Review stage '
        'per OSFI E-23 guidelines.'
    )


def _add_checklist_item(doc: Document, item: str, deliverable: str):
    """Add a checklist item with deliverable."""
    p = doc.add_paragraph()
    p.add_run('☐ ').font.size = Pt(12)
    run = p.add_run(item)
    run.bold = True

    p2 = doc.add_paragraph(f'   Deliverable: {deliverable}')
    p2.paragraph_format.left_indent = Inches(0.5)
    p2.paragraph_format.space_after = Pt(6)


def _add_annex_principles(doc: Document, current_stage: str = "design"):
    """Add annex with OSFI E-23 principles."""
    stage_display_names = {
        "design": "DESIGN STAGE",
        "review": "REVIEW STAGE",
        "deployment": "DEPLOYMENT STAGE",
        "monitoring": "MONITORING STAGE",
        "decommission": "DECOMMISSION STAGE"
    }
    stage_title = stage_display_names.get(current_stage, "DESIGN STAGE")
    doc.add_heading(f'ANNEX: OSFI E-23 PRINCIPLES ({stage_title})', level=1)

    # Chapter-specific transparency note
    p = doc.add_paragraph()
    run = p.add_run('🔧 DETERMINISTIC OUTPUT: ')
    run.bold = True
    run.font.size = Pt(9)
    run2 = p.add_run(
        'Official OSFI E-23 principles hardcoded from Guideline E-23 (2027). No AI interpretation.'
    )
    run2.font.size = Pt(9)
    run2.italic = True
    p_format = p.paragraph_format
    p_format.space_after = Pt(12)

    principles = [
        (
            "Principle 2.1: Model Inventory",
            "Institutions must maintain a comprehensive inventory of all models, including "
            "provisional risk ratings for models in development. This ensures visibility and "
            "tracking from inception."
        ),
        (
            "Principle 2.2: Risk Rating Methodology",
            "Institutions must establish their own risk rating approach assessing key dimensions "
            "of model risk. The rating determines governance intensity and review frequency requirements."
        ),
        (
            "Principle 2.3: Governance Intensity",
            "The level of governance, documentation, and oversight must be commensurate with the "
            "model's risk rating. Critical models require board-level approval, external validation, "
            "and enhanced monitoring."
        ),
        (
            "Principle 3.2: Model Design - Rationale and Data",
            "Model design must establish clear organizational rationale, ensure data quality and "
            "governance, and address AI/ML-specific considerations including explainability, bias, "
            "and privacy."
        ),
        (
            "Principle 3.3: Model Development",
            "Model development must follow documented methodologies with clear assumptions, "
            "appropriate testing, defined performance criteria, and comprehensive documentation "
            "for independent review."
        ),
        (
            "Principle 3.4: Independent Model Review",
            "All models require independent validation by qualified personnel separate from "
            "development, with scope and rigor commensurate with risk rating. Critical models "
            "require external validation."
        ),
        (
            "OSFI Appendix 1: Model Inventory Requirements",
            "Specifies mandatory tracking fields including model ID, name, owner, developer, "
            "risk rating, lifecycle stage, and review dates to ensure comprehensive model governance."
        )
    ]

    for title, description in principles:
        p = doc.add_paragraph()
        run = p.add_run(title)
        run.bold = True
        doc.add_paragraph(description)
        doc.add_paragraph()


def _add_lifecycle_coverage_section(doc: Document, lifecycle_compliance: Dict[str, Any],
                                    current_stage: str, stage_display: str):
    """Add Step 3 lifecycle coverage assessment section."""
    doc.add_heading('3. LIFECYCLE COVERAGE ASSESSMENT', level=1)

    # Chapter-specific transparency note
    p = doc.add_paragraph()
    run = p.add_run('🔧 DETERMINISTIC OUTPUT: ')
    run.bold = True
    run.font.size = Pt(9)
    run2 = p.add_run(
        'Coverage based on keyword detection in project description. Not a compliance audit.'
    )
    run2.font.size = Pt(9)
    run2.italic = True
    p_format = p.paragraph_format
    p_format.space_after = Pt(12)

    # Extract coverage data from Step 3 response
    compliance_analysis = lifecycle_compliance.get("compliance_analysis", {})
    coverage_percentage = compliance_analysis.get("compliance_percentage", 0)
    elements_covered = compliance_analysis.get("compliance_score", 0)
    total_elements = compliance_analysis.get("total_indicators", 3)
    gaps_identified = compliance_analysis.get("gaps_identified", [])
    stage_indicators = compliance_analysis.get("stage_indicators", {})

    # Coverage summary
    p = doc.add_paragraph()
    p.add_run(f'{stage_display} Stage Coverage: ').bold = True
    run = p.add_run(f'{coverage_percentage}% ({elements_covered}/{total_elements} elements detected)')
    if coverage_percentage == 100:
        run.font.color.rgb = RGBColor(0, 128, 0)  # Green
    elif coverage_percentage >= 67:
        run.font.color.rgb = RGBColor(255, 192, 0)  # Yellow
    else:
        run.font.color.rgb = RGBColor(255, 102, 0)  # Orange
    run.bold = True

    doc.add_paragraph()

    # Important note
    p = doc.add_paragraph()
    run = p.add_run('IMPORTANT NOTE: ')
    run.bold = True
    p.add_run(
        'This coverage assessment indicates whether the project description mentions the 3 official '
        f'OSFI E-23 subcomponents for {stage_display} stage. It does NOT verify actual compliance '
        'or deliverable completeness. Full compliance requires professional validation of actual '
        'documentation and deliverables.'
    )
    p_format = p.paragraph_format
    p_format.space_after = Pt(12)

    # OSFI Elements Detection Table
    doc.add_heading(f'OSFI E-23 {stage_display} Stage Elements', level=2)

    # Create table with 3 rows (one per element)
    table = doc.add_table(rows=total_elements + 1, cols=3)
    table.style = 'Light Grid Accent 1'

    # Header row
    table.rows[0].cells[0].text = 'OSFI Element'
    table.rows[0].cells[1].text = 'Detected'
    table.rows[0].cells[2].text = 'Coverage Indicator'

    # Data rows
    element_names = {
        "design": ["Model Rationale", "Model Data", "Model Development"],
        "review": ["Independent Validation", "Conceptual Soundness", "Performance Evaluation"],
        "deployment": ["Production Implementation", "Quality Control", "Change Management"],
        "monitoring": ["Performance Tracking", "Drift Detection", "Escalation Procedures"],
        "decommission": ["Retirement Process", "Stakeholder Notification", "Documentation Retention"]
    }

    elements = element_names.get(current_stage, ["Element 1", "Element 2", "Element 3"])

    # Get indicator keys for this stage
    indicator_keys = list(stage_indicators.keys()) if stage_indicators else []

    for idx, element_name in enumerate(elements):
        detected = stage_indicators.get(indicator_keys[idx], False) if idx < len(indicator_keys) else False
        table.rows[idx + 1].cells[0].text = element_name
        table.rows[idx + 1].cells[1].text = '✓ Yes' if detected else '✗ No'

        # Get coverage indicator description
        if detected:
            table.rows[idx + 1].cells[2].text = 'Keywords found in description'
        else:
            table.rows[idx + 1].cells[2].text = 'Not mentioned'

    doc.add_paragraph()

    # Gap analysis if present
    if gaps_identified:
        doc.add_heading('Coverage Gaps', level=3)
        p = doc.add_paragraph()
        p.add_run('Missing Elements: ').bold = True
        for gap in gaps_identified:
            # Convert key name to readable format
            gap_display = gap.replace('_covered', '').replace('_', ' ').title()
            doc.add_paragraph(gap_display, style='List Bullet')

        # Add recommendation
        doc.add_paragraph()
        p = doc.add_paragraph()
        p.add_run('Recommendation: ').bold = True
        p.add_run('Enhance project description to address missing elements before proceeding to next lifecycle stage.')


def _add_stage_compliance_checklist(doc: Document, compliance_framework: Dict[str, Any],
                                    current_stage: str, stage_display: str, risk_level: str):
    """Add Step 5 stage-specific compliance checklist using osfi_elements structure."""
    doc.add_heading(f'4. {stage_display.upper()} STAGE COMPLIANCE CHECKLIST', level=1)

    # Chapter-specific transparency note
    p = doc.add_paragraph()
    run = p.add_run('🔧 DETERMINISTIC OUTPUT: ')
    run.bold = True
    run.font.size = Pt(9)
    run2 = p.add_run(
        'This checklist is generated from OSFI E-23 principles. Items are not AI-generated.'
    )
    run2.font.size = Pt(9)
    run2.italic = True
    p_format = p.paragraph_format
    p_format.space_after = Pt(12)

    # Important notes
    p = doc.add_paragraph()
    run = p.add_run('IMPORTANT NOTE: ')
    run.bold = True
    p.add_run(
        'This checklist represents an interpretation of OSFI E-23 principles and is provided '
        'for exemplification purposes. Each financial institution must design its own '
        'implementation based on their specific governance framework, risk appetite, and '
        'operational context.'
    )
    p_format = p.paragraph_format
    p_format.space_after = Pt(12)

    # Get osfi_elements
    osfi_elements = compliance_framework.get("osfi_elements", [])

    # Iterate through the 3 OSFI elements
    for idx, element in enumerate(osfi_elements, 1):
        element_name = element.get("element_name", f"Element {idx}")
        osfi_principle = element.get("osfi_principle", "")

        # Element heading
        doc.add_heading(f'4.{idx} {element_name} ({osfi_principle})', level=2)

        # Requirements
        requirements = element.get("requirements", [])
        if requirements:
            p = doc.add_paragraph()
            p.add_run('Requirements:').bold = True
            for req in requirements:
                doc.add_paragraph(req, style='List Bullet')

        doc.add_paragraph()

        # Deliverables
        deliverables = element.get("deliverables", [])
        if deliverables:
            p = doc.add_paragraph()
            p.add_run('Key Deliverables:').bold = True
            for deliv in deliverables:
                doc.add_paragraph(deliv, style='List Bullet')

        doc.add_paragraph()

        # Checklist items
        checklist_items = element.get("checklist_items", [])
        if checklist_items:
            p = doc.add_paragraph()
            p.add_run('Checklist:').bold = True
            for item in checklist_items:
                item_text = item.get("item", "") if isinstance(item, dict) else item
                required = item.get("required", True) if isinstance(item, dict) else True

                p = doc.add_paragraph()
                p.add_run('☐ ').font.size = Pt(12)
                run = p.add_run(item_text)
                run.bold = True
                if required:
                    run2 = p.add_run(' (Required)')
                    run2.font.color.rgb = RGBColor(192, 0, 0)
                    run2.italic = True

        doc.add_paragraph()

    # Completion note
    doc.add_paragraph()
    p = doc.add_paragraph()
    run = p.add_run('COMPLETION REQUIREMENT: ')
    run.bold = True
    run.font.color.rgb = RGBColor(192, 0, 0)
    p.add_run(
        f'All items above must be addressed according to the {risk_level} risk rating '
        f'to transition from {stage_display} to the next lifecycle stage per OSFI E-23 guidelines.'
    )


def _add_governance_structure_section(doc: Document, compliance_framework: Dict[str, Any],
                                     assessment_results: Dict[str, Any], risk_level: str):
    """Add Step 5 governance structure section with roles, documentation, and approval procedures."""
    doc.add_heading('5. GOVERNANCE STRUCTURE', level=1)

    # Chapter-specific transparency note
    p = doc.add_paragraph()
    run = p.add_run('🔧 DETERMINISTIC OUTPUT: ')
    run.bold = True
    run.font.size = Pt(9)
    run2 = p.add_run(
        'Governance structure based on OSFI E-23 requirements and risk-based practices.'
    )
    run2.font.size = Pt(9)
    run2.italic = True
    p_format = p.paragraph_format
    p_format.space_after = Pt(12)

    # Important note
    p = doc.add_paragraph()
    run = p.add_run('IMPORTANT NOTE: ')
    run.bold = True
    p.add_run(
        'Governance roles, documentation requirements, and approval procedures shown below are based on OSFI E-23 requirements '
        '(where mandated) and common industry practices (where suggested). Each institution must '
        'align governance structure with its own organizational design and risk appetite.'
    )
    p_format = p.paragraph_format
    p_format.space_after = Pt(12)

    # === 5.1 Governance Roles and Responsibilities ===
    governance_structure = compliance_framework.get("governance_structure", {})
    doc.add_heading(f'5.1 Governance Roles and Responsibilities ({risk_level} Risk)', level=2)

    # Create table
    rows_needed = len(governance_structure) + 1
    table = doc.add_table(rows=rows_needed, cols=4)
    table.style = 'Light Grid Accent 1'

    # Header row
    table.rows[0].cells[0].text = 'Role'
    table.rows[0].cells[1].text = 'Responsibility'
    table.rows[0].cells[2].text = 'OSFI Required'
    table.rows[0].cells[3].text = 'Source'

    # Data rows
    for idx, (role_key, role_data) in enumerate(governance_structure.items(), 1):
        role_display = role_key.replace('_', ' ').title()
        table.rows[idx].cells[0].text = role_display
        table.rows[idx].cells[1].text = role_data.get("role", "")

        osfi_required = role_data.get("osfi_required", False)
        osfi_implied = role_data.get("osfi_implied", False)

        if osfi_required:
            table.rows[idx].cells[2].text = '✓ Yes'
        elif osfi_implied:
            table.rows[idx].cells[2].text = '~ Implied'
        else:
            table.rows[idx].cells[2].text = '✗ No'

        table.rows[idx].cells[3].text = role_data.get("source", "")

    doc.add_paragraph()

    # Legend
    p = doc.add_paragraph()
    p.add_run('Legend:').bold = True
    doc.add_paragraph('✓ Yes = Explicitly required by OSFI E-23 (e.g., Appendix 1 mandatory fields)', style='List Bullet')
    doc.add_paragraph('~ Implied = Implied by OSFI E-23 principles (e.g., independent reviewer)', style='List Bullet')
    doc.add_paragraph('✗ No = Suggested implementation choice based on risk-based governance', style='List Bullet')

    # === 5.2 Documentation Requirements ===
    doc.add_heading(f'5.2 Documentation Requirements ({risk_level} Risk)', level=2)

    documentation_requirements = compliance_framework.get("documentation_requirements", [])
    if documentation_requirements:
        p = doc.add_paragraph()
        p.add_run('Required Documentation: ').bold = True
        p.add_run(
            'The following documentation must be maintained throughout the model lifecycle per OSFI E-23 requirements.'
        )
        doc.add_paragraph()

        for doc_req in documentation_requirements:
            doc.add_paragraph(doc_req, style='List Bullet')
    else:
        doc.add_paragraph('No specific documentation requirements identified for this risk level.')

    doc.add_paragraph()

    # === 5.3 Review and Approval Procedures ===
    doc.add_heading(f'5.3 Review and Approval Procedures ({risk_level} Risk)', level=2)

    # Get review_approval from Step 2 governance_requirements
    governance_requirements = assessment_results.get("governance_requirements", {})
    review_approval_requirements = governance_requirements.get("review_approval", [])

    if review_approval_requirements:
        p = doc.add_paragraph()
        p.add_run('Approval Procedures: ').bold = True
        p.add_run(
            'The following review and approval procedures must be followed per OSFI E-23 governance requirements.'
        )
        doc.add_paragraph()

        for approval_req in review_approval_requirements:
            doc.add_paragraph(approval_req, style='List Bullet')
    else:
        doc.add_paragraph('No specific review and approval procedures identified for this risk level.')

    doc.add_paragraph()


def _add_monitoring_framework_section(doc: Document, monitoring_framework: Dict[str, Any]):
    """Add Step 5 monitoring framework section."""
    doc.add_heading('6. MONITORING FRAMEWORK', level=1)

    # Chapter-specific transparency note
    p = doc.add_paragraph()
    run = p.add_run('🔧 DETERMINISTIC OUTPUT: ')
    run.bold = True
    run.font.size = Pt(9)
    run2 = p.add_run(
        'Monitoring frequencies and thresholds are risk-based exemplifications.'
    )
    run2.font.size = Pt(9)
    run2.italic = True
    p_format = p.paragraph_format
    p_format.space_after = Pt(12)

    # Monitoring frequency
    frequency = monitoring_framework.get("monitoring_frequency", "Not specified")
    p = doc.add_paragraph()
    p.add_run('Monitoring Frequency: ').bold = True
    p.add_run(frequency)

    # Reporting schedule
    reporting = monitoring_framework.get("reporting_schedule", "Not specified")
    p = doc.add_paragraph()
    p.add_run('Reporting Schedule: ').bold = True
    p.add_run(reporting)

    doc.add_paragraph()

    # Key metrics
    key_metrics = monitoring_framework.get("key_metrics", [])
    if key_metrics:
        doc.add_heading('Key Performance Metrics', level=2)
        for metric in key_metrics:
            doc.add_paragraph(metric, style='List Bullet')

    doc.add_paragraph()

    # Alert thresholds
    alert_thresholds = monitoring_framework.get("alert_thresholds", {})
    if alert_thresholds:
        doc.add_heading('Alert Thresholds', level=2)
        for threshold_name, threshold_value in alert_thresholds.items():
            p = doc.add_paragraph()
            p.add_run(f'{threshold_name.replace("_", " ").title()}: ').bold = True
            p.add_run(threshold_value)
