#!/usr/bin/env python3
"""
Test script to verify the risk dimension extraction integration with assess_model_risk.

Tests:
1. Phase 1: assess_model_risk without extracted_factors returns extraction prompt
2. Phase 2: assess_model_risk with extracted_factors returns deterministic scores
3. NOT_STATED factors default to Medium and are tracked
4. Validation issues are reported
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import MCPServer


def test_phase1_extraction_prompt():
    """Test Phase 1: Returns extraction prompt when no extracted_factors provided."""
    print("=" * 80)
    print("TEST 1: Phase 1 - Extraction Prompt Generation")
    print("=" * 80)

    server = MCPServer()
    # Mark introduction as shown to bypass workflow check
    server.introduction_shown = True

    result = server._assess_model_risk({
        "projectName": "Credit Scoring Model",
        "projectDescription": """
        We are developing a credit scoring model using machine learning.
        The model processes approximately 50,000 loan applications per year
        with potential exposure of $25 million. It uses a gradient boosting
        ensemble with 200 features trained on 2 million historical records.
        The model influences lending decisions but final approval requires
        human review. Data includes customer demographics, transaction history,
        and credit bureau information.
        """,
        "currentStage": "design"
    })

    # Verify Phase 1 response structure
    assert result.get("phase") == "extraction", f"Expected phase='extraction', got {result.get('phase')}"
    assert "extraction_request" in result, "Missing extraction_request"
    assert "extraction_prompt" in result["extraction_request"], "Missing extraction_prompt"
    assert "next_step" in result, "Missing next_step guidance"
    assert "risk_dimensions" in result, "Missing risk_dimensions info"

    print("✅ Phase 1 returns extraction prompt correctly")
    print(f"   - Phase: {result['phase']}")
    print(f"   - Dimensions: {result['risk_dimensions']['count']}")
    print(f"   - Factors: {result['risk_dimensions']['total_factors']}")
    print(f"   - Extraction prompt length: {len(result['extraction_request']['extraction_prompt'])} chars")

    return True


def test_phase2_with_extracted_factors():
    """Test Phase 2: Deterministic scoring with extracted factors."""
    print("\n" + "=" * 80)
    print("TEST 2: Phase 2 - Deterministic Scoring with Extracted Factors")
    print("=" * 80)

    server = MCPServer()
    server.introduction_shown = True

    # Simulate Claude's extraction response
    extracted_factors = {
        "extraction_metadata": {
            "confidence_notes": "Most values clearly stated in description"
        },
        "dimensions": {
            "misuse_unintended_harm": {
                "financial_exposure": {"value": 25000000, "evidence": "$25 million"},
                "decision_volume": {"value": 50000, "evidence": "50,000 applications per year"},
                "scope_expansion": {"value": "medium", "evidence": "influences lending decisions"},
                "reversibility": {"value": "NOT_STATED", "evidence": None}
            },
            "output_reliability": {
                "error_rate": {"value": "NOT_STATED", "evidence": None},
                "output_consistency": {"value": "NOT_STATED", "evidence": None},
                "drift_rate": {"value": "NOT_STATED", "evidence": None},
                "explainability": {"value": "medium", "evidence": "gradient boosting ensemble"},
                "edge_cases": {"value": "NOT_STATED", "evidence": None}
            },
            "fairness_customer_impact": {
                "disparate_impact": {"value": "NOT_STATED", "evidence": None},
                "customer_complaints": {"value": "NOT_STATED", "evidence": None},
                "population_affected": {"value": 50000, "evidence": "50,000 applications"},
                "decision_type": {"value": "high", "evidence": "influences lending decisions"},
                "adverse_action_severity": {"value": "high", "evidence": "loan approval"},
                "vulnerable_population": {"value": "NOT_STATED", "evidence": None}
            },
            "operational_security": {
                "uptime_requirement": {"value": "NOT_STATED", "evidence": None},
                "recovery_time_objective": {"value": "NOT_STATED", "evidence": None},
                "third_party_dependencies": {"value": "NOT_STATED", "evidence": None},
                "data_sensitivity": {"value": "critical", "evidence": "credit bureau information"},
                "attack_surface": {"value": "NOT_STATED", "evidence": None},
                "fallback_available": {"value": "low", "evidence": "human review"}
            },
            "complexity_opacity": {
                "feature_count": {"value": 200, "evidence": "200 features"},
                "training_data_volume": {"value": 2000000, "evidence": "2 million historical records"},
                "model_type": {"value": "medium", "evidence": "gradient boosting ensemble"},
                "autonomy_level": {"value": "medium", "evidence": "influences but human review"},
                "self_learning": {"value": "NOT_STATED", "evidence": None}
            },
            "governance_oversight": {
                "override_rate": {"value": "NOT_STATED", "evidence": None},
                "validation_recency": {"value": "NOT_STATED", "evidence": None},
                "human_review": {"value": "medium", "evidence": "final approval requires human review"},
                "regulatory_scrutiny": {"value": "high", "evidence": "lending decisions"},
                "model_ownership": {"value": "NOT_STATED", "evidence": None}
            }
        }
    }

    result = server._assess_model_risk({
        "projectName": "Credit Scoring Model",
        "projectDescription": "Credit scoring model for loan applications.",
        "currentStage": "design",
        "extracted_factors": extracted_factors
    })

    # Verify Phase 2 response structure
    assert result.get("phase") == "assessment_complete", f"Expected phase='assessment_complete', got {result.get('phase')}"
    assert "risk_score" in result, "Missing risk_score"
    assert "risk_level" in result, "Missing risk_level"
    assert "dimension_assessment" in result, "Missing dimension_assessment"
    assert "factor_scores" in result, "Missing factor_scores"
    assert "not_stated_factors" in result, "Missing not_stated_factors"
    assert "governance_requirements" in result, "Missing governance_requirements"

    print("✅ Phase 2 returns deterministic assessment correctly")
    print(f"   - Risk Level: {result['risk_level']}")
    print(f"   - Risk Score: {result['risk_score']}")
    print(f"   - NOT_STATED Factors: {result['not_stated_factors']['count']}")

    return True


def test_not_stated_handling():
    """Test that NOT_STATED factors default to Medium and are tracked."""
    print("\n" + "=" * 80)
    print("TEST 3: NOT_STATED Handling - Defaults to Medium")
    print("=" * 80)

    from risk_dimension_extraction import process_extraction_response

    # Extraction with mostly NOT_STATED values
    extraction = {
        "dimensions": {
            "misuse_unintended_harm": {
                "financial_exposure": {"value": "NOT_STATED", "evidence": None},
                "decision_volume": {"value": 1000, "evidence": "1000 decisions"},
                "scope_expansion": {"value": "NOT_STATED", "evidence": None},
                "reversibility": {"value": "NOT_STATED", "evidence": None}
            }
        }
    }

    result = process_extraction_response(extraction)

    # Verify NOT_STATED handling
    not_stated = result["not_stated_summary"]
    assert not_stated["count"] > 0, "Expected NOT_STATED factors"

    # Check that NOT_STATED factors get Medium (score = 2)
    factor_scores = result["factor_scores"].get("misuse_unintended_harm", [])
    for score in factor_scores:
        if score["is_not_stated"]:
            assert score["risk_level"] == "medium", f"Expected NOT_STATED to default to medium, got {score['risk_level']}"
            assert score["numeric_score"] == 2, f"Expected score=2 for medium, got {score['numeric_score']}"

    print("✅ NOT_STATED factors correctly default to Medium (score=2)")
    print(f"   - Total NOT_STATED: {not_stated['count']}")
    print(f"   - Impact note: {not_stated['note']}")

    return True


def test_validation_issues_reported():
    """Test that validation issues are reported correctly."""
    print("\n" + "=" * 80)
    print("TEST 4: Validation Issues Reporting")
    print("=" * 80)

    from risk_dimension_extraction import validate_extraction_response

    # Extraction with invalid values
    extraction = {
        "dimensions": {
            "misuse_unintended_harm": {
                "financial_exposure": {"value": "invalid_not_a_number", "evidence": None},
                "decision_volume": {"value": 1000, "evidence": "valid"},
                "scope_expansion": {"value": "invalid_level", "evidence": None},
                "reversibility": {"value": "low", "evidence": "valid"}
            }
        }
    }

    validated, issues = validate_extraction_response(extraction)

    # Should have validation issues
    assert len(issues) > 0, "Expected validation issues for invalid values"

    print("✅ Validation issues correctly reported")
    print(f"   - Issues found: {len(issues)}")
    for issue in issues:
        print(f"   - {issue}")

    return True


def test_full_integration():
    """Test full integration with MCP server."""
    print("\n" + "=" * 80)
    print("TEST 5: Full MCP Server Integration")
    print("=" * 80)

    server = MCPServer()
    server.introduction_shown = True

    # Phase 1: Get extraction prompt
    phase1_result = server._assess_model_risk({
        "projectName": "Test Model",
        "projectDescription": "A machine learning model for testing.",
        "currentStage": "design"
    })

    assert phase1_result["phase"] == "extraction"

    # Phase 2: Submit extracted factors
    phase2_result = server._assess_model_risk({
        "projectName": "Test Model",
        "projectDescription": "A machine learning model for testing.",
        "currentStage": "design",
        "extracted_factors": {
            "dimensions": {
                "misuse_unintended_harm": {
                    "financial_exposure": {"value": 5000000, "evidence": "test"},
                    "decision_volume": {"value": 10000, "evidence": "test"},
                    "scope_expansion": {"value": "low", "evidence": "test"},
                    "reversibility": {"value": "medium", "evidence": "test"}
                }
            }
        }
    })

    assert phase2_result["phase"] == "assessment_complete"
    assert "risk_level" in phase2_result
    assert "governance_requirements" in phase2_result

    print("✅ Full MCP integration works correctly")
    print(f"   - Phase 1 returns extraction prompt")
    print(f"   - Phase 2 returns: {phase2_result['risk_level']} risk")

    return True


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RISK DIMENSION EXTRACTION INTEGRATION TESTS")
    print("=" * 80 + "\n")

    tests = [
        ("Phase 1 - Extraction Prompt", test_phase1_extraction_prompt),
        ("Phase 2 - Deterministic Scoring", test_phase2_with_extracted_factors),
        ("NOT_STATED Handling", test_not_stated_handling),
        ("Validation Issues", test_validation_issues_reported),
        ("Full Integration", test_full_integration),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ TEST ERROR: {name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    if failed > 0:
        sys.exit(1)
    else:
        print("\n✅ ALL TESTS PASSED!")
        sys.exit(0)
