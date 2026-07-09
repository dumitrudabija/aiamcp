"""
OSFI E-23 Risk Dimensions Framework

This module defines the 8 Risk Dimensions used for model risk assessment
under OSFI Guideline E-23 Model Risk Management.

Risk Dimensions (constant across all models):
1. Misuse & Unintended Harm Potential
2. Output Reliability & Integrity
3. Fairness & Customer Impact
4. Operational & Security Risk
5. Model Complexity & Opacity
6. Governance & Oversight
7. Data Provenance & Supply Chain Risk
8. Systemic & Concentration Risk

Each dimension contains multiple factors (quantitative and qualitative)
that are assessed on a 4-level scale: Low, Medium, High, Critical.

Reference: OSFI Guideline E-23 – Model Risk Management (2027)
Principle 2.2: Model Risk Rating
"""

from typing import Dict, List, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for dimension and factor assessment."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    NOT_ASSESSED = "not_assessed"


class FactorType(Enum):
    """Types of risk factors."""
    QUANTITATIVE = "quantitative"
    QUALITATIVE = "qualitative"


# =============================================================================
# RISK DIMENSION DEFINITIONS
# =============================================================================

RISK_DIMENSIONS = {
    "misuse_unintended_harm": {
        "id": "misuse_unintended_harm",
        "name": "Misuse & Unintended Harm Potential",
        "short_name": "Misuse & Harm",
        "core_question": "Can the model be used in ways that cause harm beyond its intended purpose?",
        "osfi_principles": ["1.3", "3.2"],
        "factors": [
            {
                "id": "financial_exposure",
                "name": "Financial exposure if misused",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "dollars",
                "thresholds": {
                    "low": {"max": 1_000_000, "description": "<$1M"},
                    "medium": {"min": 1_000_000, "max": 10_000_000, "description": "$1-10M"},
                    "high": {"min": 10_000_000, "max": 100_000_000, "description": "$10-100M"},
                    "critical": {"min": 100_000_000, "description": ">$100M"}
                },
                "invert_scale": False  # Higher value = higher risk
            },
            {
                "id": "decision_volume",
                "name": "Number of decisions influenced annually",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "count",
                "thresholds": {
                    "low": {"max": 1_000, "description": "<1,000"},
                    "medium": {"min": 1_000, "max": 50_000, "description": "1,000-50,000"},
                    "high": {"min": 50_000, "max": 500_000, "description": "50,000-500,000"},
                    "critical": {"min": 500_000, "description": ">500,000"}
                },
                "invert_scale": False
            },
            {
                "id": "scope_expansion",
                "name": "Can outputs be used beyond original scope?",
                "type": FactorType.QUALITATIVE.value,
                "weight": 1.0,
                "model_type_interpretation": {
                    "2-5": "GenAI/agentic systems are more prone to scope creep than traditional ML - consider whether guardrails actually constrain use to the intended purpose."
                },
                "levels": {
                    "low": "No, tightly constrained",
                    "medium": "Limited secondary uses",
                    "high": "Multiple potential uses",
                    "critical": "Broad applicability"
                }
            },
            {
                "id": "reversibility",
                "name": "Reversibility of decisions",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Easily reversed",
                    "medium": "Reversible with effort",
                    "high": "Difficult to reverse",
                    "critical": "Irreversible"
                }
            },
            {
                "id": "confabulation_false_authority",
                "name": "Confabulation / false-authority risk (GenAI)",
                "type": FactorType.QUALITATIVE.value,
                "weight": 1.0,
                "allow_na": True,
                "model_type_interpretation": {
                    "1": "Not applicable for traditional, non-generative models - mark N/A.",
                    "2-5": "Applies directly to GenAI/RAG/agentic systems; check whether outputs are grounded in retrieved or verified sources."
                },
                "levels": {
                    "low": "Outputs are grounded/cited or model is non-generative; confabulation rare",
                    "medium": "Occasional unsupported claims; users advised to verify",
                    "high": "Frequent confident but unverifiable outputs; limited grounding controls",
                    "critical": "High-stakes confabulation risk with no fact-checking or human review"
                }
            }
        ]
    },

    "output_reliability": {
        "id": "output_reliability",
        "name": "Output Reliability & Integrity",
        "short_name": "Reliability",
        "core_question": "How trustworthy and consistent are the model's outputs?",
        "osfi_principles": ["3.3", "3.4", "3.6"],
        "factors": [
            {
                "id": "error_rate",
                "name": "Error rate on validation set",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "percentage",
                "thresholds": {
                    "low": {"max": 1, "description": "<1%"},
                    "medium": {"min": 1, "max": 5, "description": "1-5%"},
                    "high": {"min": 5, "max": 10, "description": "5-10%"},
                    "critical": {"min": 10, "description": ">10%"}
                },
                "invert_scale": False  # Higher error = higher risk
            },
            {
                "id": "output_consistency",
                "name": "Output consistency (same input, same output)",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "percentage",
                "thresholds": {
                    "low": {"min": 99, "description": ">99%"},
                    "medium": {"min": 95, "max": 99, "description": "95-99%"},
                    "high": {"min": 90, "max": 95, "description": "90-95%"},
                    "critical": {"max": 90, "description": "<90%"}
                },
                "invert_scale": True  # Lower consistency = higher risk
            },
            {
                "id": "drift_rate",
                "name": "Drift from baseline (monthly)",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "percentage",
                "thresholds": {
                    "low": {"max": 2, "description": "<2%"},
                    "medium": {"min": 2, "max": 5, "description": "2-5%"},
                    "high": {"min": 5, "max": 10, "description": "5-10%"},
                    "critical": {"min": 10, "description": ">10%"}
                },
                "invert_scale": False
            },
            {
                "id": "explainability",
                "name": "Explainability of outputs",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Fully explainable",
                    "medium": "Mostly explainable",
                    "high": "Partially explainable",
                    "critical": "Black box"
                }
            },
            {
                "id": "edge_cases",
                "name": "Known edge cases documented?",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Comprehensive",
                    "medium": "Most identified",
                    "high": "Some gaps",
                    "critical": "Significant unknowns"
                }
            },
            {
                "id": "genai_output_quality_benchmark",
                "name": "GenAI output quality benchmark",
                "type": FactorType.QUALITATIVE.value,
                "weight": 1.0,
                "allow_na": True,
                "model_type_interpretation": {
                    "1": "Not applicable for non-generative models - mark N/A.",
                    "3-5": "For RAG/agentic systems, benchmarking should also cover retrieval relevance and tool-call correctness, not just generated text quality."
                },
                "levels": {
                    "low": "Benchmarked against validation set/human evaluation with documented results, or non-generative",
                    "medium": "Some benchmarking performed but not comprehensive or independently reviewed",
                    "high": "Limited or informal benchmarking; no systematic quality evaluation",
                    "critical": "No output quality benchmarking performed for a generative model in production use"
                }
            }
        ]
    },

    "fairness_customer_impact": {
        "id": "fairness_customer_impact",
        "name": "Fairness & Customer Impact",
        "short_name": "Fairness & Impact",
        "core_question": "Does the model produce equitable outcomes? What's the impact on customers?",
        "osfi_principles": ["2.2", "3.2"],
        "factors": [
            {
                "id": "disparate_impact",
                "name": "Disparate impact ratio across protected groups",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "ratio",
                "thresholds": {
                    "low": {"min": 0.9, "description": ">0.9"},
                    "medium": {"min": 0.8, "max": 0.9, "description": "0.8-0.9"},
                    "high": {"min": 0.7, "max": 0.8, "description": "0.7-0.8"},
                    "critical": {"max": 0.7, "description": "<0.7"}
                },
                "invert_scale": True  # Lower ratio = higher risk
            },
            {
                "id": "customer_complaints",
                "name": "Customer complaints attributable to model",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "percentage",
                "thresholds": {
                    "low": {"max": 0.1, "description": "<0.1%"},
                    "medium": {"min": 0.1, "max": 0.5, "description": "0.1-0.5%"},
                    "high": {"min": 0.5, "max": 2, "description": "0.5-2%"},
                    "critical": {"min": 2, "description": ">2%"}
                },
                "invert_scale": False
            },
            {
                "id": "population_affected",
                "name": "Population affected annually",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "count",
                "thresholds": {
                    "low": {"max": 10_000, "description": "<10,000"},
                    "medium": {"min": 10_000, "max": 100_000, "description": "10,000-100,000"},
                    "high": {"min": 100_000, "max": 1_000_000, "description": "100,000-1M"},
                    "critical": {"min": 1_000_000, "description": ">1M"}
                },
                "invert_scale": False
            },
            {
                "id": "decision_type",
                "name": "Decision type",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Informational only",
                    "medium": "Influences decision",
                    "high": "Significant factor",
                    "critical": "Sole determinant"
                }
            },
            {
                "id": "adverse_action_severity",
                "name": "Adverse action severity",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Minor inconvenience",
                    "medium": "Moderate impact",
                    "high": "Significant harm",
                    "critical": "Severe/irreversible harm"
                }
            },
            {
                "id": "vulnerable_population",
                "name": "Vulnerable population exposure",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "None",
                    "medium": "Limited",
                    "high": "Moderate",
                    "critical": "Significant"
                }
            },
            {
                "id": "predeployment_fairness_testing",
                "name": "Pre-deployment fairness / bias testing",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Comprehensive pre-deployment fairness testing completed and documented across protected groups",
                    "medium": "Some fairness testing performed but not comprehensive across all relevant groups",
                    "high": "Limited or ad hoc fairness testing; gaps in protected-group coverage",
                    "critical": "No pre-deployment fairness/bias testing conducted"
                }
            }
        ]
    },

    "operational_security": {
        "id": "operational_security",
        "name": "Operational & Security Risk",
        "short_name": "Operations & Security",
        "core_question": "What are the infrastructure, availability, and security risks?",
        "osfi_principles": ["2.2", "3.5"],
        "factors": [
            {
                "id": "uptime_requirement",
                "name": "Uptime requirement",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "percentage",
                "thresholds": {
                    "low": {"max": 95, "description": "<95%"},
                    "medium": {"min": 95, "max": 99, "description": "95-99%"},
                    "high": {"min": 99, "max": 99.9, "description": "99-99.9%"},
                    "critical": {"min": 99.9, "description": ">99.9%"}
                },
                "invert_scale": False  # Higher uptime requirement = higher operational risk
            },
            {
                "id": "recovery_time_objective",
                "name": "Recovery time objective",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "hours",
                "thresholds": {
                    "low": {"min": 24, "description": ">24h"},
                    "medium": {"min": 4, "max": 24, "description": "4-24h"},
                    "high": {"min": 1, "max": 4, "description": "1-4h"},
                    "critical": {"max": 1, "description": "<1h"}
                },
                "invert_scale": True  # Lower RTO = higher criticality = higher risk
            },
            {
                "id": "third_party_dependencies",
                "name": "Third-party dependencies",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "count",
                "thresholds": {
                    "low": {"max": 1, "description": "0-1"},
                    "medium": {"min": 2, "max": 3, "description": "2-3"},
                    "high": {"min": 4, "max": 6, "description": "4-6"},
                    "critical": {"min": 7, "description": ">6"}
                },
                "invert_scale": False
            },
            {
                "id": "data_sensitivity",
                "name": "Data sensitivity",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Public data",
                    "medium": "Internal only",
                    "high": "Confidential",
                    "critical": "PII/regulated data"
                }
            },
            {
                "id": "attack_surface",
                "name": "Attack surface exposure",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Internal only",
                    "medium": "Limited external",
                    "high": "Broad external",
                    "critical": "Public-facing"
                }
            },
            {
                "id": "fallback_available",
                "name": "Fallback/manual process available?",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Full manual backup",
                    "medium": "Partial backup",
                    "high": "Limited backup",
                    "critical": "No backup"
                }
            },
            {
                "id": "adversarial_robustness_testing",
                "name": "Adversarial robustness / prompt-injection testing",
                "type": FactorType.QUALITATIVE.value,
                "allow_na": True,
                "levels": {
                    "low": "Adversarial/prompt-injection testing completed with documented mitigations, or not applicable",
                    "medium": "Some adversarial testing performed but not comprehensive",
                    "high": "Limited adversarial testing; known gaps in defenses",
                    "critical": "No adversarial robustness or prompt-injection testing conducted for an exposed system"
                }
            }
        ]
    },

    "complexity_opacity": {
        "id": "complexity_opacity",
        "name": "Model Complexity & Opacity",
        "short_name": "Complexity",
        "core_question": "How complex is the model and how well can it be understood?",
        "osfi_principles": ["2.2", "3.3"],
        "factors": [
            {
                "id": "feature_count",
                "name": "Number of features/parameters",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "count",
                "thresholds": {
                    "low": {"max": 50, "description": "<50"},
                    "medium": {"min": 50, "max": 500, "description": "50-500"},
                    "high": {"min": 500, "max": 10_000, "description": "500-10,000"},
                    "critical": {"min": 10_000, "description": ">10,000"}
                },
                "invert_scale": False
            },
            {
                "id": "training_data_volume",
                "name": "Training data volume",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "records",
                "thresholds": {
                    "low": {"max": 100_000, "description": "<100K records"},
                    "medium": {"min": 100_000, "max": 1_000_000, "description": "100K-1M"},
                    "high": {"min": 1_000_000, "max": 100_000_000, "description": "1M-100M"},
                    "critical": {"min": 100_000_000, "description": ">100M"}
                },
                "invert_scale": False
            },
            {
                "id": "model_architecture_type",
                "name": "Model architecture type",
                "type": FactorType.QUALITATIVE.value,
                "weight": 1.0,
                "levels": {
                    "low": "Linear/rules-based",
                    "medium": "Ensemble/boosted",
                    "high": "Neural network",
                    "critical": "Deep learning/LLM"
                }
            },
            {
                "id": "autonomy_level",
                "name": "Autonomy level",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "No autonomy",
                    "medium": "Recommends only",
                    "high": "Auto-executes with override",
                    "critical": "Fully autonomous"
                }
            },
            {
                "id": "self_learning",
                "name": "Self-learning/adaptive?",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Static",
                    "medium": "Periodic retrain",
                    "high": "Continuous learning",
                    "critical": "Autonomous adaptation"
                }
            },
            {
                "id": "decision_path_traceability",
                "name": "Decision path traceability",
                "type": FactorType.QUALITATIVE.value,
                "weight": 1.0,
                "model_type_interpretation": {
                    "3-5": "For RAG/agentic systems, confirm traceability covers retrieved sources and any tool/action steps, not just the final generated text."
                },
                "levels": {
                    "low": "Every output can be traced back to the specific inputs, rules, retrieved sources, or model steps that produced it (full lineage/audit trail available).",
                    "medium": "Most outputs can be traced to their contributing inputs or sources with reasonable effort; minor gaps in lineage exist.",
                    "high": "Tracing a specific output back to its inputs/sources is difficult, requires specialized tooling or expertise, or lineage is materially incomplete.",
                    "critical": "Outputs cannot be traced back to the specific inputs, rules, or sources that produced them (fully opaque decision path)."
                }
            },
            {
                "id": "pipeline_component_count",
                "name": "Pipeline component count",
                "type": FactorType.QUALITATIVE.value,
                "weight": 1.0,
                "model_type_interpretation": {
                    "4-5": "Agentic workflows typically chain several tools/services by design - expect this factor to score higher unless the pipeline is unusually simple and well-documented."
                },
                "levels": {
                    "low": "A single, self-contained component (e.g., one model or service) produces the output with no chained calls to other systems.",
                    "medium": "A small number of components are chained (e.g., 2-3 systems, services, tools, or retrieval steps) with clear, documented handoffs.",
                    "high": "Multiple components are chained (e.g., 4-6 systems, services, tools, or retrieval/agent steps) with some undocumented or complex handoffs.",
                    "critical": "Many components are chained (7+ systems, services, tools, or agents), or the end-to-end pipeline is not fully documented or understood."
                }
            },
            {
                "id": "model_update_velocity",
                "name": "Model / configuration update velocity",
                "type": FactorType.QUALITATIVE.value,
                "weight": 1.0,
                "model_type_interpretation": {
                    "2-5": "For GenAI/vendor-hosted systems, consider whether the underlying foundation model can be updated by the vendor outside the institution's own change control."
                },
                "levels": {
                    "low": "Model or configuration changes are infrequent and scheduled (e.g., annually or less), each going through full change control and testing before release.",
                    "medium": "Model or configuration is updated periodically (e.g., quarterly) through a controlled, documented release process.",
                    "high": "Model or configuration is updated frequently (e.g., monthly or more), or updates sometimes occur outside a fully controlled release process.",
                    "critical": "Model or configuration changes continuously or automatically in production (e.g., online learning, continuous fine-tuning, silent vendor-pushed updates) without a discrete, reviewable release process."
                }
            }
        ]
    },

    "governance_oversight": {
        "id": "governance_oversight",
        "name": "Governance & Oversight",
        "short_name": "Governance",
        "core_question": "How robust are the controls and accountability structures?",
        "osfi_principles": ["1.1", "1.2", "2.3"],
        "factors": [
            {
                "id": "override_rate",
                "name": "Override rate by humans",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "percentage",
                "thresholds": {
                    "low": {"max": 0, "description": "N/A", "allow_na": True},
                    "medium": {"max": 5, "description": "<5%"},
                    "high": {"min": 5, "max": 20, "description": "5-20%"},
                    "critical": {"min": 20, "description": ">20%"}
                },
                "invert_scale": False,
                "allow_na": True  # N/A is valid for Low risk
            },
            {
                "id": "validation_recency",
                "name": "Time since last validation",
                "type": FactorType.QUANTITATIVE.value,
                "unit": "months",
                "thresholds": {
                    "low": {"max": 6, "description": "<6 months"},
                    "medium": {"min": 6, "max": 12, "description": "6-12 months"},
                    "high": {"min": 12, "max": 24, "description": "12-24 months"},
                    "critical": {"min": 24, "description": ">24 months"}
                },
                "invert_scale": False  # Longer time = higher risk
            },
            {
                "id": "human_review",
                "name": "Human review requirement",
                "type": FactorType.QUALITATIVE.value,
                "weight": 1.0,
                "model_type_interpretation": {
                    "4-5": "For agentic/autonomous systems, confirm review requirements cover the actions taken (e.g. tool calls, writes), not only the final recommendation text."
                },
                "levels": {
                    "low": "All decisions reviewed",
                    "medium": "Sample review",
                    "high": "Exception-based",
                    "critical": "No review"
                }
            },
            {
                "id": "regulatory_scrutiny",
                "name": "Regulatory scrutiny level",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "None",
                    "medium": "Low",
                    "high": "Moderate",
                    "critical": "High (SR 11-7, fair lending)"
                }
            },
            {
                "id": "model_ownership",
                "name": "Model owner accountability",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Clear single owner",
                    "medium": "Shared ownership",
                    "high": "Unclear",
                    "critical": "None assigned"
                }
            },
            {
                "id": "ai_incident_response",
                "name": "AI-specific incident response",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Documented AI-specific incident response plan, tested and current",
                    "medium": "Incident response plan exists but not AI-specific or not recently tested",
                    "high": "Incident response plan is informal or incomplete",
                    "critical": "No incident response plan for AI-related failures or misuse"
                }
            },
            {
                "id": "production_monitoring_alerting",
                "name": "Production monitoring & alerting coverage",
                "type": FactorType.QUALITATIVE.value,
                "weight": 1.0,
                "model_type_interpretation": {
                    "4-5": "For agentic/autonomous systems, confirm monitoring covers action-taking behavior (e.g. tool calls, writes) and not just output content."
                },
                "levels": {
                    "low": "Automated monitoring and alerting actively covers model behavior, drift, errors, and anomalies in production, with defined thresholds and a documented on-call/response process.",
                    "medium": "Automated monitoring exists for key metrics, but alerting coverage or thresholds have some gaps (e.g., partial coverage of behavior, drift, or error signals).",
                    "high": "Monitoring is largely manual or ad hoc, and alerting is limited or inconsistent, so issues may go undetected for extended periods.",
                    "critical": "No automated monitoring or alerting exists for model behavior, drift, errors, or anomalies in production."
                }
            }
        ]
    },

    "data_provenance_supply_chain": {
        "id": "data_provenance_supply_chain",
        "name": "Data Provenance & Supply Chain Risk",
        "short_name": "Data Provenance & Supply Chain",
        "core_question": "Are the model's data, training inputs, fine-tuning data, validation data, RAG grounding sources, third-party components, and synthetic data understood, approved, traceable, and controlled?",
        "osfi_principles": ["3.2", "3.5"],
        "factors": [
            {
                "id": "training_data_documentation",
                "name": "Training data documentation",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Data provenance is fully documented for all material datasets, including source, owner, permitted use, lineage, and known limitations.",
                    "medium": "Most material data sources are documented, but some metadata is incomplete.",
                    "high": "Data provenance is partially documented, but key sources, ownership, lineage, or permitted use are unclear.",
                    "critical": "Training, fine-tuning, validation, or grounding data is undocumented, unknown, unapproved, or untraceable."
                }
            },
            {
                "id": "pii_training_context_data",
                "name": "PII in training or context data",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "PII/confidential data exposure is documented, minimized, controlled, and tested for leakage in outputs.",
                    "medium": "PII/confidential exposure is documented and controlled, but leakage testing or retention evidence is incomplete.",
                    "high": "PII/confidential data may be present, but controls, retention rules, or leakage testing are incomplete or unverified.",
                    "critical": "Sensitive data exposure is known or likely, with no documented controls, retention safeguards, or leakage testing."
                }
            },
            {
                "id": "third_party_oss_component_integrity",
                "name": "Third-party / open-source component integrity",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "All material third-party/open-source components are approved, versioned, monitored, and covered by security/vendor review.",
                    "medium": "Most components are approved and monitored, but some non-critical dependencies lack complete evidence.",
                    "high": "Material dependencies exist with incomplete approval, versioning, vulnerability monitoring, or vendor due diligence.",
                    "critical": "Critical components are unapproved, unverified, unsupported, unmonitored, or cannot be replaced."
                }
            },
            {
                "id": "synthetic_data_quality",
                "name": "Synthetic data quality",
                "type": FactorType.QUALITATIVE.value,
                "allow_na": True,
                "levels": {
                    "low": "No synthetic data is used, or synthetic data is fully documented and validated for representativeness, leakage, distortion, and bias.",
                    "medium": "Synthetic data is used and partially validated, but some validation dimensions are incomplete.",
                    "high": "Synthetic data is used materially, but validation is weak, incomplete, or not independently reviewed.",
                    "critical": "Synthetic data materially affects training/testing/monitoring with no validation or known distortion/leakage issues."
                }
            }
        ]
    },

    "systemic_concentration_risk": {
        "id": "systemic_concentration_risk",
        "name": "Systemic & Concentration Risk",
        "short_name": "Systemic & Concentration",
        "core_question": "Do risks exist that are not fully visible when assessing one model in isolation, because many models, processes, or controls depend on the same cloud provider, AI platform, foundation model, data provider, or vendor?",
        "osfi_principles": ["2.1", "2.2"],
        "factors": [
            {
                "id": "infrastructure_concentration",
                "name": "Infrastructure concentration",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Infrastructure is resilient, substitutable, tested, and not dependent on a single irreplaceable provider/component.",
                    "medium": "Some concentration exists, but there is a documented recovery, failover, or substitution plan.",
                    "high": "The model depends on a single provider/component and substitution is difficult, untested, or undocumented.",
                    "critical": "The model depends on a non-substitutable provider/component whose outage would stop a critical business process."
                }
            },
            {
                "id": "foundation_model_vendor_concentration",
                "name": "Foundation model / vendor concentration",
                "type": FactorType.QUALITATIVE.value,
                "levels": {
                    "low": "Model/vendor dependency is documented, version-controlled, monitored, and substitutable.",
                    "medium": "Dependency is documented and monitored, but substitution or vendor change controls are incomplete.",
                    "high": "The model depends on a common vendor/foundation model with weak substitution, weak update controls, or limited transparency.",
                    "critical": "Critical function depends on a single foundation model/vendor with no substitution plan, version control, or vendor-change testing."
                }
            },
            {
                "id": "portfolio_level_ai_estate_concentration",
                "name": "Portfolio-level AI estate concentration",
                "type": FactorType.QUALITATIVE.value,
                "allow_review_required": True,
                "levels": {
                    "low": "No single provider supports a material share of critical AI functions, or concentration is actively mitigated.",
                    "medium": "Some concentration exists, but it is documented, monitored, and covered by contingency planning.",
                    "high": "A single provider/model/platform supports a material share of important functions with incomplete mitigation.",
                    "critical": "A single provider/model/platform supports a material share of critical functions with no effective substitution or contingency plan."
                }
            }
        ]
    }
}


# =============================================================================
# FACTOR WEIGHT DEFAULTS
# =============================================================================
# Every factor gets an explicit "weight" (default 1.0 = equal weighting).
# Scoring itself remains a simple unweighted average by default (see
# risk_dimension_extraction.py's `use_weights` config flag) - this default
# just guarantees the field exists on every factor for future use, without
# requiring every factor literal above to redundantly set it by hand.
for _dim in RISK_DIMENSIONS.values():
    for _factor in _dim["factors"]:
        _factor.setdefault("weight", 1.0)
del _dim, _factor


# =============================================================================
# DIMENSION ORDER (for consistent display)
# =============================================================================

DIMENSION_ORDER = [
    "misuse_unintended_harm",
    "output_reliability",
    "fairness_customer_impact",
    "operational_security",
    "complexity_opacity",
    "governance_oversight",
    "data_provenance_supply_chain",
    "systemic_concentration_risk"
]


# =============================================================================
# RISK LEVEL NUMERIC MAPPING
# =============================================================================

RISK_LEVEL_SCORES = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
    "not_assessed": 0
}

RISK_LEVEL_FROM_SCORE = {
    1: "low",
    2: "medium",
    3: "high",
    4: "critical",
    0: "not_assessed"
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_dimension(dimension_id: str) -> Optional[Dict[str, Any]]:
    """Get a dimension definition by ID."""
    return RISK_DIMENSIONS.get(dimension_id)


def get_all_dimensions() -> Dict[str, Dict[str, Any]]:
    """Get all dimension definitions."""
    return RISK_DIMENSIONS


def get_dimension_names() -> List[str]:
    """Get list of dimension names in order."""
    return [RISK_DIMENSIONS[dim_id]["name"] for dim_id in DIMENSION_ORDER]


def get_dimension_factors(dimension_id: str) -> List[Dict[str, Any]]:
    """Get all factors for a dimension."""
    dimension = get_dimension(dimension_id)
    if dimension:
        return dimension.get("factors", [])
    return []


def get_factor_by_id(dimension_id: str, factor_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific factor by dimension and factor ID."""
    factors = get_dimension_factors(dimension_id)
    for factor in factors:
        if factor["id"] == factor_id:
            return factor
    return None


def get_quantitative_factors(dimension_id: str) -> List[Dict[str, Any]]:
    """Get only quantitative factors for a dimension."""
    factors = get_dimension_factors(dimension_id)
    return [f for f in factors if f["type"] == FactorType.QUANTITATIVE.value]


def get_qualitative_factors(dimension_id: str) -> List[Dict[str, Any]]:
    """Get only qualitative factors for a dimension."""
    factors = get_dimension_factors(dimension_id)
    return [f for f in factors if f["type"] == FactorType.QUALITATIVE.value]


def get_total_factor_count() -> int:
    """Get total number of factors across all dimensions."""
    total = 0
    for dim_id in DIMENSION_ORDER:
        total += len(get_dimension_factors(dim_id))
    return total


def get_dimension_summary() -> Dict[str, Dict[str, int]]:
    """Get summary statistics for each dimension."""
    summary = {}
    for dim_id in DIMENSION_ORDER:
        dim = get_dimension(dim_id)
        quant_count = len(get_quantitative_factors(dim_id))
        qual_count = len(get_qualitative_factors(dim_id))
        summary[dim_id] = {
            "name": dim["name"],
            "quantitative": quant_count,
            "qualitative": qual_count,
            "total": quant_count + qual_count
        }
    return summary


def risk_level_to_score(level: str) -> int:
    """Convert risk level string to numeric score."""
    return RISK_LEVEL_SCORES.get(level.lower(), 0)


def score_to_risk_level(score: int) -> str:
    """Convert numeric score to risk level string."""
    # Round to nearest integer level
    rounded = max(0, min(4, round(score)))
    return RISK_LEVEL_FROM_SCORE.get(rounded, "not_assessed")


# =============================================================================
# ASSESSMENT RESULT STRUCTURE
# =============================================================================

def create_empty_assessment() -> Dict[str, Any]:
    """Create an empty assessment structure for all dimensions."""
    assessment = {
        "dimensions": {},
        "overall_risk_level": "not_assessed",
        "overall_risk_score": 0,
        "assessment_complete": False
    }

    for dim_id in DIMENSION_ORDER:
        dim = get_dimension(dim_id)
        assessment["dimensions"][dim_id] = {
            "name": dim["name"],
            "risk_level": "not_assessed",
            "risk_score": 0,
            "factors": {}
        }

        for factor in dim["factors"]:
            assessment["dimensions"][dim_id]["factors"][factor["id"]] = {
                "name": factor["name"],
                "type": factor["type"],
                "value": None,
                "risk_level": "not_assessed",
                "evidence": None
            }

    return assessment


# =============================================================================
# VALIDATION
# =============================================================================

def validate_dimension_structure() -> Dict[str, Any]:
    """Validate the dimension structure for completeness and consistency."""
    issues = []
    stats = {
        "dimensions": len(DIMENSION_ORDER),
        "total_factors": 0,
        "quantitative_factors": 0,
        "qualitative_factors": 0
    }

    for dim_id in DIMENSION_ORDER:
        dim = get_dimension(dim_id)

        if not dim:
            issues.append(f"Dimension {dim_id} not found in RISK_DIMENSIONS")
            continue

        # Check required fields
        required_fields = ["id", "name", "core_question", "factors"]
        for field in required_fields:
            if field not in dim:
                issues.append(f"Dimension {dim_id} missing required field: {field}")

        # Check factors
        factors = dim.get("factors", [])
        if not factors:
            issues.append(f"Dimension {dim_id} has no factors")

        for factor in factors:
            stats["total_factors"] += 1

            factor_required = ["id", "name", "type"]
            for field in factor_required:
                if field not in factor:
                    issues.append(f"Factor {factor.get('id', 'unknown')} in {dim_id} missing: {field}")

            if factor["type"] == FactorType.QUANTITATIVE.value:
                stats["quantitative_factors"] += 1
                if "thresholds" not in factor:
                    issues.append(f"Quantitative factor {factor['id']} missing thresholds")
            elif factor["type"] == FactorType.QUALITATIVE.value:
                stats["qualitative_factors"] += 1
                if "levels" not in factor:
                    issues.append(f"Qualitative factor {factor['id']} missing levels")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "statistics": stats
    }


# =============================================================================
# MODULE INITIALIZATION CHECK
# =============================================================================

if __name__ == "__main__":
    # Run validation when module is executed directly
    validation = validate_dimension_structure()

    print("=" * 60)
    print("OSFI E-23 Risk Dimensions Framework Validation")
    print("=" * 60)
    print(f"\nStructure Valid: {validation['valid']}")
    print(f"\nStatistics:")
    for key, value in validation['statistics'].items():
        print(f"  {key}: {value}")

    if validation['issues']:
        print(f"\nIssues Found ({len(validation['issues'])}):")
        for issue in validation['issues']:
            print(f"  - {issue}")
    else:
        print("\nNo issues found.")

    print("\n" + "=" * 60)
    print("Dimension Summary:")
    print("=" * 60)
    summary = get_dimension_summary()
    for dim_id, stats in summary.items():
        print(f"\n{stats['name']}:")
        print(f"  Quantitative: {stats['quantitative']}")
        print(f"  Qualitative: {stats['qualitative']}")
        print(f"  Total: {stats['total']}")
