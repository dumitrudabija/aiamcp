#!/usr/bin/env python3
"""
Test that Step 4 (generate_risk_rating) is streamlined to focus only on risk rating.
Verifies that governance and compliance elements are NOT in Step 4 output.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from osfi_e23_processor import OSFIE23Processor


def test_step4_returns_only_risk_rating():
    """Test that Step 4 returns only risk rating information, no governance/compliance."""
    print("\n" + "="*80)
    print("TEST: Step 4 (generate_risk_rating) Streamlined Output")
    print("="*80)

    processor = OSFIE23Processor()

    project_description = """
    Our bank is developing a credit risk scoring model for retail lending.
    The model uses machine learning to predict default probability.
    It processes sensitive customer financial data and directly impacts lending decisions.
    The model will be used in production for automated credit approval.
    """

    result = processor.generate_risk_rating(
        project_name="Credit Risk Scoring Model",
        project_description=project_description
    )

    print("\nStep 4 Output Keys:")
    for key in result.keys():
        print(f"  - {key}")

    # Expected keys (SHOULD be present)
    expected_keys = [
        "project_name",
        "project_description",
        "assessment_date",
        "risk_rating",
        "risk_description",
        "overall_score",
        "risk_scores",
        "risk_factor_analysis"
    ]

    # Unexpected keys (SHOULD NOT be present - these belong in Step 5)
    unexpected_keys = [
        "governance_intensity",
        "review_frequency",
        "approval_authority",
        "governance_structure",
        "monitoring_framework",
        "documentation_requirements"
    ]

    print("\n" + "-"*80)
    print("Checking Expected Keys (should be present):")
    print("-"*80)

    all_expected_present = True
    for key in expected_keys:
        present = key in result
        status = "✅ PASS" if present else "❌ FAIL"
        print(f"{status}: {key}")
        all_expected_present = all_expected_present and present

    print("\n" + "-"*80)
    print("Checking Unexpected Keys (should NOT be present - belong in Step 5):")
    print("-"*80)

    no_unexpected_present = True
    for key in unexpected_keys:
        absent = key not in result
        status = "✅ PASS" if absent else "❌ FAIL"
        print(f"{status}: {key} {'NOT present' if absent else 'PRESENT (ERROR!)'}")
        no_unexpected_present = no_unexpected_present and absent

    print("\n" + "-"*80)
    print("Risk Rating Details:")
    print("-"*80)
    print(f"Risk Level: {result.get('risk_rating')}")
    print(f"Risk Score: {result.get('overall_score')}")
    print(f"Risk Description: {result.get('risk_description')}")

    # Check risk_scores structure
    risk_scores = result.get('risk_scores', {})
    print(f"\nRisk Scores Breakdown:")
    print(f"  Quantitative Score: {risk_scores.get('quantitative_score')}")
    print(f"  Qualitative Score: {risk_scores.get('qualitative_score')}")
    print(f"  Amplification Factor: {risk_scores.get('amplification_factor')}")

    # Check risk_factor_analysis structure
    risk_analysis = result.get('risk_factor_analysis', {})
    print(f"\nRisk Factor Analysis:")
    print(f"  High Risk Factors: {len(risk_analysis.get('high_risk_factors', []))} identified")
    print(f"  Medium Risk Factors: {len(risk_analysis.get('medium_risk_factors', []))} identified")
    print(f"  Risk Interactions: {len(risk_analysis.get('risk_interactions', []))} identified")

    # Overall test result
    test_passed = all_expected_present and no_unexpected_present

    print("\n" + "="*80)
    if test_passed:
        print("✅ TEST PASSED: Step 4 is properly streamlined")
        print("\nStep 4 correctly focuses on:")
        print("  - Risk rating determination (Low/Medium/High/Critical)")
        print("  - Risk score calculation (quantitative + qualitative + amplification)")
        print("  - Risk factor analysis (what makes this model risky)")
        print("\nGovernance and compliance elements are properly deferred to Step 5:")
        print("  - governance_structure → Step 5")
        print("  - review_frequency → Step 5")
        print("  - approval_authority → Step 5")
        print("  - monitoring_framework → Step 5")
    else:
        print("❌ TEST FAILED: Step 4 has issues")
        if not all_expected_present:
            print("  Missing expected risk rating keys")
        if not no_unexpected_present:
            print("  Contains governance/compliance keys that belong in Step 5")

    return test_passed


def test_step5_still_has_governance():
    """Verify that Step 5 still contains governance and compliance elements."""
    print("\n" + "="*80)
    print("TEST: Step 5 (create_compliance_framework) Still Has Governance Elements")
    print("="*80)

    processor = OSFIE23Processor()

    project_description = """
    Our bank is developing a credit risk scoring model for retail lending.
    The model uses machine learning to predict default probability.
    """

    result = processor.create_compliance_framework(
        project_name="Credit Risk Scoring Model",
        project_description=project_description,
        current_stage="design"
    )

    print("\nStep 5 Output Keys:")
    for key in result.keys():
        print(f"  - {key}")

    # Expected keys in Step 5
    expected_keys = [
        "governance_structure",
        "monitoring_framework",
        "documentation_requirements"
    ]

    print("\n" + "-"*80)
    print("Checking Expected Governance/Compliance Keys:")
    print("-"*80)

    all_present = True
    for key in expected_keys:
        present = key in result
        status = "✅ PASS" if present else "❌ FAIL"
        print(f"{status}: {key}")
        all_present = all_present and present

    if all_present:
        print("\n✅ TEST PASSED: Step 5 still contains governance and compliance framework")
    else:
        print("\n❌ TEST FAILED: Step 5 missing governance/compliance elements")

    return all_present


def run_all_tests():
    """Run all Step 4 streamlining tests."""
    print("\n" + "="*80)
    print("STEP 4 STREAMLINING TEST SUITE")
    print("="*80)
    print("\nVerifying Step 4 focuses on risk rating, Step 5 handles governance/compliance")

    results = []
    results.append(("Step 4 Returns Only Risk Rating", test_step4_returns_only_risk_rating()))
    results.append(("Step 5 Still Has Governance Elements", test_step5_still_has_governance()))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Step 4 is properly streamlined.")
        print("\nWhat this means:")
        print("  1. Step 4 (generate_risk_rating) focuses purely on risk assessment")
        print("  2. No governance or compliance elements in Step 4 output")
        print("  3. Step 5 (create_compliance_framework) still contains governance elements")
        print("  4. Clear separation of concerns: risk rating vs compliance framework")
        return True
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED - Review output above for details")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
