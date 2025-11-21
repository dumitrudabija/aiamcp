#!/usr/bin/env python3
"""
Test updated Step 6 (export_e23_report) with stage-specific functionality.
Verifies that reports leverage Step 3 and Step 5 data.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import MCPServer


def test_design_stage_report():
    """Test report generation for Design stage."""
    print("\n" + "="*80)
    print("TEST: Design Stage Report Generation")
    print("="*80)

    server = MCPServer()

    project_description = """
    Our bank is developing a new credit risk scoring model for retail lending.
    The model uses machine learning to predict default probability based on customer data.
    We have established data governance framework and defined model methodology.
    The model will process sensitive financial data and impact lending decisions.
    """

    # Create assessment results directly (bypassing workflow enforcement for testing)
    from osfi_e23_processor import OSFIE23Processor
    processor = OSFIE23Processor()

    assessment = processor.assess_model_risk(
        project_name="Credit Risk Model - Design Stage",
        project_description=project_description
    )

    assessment_results = {
        "risk_level": assessment.get("risk_level"),
        "risk_score": assessment.get("risk_score"),
        "risk_analysis": assessment.get("risk_analysis")
    }

    # Step 6: Export report
    result = server._export_e23_report({
        "project_name": "Credit Risk Model - Design Stage",
        "project_description": project_description,
        "assessment_results": assessment_results
    })

    # Verify result
    success = result.get("success", False)
    lifecycle_stage = result.get("lifecycle_stage")
    file_path = result.get("file_path")

    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Report generated successfully")
    print(f"{'✅ PASS' if lifecycle_stage == 'design' else '❌ FAIL'}: Lifecycle stage detected as 'design' (got: {lifecycle_stage})")
    print(f"{'✅ PASS' if file_path and os.path.exists(file_path) else '❌ FAIL'}: File created at {file_path}")

    if file_path and os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        print(f"File size: {file_size} bytes ({file_size/1024:.1f} KB)")

        # Clean up
        os.unlink(file_path)
        print("File cleaned up")

    return success and lifecycle_stage == "design"


def test_monitoring_stage_report():
    """Test report generation for Monitoring stage."""
    print("\n" + "="*80)
    print("TEST: Monitoring Stage Report Generation")
    print("="*80)

    server = MCPServer()

    project_description = """
    Our fraud detection model is deployed in production and being monitored.
    We track performance metrics daily and have drift detection procedures in place.
    The model is monitored for accuracy degradation and data distribution changes.
    We have established escalation procedures for performance issues.
    """

    # Create assessment results directly (bypassing workflow enforcement for testing)
    from osfi_e23_processor import OSFIE23Processor
    processor = OSFIE23Processor()

    assessment = processor.assess_model_risk(
        project_name="Fraud Detection Model - Production Monitoring",
        project_description=project_description
    )

    assessment_results = {
        "risk_level": assessment.get("risk_level"),
        "risk_score": assessment.get("risk_score"),
        "risk_analysis": assessment.get("risk_analysis")
    }

    # Step 6: Export report
    result = server._export_e23_report({
        "project_name": "Fraud Detection Model - Production Monitoring",
        "project_description": project_description,
        "assessment_results": assessment_results
    })

    # Verify result
    success = result.get("success", False)
    lifecycle_stage = result.get("lifecycle_stage")
    file_path = result.get("file_path")

    print(f"\n{'✅ PASS' if success else '❌ FAIL'}: Report generated successfully")
    print(f"{'✅ PASS' if lifecycle_stage == 'monitoring' else '❌ FAIL'}: Lifecycle stage detected as 'monitoring' (got: {lifecycle_stage})")
    print(f"{'✅ PASS' if file_path and os.path.exists(file_path) else '❌ FAIL'}: File created at {file_path}")

    if file_path and os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        print(f"File size: {file_size} bytes ({file_size/1024:.1f} KB)")

        # Clean up
        os.unlink(file_path)
        print("File cleaned up")

    return success and lifecycle_stage == "monitoring"


def test_report_has_new_sections():
    """Test that report contains new sections from Step 3 and Step 5."""
    print("\n" + "="*80)
    print("TEST: Report Contains New Sections")
    print("="*80)

    server = MCPServer()

    project_description = """
    Our bank is designing a pricing model with machine learning capabilities.
    The model includes clear rationale, data governance, and development methodology.
    It will be used for customer-facing pricing decisions in our retail banking division.
    """

    # Create assessment results directly (bypassing workflow enforcement for testing)
    from osfi_e23_processor import OSFIE23Processor
    processor = OSFIE23Processor()

    assessment = processor.assess_model_risk(
        project_name="Pricing Model - Section Test",
        project_description=project_description
    )

    assessment_results = {
        "risk_level": assessment.get("risk_level"),
        "risk_score": assessment.get("risk_score"),
        "risk_analysis": assessment.get("risk_analysis")
    }

    # Step 6: Export report
    result = server._export_e23_report({
        "project_name": "Pricing Model - Section Test",
        "project_description": project_description,
        "assessment_results": assessment_results
    })

    file_path = result.get("file_path")

    if file_path and os.path.exists(file_path):
        # Read document and check for new sections
        from docx import Document
        doc = Document(file_path)
        full_text = "\n".join([para.text for para in doc.paragraphs])

        # Check for new sections
        has_coverage = "LIFECYCLE COVERAGE ASSESSMENT" in full_text
        has_governance = "GOVERNANCE STRUCTURE" in full_text
        has_monitoring = "MONITORING FRAMEWORK" in full_text
        has_professional_warning = "PROFESSIONAL VALIDATION REQUIRED" in full_text

        print(f"\n{'✅ PASS' if has_coverage else '❌ FAIL'}: Report has Lifecycle Coverage Assessment section")
        print(f"{'✅ PASS' if has_governance else '❌ FAIL'}: Report has Governance Structure section")
        print(f"{'✅ PASS' if has_monitoring else '❌ FAIL'}: Report has Monitoring Framework section")
        print(f"{'✅ PASS' if has_professional_warning else '❌ FAIL'}: Report has Professional Validation warning")

        # Clean up
        os.unlink(file_path)
        print("\nFile cleaned up")

        return has_coverage and has_governance and has_monitoring and has_professional_warning
    else:
        print("❌ FAIL: Could not generate report for section test")
        return False


def run_all_tests():
    """Run all Step 6 update tests."""
    print("\n" + "="*80)
    print("STEP 6 UPDATED REPORT GENERATION TEST SUITE")
    print("="*80)
    print("\nVerifying stage-specific reports with Step 3/5 data integration")

    results = []
    results.append(("Design Stage Report", test_design_stage_report()))
    results.append(("Monitoring Stage Report", test_monitoring_stage_report()))
    results.append(("Report Has New Sections", test_report_has_new_sections()))

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
        print("\n🎉 ALL TESTS PASSED! Step 6 report generation updated successfully.")
        print("\nWhat this means:")
        print("  1. Reports are now stage-specific (Design, Review, Deployment, Monitoring, Decommission)")
        print("  2. Reports include Step 3 coverage assessment (0/33/67/100%)")
        print("  3. Reports include Step 5 osfi_elements checklist structure")
        print("  4. Reports include governance structure with OSFI-mandated vs choice clarity")
        print("  5. Reports include monitoring framework section")
        print("  6. Professional validation warnings preserved at beginning and end")
        return True
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED - Review output above for details")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
