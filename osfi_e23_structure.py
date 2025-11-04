"""
OSFI E-23 Model Risk Management - Official Structure and Terminology

This module provides the official OSFI E-23 Guideline structure, terminology,
and lifecycle-focused compliance framework for Canadian federally regulated
financial institutions (FRFIs).

Reference: OSFI Guideline E-23 – Model Risk Management (2027)
Effective Date: May 1, 2027
URL: https://www.osfi-bsif.gc.ca/en/guidance/guidance-library/guideline-e-23-model-risk-management-2027
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# OSFI E-23 OFFICIAL PRINCIPLES
# ============================================================================

OSFI_PRINCIPLES = {
    "1.1": "Effective reporting structures and proper resourcing should enable sound model governance",
    "1.2": "The MRM framework should align risk-taking activities to strategic objectives and risk appetite",
    "1.3": "Models should be appropriate for their business purposes",
    "2.1": "Institutions should identify and track all models in use or recently decommissioned",
    "2.2": "Institutions should establish a model risk rating approach that assesses key dimensions of model risk",
    "2.3": "The scope, scale, and intensity of MRM should be commensurate with the risk introduced by the model",
    "3.1": "MRM policies, procedures, and controls should be robust, flexible, and lead to effective requirements applied across the model lifecycle",
    "3.2": "Data used to develop the model should be suitable for the intended use",
    "3.3": "Institutions should have model development processes that set clear standards for performance and documentation",
    "3.4": "Institutions should have a process to independently assess conceptual soundness and performance of models",
    "3.5": "Models should be deployed in an environment with quality and change control processes",
    "3.6": "Institutions should have defined standards for model monitoring, and model decommission"
}

# ============================================================================
# OSFI E-23 OUTCOMES
# ============================================================================

OSFI_OUTCOMES = {
    "1": "Model risk is well understood and managed across the enterprise",
    "2": "Model risk is managed using a risk-based approach",
    "3": "Model governance covers the entire model lifecycle"
}

# ============================================================================
# OSFI E-23 LIFECYCLE COMPONENTS
# ============================================================================

OSFI_LIFECYCLE_COMPONENTS = {
    "design": {
        "name": "Model Design",
        "subcomponents": ["Model Rationale", "Model Data", "Model Development"],
        "principles": ["3.2", "3.3"],
        "description": "Encompasses model rationale, data governance, and development processes"
    },
    "review": {
        "name": "Model Review",
        "subcomponents": ["Independent Validation", "Conceptual Soundness", "Performance Evaluation"],
        "principles": ["3.4"],
        "description": "Independent assessment of model conceptual soundness and performance"
    },
    "deployment": {
        "name": "Model Deployment",
        "subcomponents": ["Production Implementation", "Quality Control", "Change Management"],
        "principles": ["3.5"],
        "description": "Production implementation with quality and change control processes"
    },
    "monitoring": {
        "name": "Model Monitoring",
        "subcomponents": ["Performance Tracking", "Drift Detection", "Escalation Procedures"],
        "principles": ["3.6"],
        "description": "Ongoing performance monitoring with defined standards and thresholds"
    },
    "decommission": {
        "name": "Model Decommission",
        "subcomponents": ["Retirement Process", "Stakeholder Notification", "Documentation Retention"],
        "principles": ["3.6"],
        "description": "Formal model retirement with proper documentation and notification"
    }
}

# ============================================================================
# OSFI APPENDIX 1: MODEL TRACKING FIELDS
# ============================================================================

APPENDIX_1_REQUIRED_FIELDS = [
    "model_id",
    "model_name",
    "model_description",
    "model_owner",
    "model_developer",
    "model_origin"  # Internal/Vendor/Third-party
]

APPENDIX_1_OPTIONAL_FIELDS = [
    "model_version",
    "date_deployed",
    "model_reviewer",
    "model_approver",
    "model_dependencies",
    "data_sources",
    "approved_uses",
    "model_limitations",
    "date_most_recent_review",
    "monitoring_status",
    "next_review_date"
]

APPENDIX_1_STAGE_SPECIFIC = {
    "design": ["provisional_risk_rating", "target_review_date"],
    "review": ["model_reviewer", "review_scope", "review_schedule"],
    "deployment": ["date_deployed", "model_version", "model_approver"],
    "monitoring": ["monitoring_status", "next_review_date", "date_most_recent_review"],
    "decommission": ["decommission_date", "decommission_reason"]
}

# ============================================================================
# LIFECYCLE STAGE DETECTION
# ============================================================================

def detect_lifecycle_stage(project_description: str) -> str:
    """
    Detect current lifecycle stage from project description.

    Args:
        project_description: The project/model description text

    Returns:
        str: One of 'design', 'review', 'deployment', 'monitoring', 'decommission'

    Stage Detection Logic:
    - Uses keyword matching with priority order
    - More specific stages checked first to avoid false positives
    - Defaults to 'design' if no clear indicators
    """
    if not project_description:
        logger.warning("Empty project description, defaulting to 'design' stage")
        return 'design'

    description_lower = project_description.lower()

    # Stage indicators (ordered by specificity/priority)
    stage_indicators = {
        "decommission": [
            "retiring", "retirement", "decommission", "decommissioning", "sunsetting",
            "end of life", "discontinuing", "phasing out", "sunset"
        ],
        "monitoring": [
            "deployed", "in production", "live", "operational",
            "monitoring", "production environment", "post-deployment"
        ],
        "deployment": [
            "deploy", "deploying", "implementing", "implementation",
            "go-live", "rollout", "production preparation", "deployment phase"
        ],
        "review": [
            "review", "reviewing", "validation", "validating", "testing",
            "under review", "being validated", "independent assessment",
            "validation phase", "review stage"
        ],
        "design": [
            "design", "designing", "develop", "developing", "in development",
            "planning", "creating", "building", "early stage", "conceptual",
            "design phase", "development phase", "prototype", "prototyping"
        ]
    }

    # Check stages in priority order
    for stage, indicators in stage_indicators.items():
        if any(indicator in description_lower for indicator in indicators):
            logger.info(f"Detected lifecycle stage: {stage}")
            return stage

    # Default to design if no clear indicators
    logger.info("No clear stage indicators found, defaulting to 'design'")
    return 'design'

# ============================================================================
# DESIGN STAGE COMPLIANCE CHECKLIST
# ============================================================================

def get_design_stage_checklist() -> Dict[str, List[Dict[str, str]]]:
    """
    Return comprehensive Design stage compliance checklist.

    Based on OSFI E-23 Principles 3.2 (Model Data) and 3.3 (Model Development).
    Includes model rationale, data governance, development processes, and
    planning for future stages.

    Returns:
        Dict containing categorized checklist items with OSFI references
    """
    return {
        "model_rationale": [
            {
                "item": "Clear organizational rationale documented",
                "requirement": "Establish why this model is needed and its business purpose",
                "deliverable": "Model Rationale Document",
                "osfi_reference": "Principle 3.2 (Model Rationale)",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Well-defined model purpose and scope",
                "requirement": "Define what the model does, boundaries of use, and coverage",
                "deliverable": "Model Purpose and Scope Statement",
                "osfi_reference": "Principle 3.2 (Model Rationale)",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Business use case identified and documented",
                "requirement": "Document specific business applications and decision-making context",
                "deliverable": "Business Use Case Documentation",
                "osfi_reference": "Principle 3.2 (Model Rationale)",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Risk of intended usage assessed",
                "requirement": "Evaluate risks associated with model use in business context",
                "deliverable": "Usage Risk Assessment",
                "osfi_reference": "Principle 3.2 (Model Rationale)",
                "category": "design",
                "priority": "high"
            },
            {
                "item": "Explainability requirements defined (AI/ML models)",
                "requirement": "Determine level of transparency and explainability required for intended use",
                "deliverable": "Explainability Requirements Document",
                "osfi_reference": "Principle 3.2 (Model Rationale - AI/ML)",
                "category": "design",
                "priority": "high",
                "ai_ml_specific": True
            },
            {
                "item": "Bias and fairness considerations documented (AI/ML models)",
                "requirement": "Assess potential for biased outcomes and ethical implications",
                "deliverable": "Bias and Fairness Assessment",
                "osfi_reference": "Principle 3.2 (Model Rationale - AI/ML)",
                "category": "design",
                "priority": "high",
                "ai_ml_specific": True
            },
            {
                "item": "Privacy risk assessment completed (AI/ML models)",
                "requirement": "Evaluate privacy risks associated with model use",
                "deliverable": "Privacy Impact Assessment",
                "osfi_reference": "Principle 3.2 (Model Rationale - AI/ML)",
                "category": "design",
                "priority": "high",
                "ai_ml_specific": True
            }
        ],

        "model_data": [
            {
                "item": "Data governance framework established",
                "requirement": "Standards for collecting, storing, accessing model data integrated with enterprise data governance",
                "deliverable": "Data Governance Documentation",
                "osfi_reference": "Principle 3.2 (Model Data)",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Data quality standards defined",
                "requirement": "Accuracy, fit-for-use, relevance, representativeness requirements documented",
                "deliverable": "Data Quality Standards Document",
                "osfi_reference": "Principle 3.2 (Model Data)",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Data sources documented with lineage and provenance",
                "requirement": "Document all data sources, formats, types, and traceability",
                "deliverable": "Data Lineage and Provenance Documentation",
                "osfi_reference": "Principle 3.2 (Model Data)",
                "category": "design",
                "priority": "high"
            },
            {
                "item": "Data compliance requirements addressed",
                "requirement": "Adherence to statutory, regulatory, and internal requirements for data ethics and privacy",
                "deliverable": "Data Compliance Documentation",
                "osfi_reference": "Principle 3.2 (Model Data)",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Data quality checks defined",
                "requirement": "Define processes for outlier detection, missing value analysis, consistency evaluations",
                "deliverable": "Data Quality Check Procedures",
                "osfi_reference": "Principle 3.2 (Model Data)",
                "category": "design",
                "priority": "high"
            },
            {
                "item": "Bias assessment and management approach documented",
                "requirement": "Identify potential unwanted bias in data and mitigation approaches",
                "deliverable": "Data Bias Management Plan",
                "osfi_reference": "Principle 3.2 (Model Data)",
                "category": "design",
                "priority": "high"
            },
            {
                "item": "Data update frequency established",
                "requirement": "Define timeliness requirements and update schedules",
                "deliverable": "Data Refresh Schedule",
                "osfi_reference": "Principle 3.2 (Model Data)",
                "category": "design",
                "priority": "medium"
            }
        ],

        "model_development": [
            {
                "item": "Model methodology documented",
                "requirement": "Document conceptually sound methodologies, data transformations, and algorithms selected",
                "deliverable": "Model Methodology Documentation",
                "osfi_reference": "Principle 3.3",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Model assumptions documented",
                "requirement": "Detailed descriptions of model assumptions and limitations",
                "deliverable": "Model Assumptions Document",
                "osfi_reference": "Principle 3.3",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Development processes documented",
                "requirement": "Document model setup, running procedures, and development approach",
                "deliverable": "Development Process Documentation",
                "osfi_reference": "Principle 3.3",
                "category": "design",
                "priority": "high"
            },
            {
                "item": "Expert judgment role documented",
                "requirement": "Document which experts are involved and how their input affects model output",
                "deliverable": "Expert Judgment Documentation",
                "osfi_reference": "Principle 3.3",
                "category": "design",
                "priority": "medium"
            },
            {
                "item": "Performance criteria established",
                "requirement": "Define clear performance and selection criteria for model evaluation",
                "deliverable": "Performance Criteria Document",
                "osfi_reference": "Principle 3.3",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Development testing documented",
                "requirement": "Document analyses and performance tests performed by developers",
                "deliverable": "Development Testing Report",
                "osfi_reference": "Principle 3.3",
                "category": "design",
                "priority": "high"
            },
            {
                "item": "Model output usage standards defined",
                "requirement": "Define how model outputs are used and reported",
                "deliverable": "Output Usage Standards",
                "osfi_reference": "Principle 3.3",
                "category": "design",
                "priority": "high"
            }
        ],

        "planning_for_future": [
            {
                "item": "Model monitoring criteria defined",
                "requirement": "Define performance criteria and thresholds for future monitoring (Principle 3.6)",
                "deliverable": "Monitoring Criteria Design Document",
                "osfi_reference": "Principle 3.3 (performance criteria for model monitoring)",
                "category": "design",
                "priority": "high",
                "future_stage": "monitoring",
                "note": "Design stage requirement that defines approaches for future implementation"
            },
            {
                "item": "Model review standards established",
                "requirement": "Define scope and criteria for independent validation (Principle 3.4)",
                "deliverable": "Review Standards and Criteria Document",
                "osfi_reference": "Principle 3.3 (model documentation for review)",
                "category": "design",
                "priority": "high",
                "future_stage": "review",
                "note": "Design stage requirement that defines approaches for future implementation"
            },
            {
                "item": "Performance thresholds defined",
                "requirement": "Define breach criteria and materiality thresholds (Principle 3.6)",
                "deliverable": "Performance Threshold Definition",
                "osfi_reference": "Principle 3.3 (performance standards)",
                "category": "design",
                "priority": "medium",
                "future_stage": "monitoring",
                "note": "Design stage requirement that defines approaches for future implementation"
            },
            {
                "item": "Escalation procedures designed",
                "requirement": "Define escalation process for performance issues (Principle 3.6)",
                "deliverable": "Escalation Procedure Design",
                "osfi_reference": "Model development should include monitoring escalation design",
                "category": "design",
                "priority": "medium",
                "future_stage": "monitoring",
                "note": "Design stage requirement that defines approaches for future implementation"
            }
        ],

        "design_governance": [
            {
                "item": "Model owner assigned",
                "requirement": "Designate accountable individual/unit responsible for model",
                "deliverable": "Model Owner Assignment",
                "osfi_reference": "OSFI Appendix 1 requirement",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Model developer identified",
                "requirement": "Document who is developing the model",
                "deliverable": "Model Developer Identification",
                "osfi_reference": "OSFI Appendix 1 requirement",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Model ID assigned",
                "requirement": "Unique identifier for model inventory",
                "deliverable": "Model ID Assignment",
                "osfi_reference": "OSFI Appendix 1 requirement",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Model name and description defined",
                "requirement": "Clear model name and description of key features and use",
                "deliverable": "Model Name and Description",
                "osfi_reference": "OSFI Appendix 1 requirement",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Provisional model risk rating assigned",
                "requirement": "Assign initial risk rating (to be confirmed in Review stage)",
                "deliverable": "Provisional Risk Rating",
                "osfi_reference": "Principle 2.1 (provisional rating for new models)",
                "category": "design",
                "priority": "high"
            }
        ],

        "readiness_for_review": [
            {
                "item": "All Design stage deliverables complete",
                "requirement": "Complete all documentation and requirements for Design stage",
                "deliverable": "Design Stage Completion Checklist",
                "osfi_reference": "Principle 3.3",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Model documentation meets standards for independent review",
                "requirement": "Documentation adequate for independent validation per Principle 3.4",
                "deliverable": "Review-Ready Documentation Package",
                "osfi_reference": "Principle 3.4",
                "category": "design",
                "priority": "critical"
            },
            {
                "item": "Model reviewer identified and assigned",
                "requirement": "Independent reviewer assigned for validation stage",
                "deliverable": "Model Reviewer Assignment",
                "osfi_reference": "Principle 3.4",
                "category": "design",
                "priority": "high"
            },
            {
                "item": "Review scope and criteria defined based on model risk rating",
                "requirement": "Define review scope commensurate with risk rating per Principle 2.3",
                "deliverable": "Review Scope Definition",
                "osfi_reference": "Principle 2.3",
                "category": "design",
                "priority": "high"
            }
        ]
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_stage_name(stage: str) -> str:
    """Get formal OSFI E-23 name for lifecycle stage."""
    return OSFI_LIFECYCLE_COMPONENTS.get(stage, {}).get("name", stage.capitalize())

def get_stage_principles(stage: str) -> List[str]:
    """Get OSFI Principles applicable to lifecycle stage."""
    return OSFI_LIFECYCLE_COMPONENTS.get(stage, {}).get("principles", [])

def get_principle_text(principle_number: str) -> str:
    """Get full text of OSFI Principle."""
    return OSFI_PRINCIPLES.get(principle_number, "Unknown principle")

def is_ai_ml_model(project_description: str) -> bool:
    """
    Determine if model is AI/ML based on description.
    Used to include AI/ML specific requirements.
    """
    description_lower = project_description.lower()
    ai_ml_indicators = [
        "ai", "artificial intelligence", "ml", "machine learning",
        "neural network", "deep learning", "algorithm", "predictive",
        "random forest", "gradient boost", "decision tree", "regression"
    ]
    return any(indicator in description_lower for indicator in ai_ml_indicators)
