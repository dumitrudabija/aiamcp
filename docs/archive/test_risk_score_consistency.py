#!/usr/bin/env python3
"""
Test Risk Score Consistency Between Step 2 and Step 4
Verifies that assess_model_risk and generate_risk_rating produce consistent scores
"""

import sys
from server import MCPServer

def test_risk_score_consistency():
    """Test that step 2 and step 4 produce consistent risk scores."""
    print("\n" + "="*80)
    print("TESTING: Risk Score Consistency Between Step 2 and Step 4")
    print("="*80)

    server = MCPServer()

    test_description = (
        "AI-powered commercial lending model using machine learning for credit risk assessment. "
        "Processes $150-200M annual lending volume. Makes automated lending decisions for loans up to $2M. "
        "Customer-facing system affecting business credit access. Uses ensemble ML models with complex feature engineering."
    )

    # Step 2: assess_model_risk
    print("\n1. Running Step 2: assess_model_risk")
    print("-" * 80)
    step2_result = server.osfi_e23_processor.assess_model_risk(
        project_name="Test Model",
        project_description=test_description
    )

    step2_score = step2_result.get("risk_score")
    step2_level = step2_result.get("risk_level")
    print(f"   Risk Score: {step2_score}")
    print(f"   Risk Level: {step2_level}")

    # Step 4: generate_risk_rating
    print("\n2. Running Step 4: generate_risk_rating")
    print("-" * 80)
    step4_result = server.osfi_e23_processor.generate_risk_rating(
        project_name="Test Model",
        project_description=test_description
    )

    step4_score = step4_result.get("overall_score")
    step4_level = step4_result.get("risk_rating")
    print(f"   Overall Score: {step4_score}")
    print(f"   Risk Rating: {step4_level}")

    # Compare
    print("\n" + "="*80)
    print("COMPARISON")
    print("="*80)
    print(f"Step 2 Score: {step2_score}")
    print(f"Step 4 Score: {step4_score}")
    print(f"Difference: {abs(step2_score - step4_score)} points")
    print()
    print(f"Step 2 Level: {step2_level}")
    print(f"Step 4 Level: {step4_level}")

    if step2_score == step4_score and step2_level == step4_level:
        print("\n✅ PASS: Scores are consistent")
        return True
    else:
        print(f"\n❌ FAIL: Scores are inconsistent")
        print(f"   Score difference: {abs(step2_score - step4_score)} points")
        if step2_level != step4_level:
            print(f"   Risk level mismatch: {step2_level} vs {step4_level}")
        return False

if __name__ == "__main__":
    success = test_risk_score_consistency()
    sys.exit(0 if success else 1)
