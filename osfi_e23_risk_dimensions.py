"""
OSFI E-23 Risk Dimensions Framework

This module defines the 6 Risk Dimensions used for model risk assessment
under OSFI Guideline E-23 Model Risk Management.

Risk Dimensions (constant across all models):
1. Misuse & Unintended Harm Potential
2. Output Reliability & Integrity
3. Fairness & Customer Impact
4. Operational & Security Risk
5. Model Complexity & Opacity
6. Governance & Oversight

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
                "id": "model_type",
                "name": "Model type",
                "type": FactorType.QUALITATIVE.value,
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
            }
        ]
    }
}


# =============================================================================
# DIMENSION ORDER (for consistent display)
# =============================================================================

DIMENSION_ORDER = [
    "misuse_unintended_harm",
    "output_reliability",
    "fairness_customer_impact",
    "operational_security",
    "complexity_opacity",
    "governance_oversight"
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
