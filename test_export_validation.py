#!/usr/bin/env python3
"""
Test suite for export function validation fix.

Tests that export tools:
1. Reject empty assessment_results with clear error messages
2. Auto-inject results from workflow state when available
3. Reject incomplete assessment data (missing required fields)
4. Accept and export valid assessment data
"""

import sys
import json
from workflow_engine import WorkflowEngine, AssessmentType


def test_export_rejects_empty_results():
    """Test that export_e23_report rejects empty assessment_results."""
    print("\n" + "="*80)
    print("TEST 1: Export Rejects Empty Assessment Results")
    print("="*80)

    # Import server to test export functions
    from server import MCPServer
    server = MCPServer()

    print("\nTest Case 1a: Call export_e23_report with empty assessment_results")

    result = server._export_e23_report({
        "project_name": "Test Credit Model",
        "project_description": "Test description",
        "assessment_results": {}
    })

    print(f"Result keys: {result.keys()}")
    print(f"Error: {result.get('error')}")
    print(f"Reason: {result.get('reason')}")

    assert "error" in result, "Expected error when assessment_results is empty"
    assert result["error"] == "export_failed", "Expected 'export_failed' error"
    assert "empty" in result["reason"].lower() or "missing" in result["reason"].lower(), \
        "Error reason should mention empty/missing data"
    assert "required_action" in result, "Should provide required_action guidance"
    assert "critical_warning" in result, "Should include critical compliance warning"

    print("✅ PASS: Export correctly rejects empty assessment_results")

    print("\nTest Case 1b: Call export_assessment_report with empty assessment_results")

    result = server._export_assessment_report({
        "project_name": "Test AI System",
        "project_description": "Test description",
        "assessment_results": {}
    })

    print(f"Result keys: {result.keys()}")
    print(f"Error: {result.get('error')}")

    assert "error" in result, "Expected error when assessment_results is empty"
    assert result["error"] == "export_failed", "Expected 'export_failed' error"

    print("✅ PASS: AIA export correctly rejects empty assessment_results")

    return True


def test_export_rejects_incomplete_results():
    """Test that exports reject incomplete assessment data."""
    print("\n" + "="*80)
    print("TEST 2: Export Rejects Incomplete Assessment Data")
    print("="*80)

    from server import MCPServer
    server = MCPServer()

    print("\nTest Case 2a: OSFI E-23 export with missing risk_score")

    result = server._export_e23_report({
        "project_name": "Test Model",
        "project_description": "Test description",
        "assessment_results": {
            "risk_level": "High"
            # Missing risk_score
        }
    })

    print(f"Error: {result.get('error')}")
    print(f"Missing fields: {result.get('missing_fields')}")

    assert "error" in result, "Should reject incomplete assessment data"
    assert "missing_fields" in result, "Should specify which fields are missing"
    assert result["missing_fields"]["risk_score_missing"] == True, \
        "Should identify risk_score as missing"

    print("✅ PASS: Correctly rejects OSFI E-23 data missing risk_score")

    print("\nTest Case 2b: OSFI E-23 export with missing risk_level")

    result = server._export_e23_report({
        "project_name": "Test Model",
        "project_description": "Test description",
        "assessment_results": {
            "risk_score": 72
            # Missing risk_level
        }
    })

    print(f"Error: {result.get('error')}")
    print(f"Missing fields: {result.get('missing_fields')}")

    assert "error" in result, "Should reject incomplete assessment data"
    assert result["missing_fields"]["risk_level_missing"] == True, \
        "Should identify risk_level as missing"

    print("✅ PASS: Correctly rejects OSFI E-23 data missing risk_level")

    print("\nTest Case 2c: AIA export with missing score and impact_level")

    result = server._export_assessment_report({
        "project_name": "Test System",
        "project_description": "Test description",
        "assessment_results": {
            "responses": []  # Has responses but no score/impact_level
        }
    })

    print(f"Error: {result.get('error')}")
    print(f"Missing fields: {result.get('missing_fields')}")

    assert "error" in result, "Should reject incomplete AIA data"
    assert "missing_fields" in result, "Should specify which fields are missing"

    print("✅ PASS: Correctly rejects AIA data missing score and impact_level")

    return True


def test_export_accepts_valid_results():
    """Test that exports accept valid complete assessment data."""
    print("\n" + "="*80)
    print("TEST 3: Export Accepts Valid Assessment Data")
    print("="*80)

    from server import MCPServer
    server = MCPServer()

    print("\nTest Case 3a: OSFI E-23 export with complete data")

    result = server._export_e23_report({
        "project_name": "Test Credit Risk Model",
        "project_description": "A comprehensive credit risk model for loan approvals",
        "assessment_results": {
            "risk_score": 72,
            "risk_level": "High",
            "quantitative_factors": {"complexity": "High"},
            "qualitative_factors": {"materiality": "Significant"}
        }
    })

    print(f"Result keys: {result.keys()}")
    print(f"Has error: {'error' in result}")
    print(f"Has file_path: {'file_path' in result}")

    assert "error" not in result, f"Should not error with valid data. Got: {result.get('error')}"
    assert "file_path" in result, "Should return file_path on successful export"

    print(f"✅ PASS: Successfully exported with file: {result.get('file_path')}")

    print("\nTest Case 3b: AIA export with complete data (assess_project format)")

    result = server._export_assessment_report({
        "project_name": "Test AI Decision System",
        "project_description": "AI system for automated decisions",
        "assessment_results": {
            "score": 45,
            "impact_level": "Level III",
            "responses": []
        }
    })

    print(f"Result keys: {result.keys()}")
    print(f"Has error: {'error' in result}")

    assert "error" not in result, f"Should not error with valid AIA data. Got: {result.get('error')}"
    assert "file_path" in result, "Should return file_path on successful export"

    print(f"✅ PASS: Successfully exported AIA report")

    print("\nTest Case 3c: AIA export with functional_preview data")

    result = server._export_assessment_report({
        "project_name": "Test AI System",
        "project_description": "AI system for automated decisions",
        "assessment_results": {
            "functional_risk_score": 38,
            "impact_level": "Level II",
            "assessment_type": "functional_preview"
        }
    })

    print(f"Has error: {'error' in result}")

    assert "error" not in result, f"Should accept functional_preview data. Got: {result.get('error')}"

    print(f"✅ PASS: Successfully exported with functional_preview data")

    return True


def test_workflow_auto_injection():
    """Test that workflow automatically injects assessment results."""
    print("\n" + "="*80)
    print("TEST 4: Workflow Auto-Injection of Assessment Results")
    print("="*80)

    from server import MCPServer
    server = MCPServer()

    print("\nTest Case 4a: Create workflow and complete OSFI E-23 assessment")

    # Create workflow
    create_result = server._create_workflow({
        "projectName": "Test Credit Model",
        "projectDescription": "Credit risk model for loan decisions using machine learning algorithms. Business purpose: evaluate loan applications. Data sources: credit bureau reports, financial data. Impact: affects loan approvals. Decision process: automated scoring with manual review. Technical: ML model deployed on cloud infrastructure.",
        "assessmentType": "osfi_e23"
    })

    session_id = create_result["workflow_created"]["session_id"]
    print(f"Created workflow session: {session_id[:8]}...")

    # Simulate completing validation step
    validation_result = {
        "validation": {
            "is_valid": True,
            "validation_message": "✅ Valid",
            "framework_readiness": {
                "osfi_e23_framework": True
            }
        }
    }

    server.workflow_engine.execute_tool(session_id, "validate_project_description", validation_result)
    print("✅ Completed validation step")

    # Simulate completing assess_model_risk step
    assessment_data = {
        "assessment": {
            "risk_score": 72,
            "risk_level": "High",
            "quantitative_factors": {"complexity": "High", "materiality": "Significant"},
            "qualitative_factors": {"governance": "Adequate"},
            "risk_amplification": {"amplified": True, "multiplier": 1.2}
        }
    }

    server.workflow_engine.execute_tool(session_id, "assess_model_risk", assessment_data)
    print("✅ Completed assess_model_risk step")

    print("\nTest Case 4b: Call export with EMPTY assessment_results via workflow")

    # Call export through workflow with empty assessment_results
    # The workflow should auto-inject the assessment data
    result = server._execute_workflow_step({
        "sessionId": session_id,
        "toolName": "export_e23_report",
        "toolArguments": {
            "project_name": "Test Credit Model",
            "project_description": "Test description",
            "assessment_results": {}  # Empty - should be auto-injected
        }
    })

    print(f"Tool result keys: {result.get('tool_result', {}).keys()}")
    has_error = "error" in result.get('tool_result', {})
    print(f"Has error: {has_error}")

    if has_error:
        print(f"Error: {result['tool_result'].get('error')}")
        print(f"Reason: {result['tool_result'].get('reason')}")

    assert not has_error, \
        "Workflow should auto-inject assessment results, preventing export failure"
    assert "file_path" in result.get('tool_result', {}), \
        "Export should succeed when workflow auto-injects results"

    print("✅ PASS: Workflow successfully auto-injected assessment results")
    print(f"   Exported to: {result['tool_result'].get('file_path')}")

    return True


def test_direct_export_without_workflow():
    """Test that direct export calls (outside workflow) are properly validated."""
    print("\n" + "="*80)
    print("TEST 5: Direct Export Calls Without Workflow")
    print("="*80)

    from server import MCPServer
    server = MCPServer()

    print("\nTest Case 5a: Direct export_e23_report call with empty data (no workflow)")

    # Call export directly (not through workflow) with empty data
    # This should fail with validation error
    result = server._export_e23_report({
        "project_name": "Direct Test",
        "project_description": "Test",
        "assessment_results": {}
    })

    print(f"Has error: {'error' in result}")
    print(f"Error: {result.get('error')}")

    assert "error" in result, \
        "Direct export call without workflow should reject empty assessment_results"
    assert result["error"] == "export_failed", \
        "Should return export_failed error"

    print("✅ PASS: Direct export correctly rejected empty data")

    print("\nTest Case 5b: Direct export with valid data (no workflow) should succeed")

    result = server._export_e23_report({
        "project_name": "Direct Test Valid",
        "project_description": "Test description",
        "assessment_results": {
            "risk_score": 65,
            "risk_level": "High"
        }
    })

    print(f"Has error: {'error' in result}")

    assert "error" not in result, \
        "Direct export with valid data should succeed"

    print("✅ PASS: Direct export succeeded with valid data")

    return True


def main():
    """Run all export validation tests."""
    print("\n" + "="*80)
    print("EXPORT VALIDATION FIX - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("\nTesting fixes for:")
    print("- Empty assessment_results rejection")
    print("- Incomplete assessment data validation")
    print("- Workflow auto-injection")
    print("- Direct export validation")

    tests = [
        ("Export Rejects Empty Results", test_export_rejects_empty_results),
        ("Export Rejects Incomplete Results", test_export_rejects_incomplete_results),
        ("Export Accepts Valid Results", test_export_accepts_valid_results),
        ("Workflow Auto-Injection", test_workflow_auto_injection),
        ("Direct Export Without Workflow", test_direct_export_without_workflow),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAIL: {test_name}")
            print(f"   Error: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR: {test_name}")
            print(f"   Exception: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Export validation fix is working correctly.")
        print("\nWhat this means:")
        print("  1. Export tools reject empty assessment_results")
        print("  2. Export tools validate required risk assessment fields")
        print("  3. Workflow auto-injects assessment results when available")
        print("  4. Direct exports are properly validated")
        print("  5. No more misleading reports with default values (0/100, Medium)")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
