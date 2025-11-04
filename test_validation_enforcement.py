#!/usr/bin/env python3
"""
Comprehensive test suite for validation enforcement fix.

Tests that validation failures properly block workflow execution and
that framework_readiness flags are consistent with is_valid status.
"""

import json
import sys
from description_validator import ProjectDescriptionValidator
from workflow_engine import WorkflowEngine, AssessmentType


def test_validation_consistency():
    """Test that framework_readiness flags are consistent with is_valid."""
    print("\n" + "="*80)
    print("TEST 1: Validation Consistency")
    print("="*80)

    validator = ProjectDescriptionValidator()

    # Test Case 1a: Insufficient description (too few words, but 3+ areas covered)
    insufficient_description = """
    This is an AI system for credit risk assessment. It uses machine learning
    algorithms to process financial data and customer information. The system
    makes automated decisions about loan approvals.
    """

    result = validator.validate_description(insufficient_description)

    print(f"\nTest Case 1a: Insufficient description (too few words)")
    print(f"Word count: {result['total_words']} (minimum: 100)")
    print(f"Areas covered: {result['areas_covered']} (minimum: 3)")
    print(f"is_valid: {result['is_valid']}")
    print(f"aia_framework: {result['framework_readiness']['aia_framework']}")
    print(f"osfi_e23_framework: {result['framework_readiness']['osfi_e23_framework']}")
    print(f"combined_readiness: {result['framework_readiness']['combined_readiness']}")

    # Verify fix: ALL flags should be False when is_valid is False
    assert result['is_valid'] == False, "Expected is_valid to be False"
    assert result['framework_readiness']['aia_framework'] == False, \
        "CRITICAL BUG: aia_framework should be False when is_valid is False"
    assert result['framework_readiness']['osfi_e23_framework'] == False, \
        "CRITICAL BUG: osfi_e23_framework should be False when is_valid is False"
    assert result['framework_readiness']['combined_readiness'] == False, \
        "Expected combined_readiness to be False when is_valid is False"

    print("✅ PASS: All framework flags correctly set to False when validation fails")

    # Test Case 1b: Valid description
    valid_description = """
    This is a comprehensive AI-powered credit risk assessment system designed for
    financial institutions. The system uses advanced machine learning algorithms
    including gradient boosting and neural networks to analyze applicant data.

    Business Purpose: The system evaluates loan applications and provides risk
    scores to support credit decisions. It aims to improve approval accuracy and
    reduce default rates while ensuring fair lending practices.

    Data Sources: The system processes applicant financial history, credit bureau
    reports, transaction records, employment verification data, and demographic
    information. All data is stored in encrypted databases with access controls.

    Impact Scope: The system affects loan applicants by influencing approval
    decisions. It has financial impacts on both customers and the institution.
    Risk includes potential bias in lending decisions and financial harm from
    incorrect predictions.

    Decision Process: The system generates risk scores from 0-1000. Scores above
    700 receive automatic preliminary approval. Scores 400-699 require manual
    review. Below 400 are flagged for decline with human review required.

    Technical Architecture: The system uses a microservices architecture deployed
    on AWS cloud infrastructure. It integrates with core banking systems via REST
    APIs and includes real-time monitoring dashboards for model performance.
    """

    result = validator.validate_description(valid_description)

    print(f"\nTest Case 1b: Valid description")
    print(f"Word count: {result['total_words']} (minimum: 100)")
    print(f"Areas covered: {result['areas_covered']} (minimum: 3)")
    print(f"is_valid: {result['is_valid']}")
    print(f"aia_framework: {result['framework_readiness']['aia_framework']}")
    print(f"osfi_e23_framework: {result['framework_readiness']['osfi_e23_framework']}")
    print(f"combined_readiness: {result['framework_readiness']['combined_readiness']}")

    # Verify: ALL flags should be True when is_valid is True
    assert result['is_valid'] == True, "Expected is_valid to be True"
    assert result['framework_readiness']['aia_framework'] == True, \
        "Expected aia_framework to be True when validation passes"
    assert result['framework_readiness']['osfi_e23_framework'] == True, \
        "Expected osfi_e23_framework to be True when validation passes"
    assert result['framework_readiness']['combined_readiness'] == True, \
        "Expected combined_readiness to be True when validation passes"

    print("✅ PASS: All framework flags correctly set to True when validation passes")

    return True


def test_workflow_blocking():
    """Test that workflow execution is blocked when validation fails."""
    print("\n" + "="*80)
    print("TEST 2: Workflow Execution Blocking")
    print("="*80)

    engine = WorkflowEngine()

    # Create workflow with insufficient description
    insufficient_description = """
    AI credit risk system for loan decisions using machine learning.
    """

    session_id = engine.create_session(
        project_name="Test Credit System",
        project_description=insufficient_description,
        assessment_type=AssessmentType.OSFI_E23.value
    )

    print(f"\nCreated workflow session: {session_id}")

    # Simulate validation tool execution with FAILED result
    validation_result = {
        "validation": {
            "is_valid": False,
            "validation_message": "❌ Insufficient project description",
            "framework_readiness": {
                "aia_framework": False,
                "osfi_e23_framework": False,
                "combined_readiness": False
            }
        }
    }

    workflow_status = engine.execute_tool(
        session_id=session_id,
        tool_name="validate_project_description",
        tool_result=validation_result
    )

    print(f"\nValidation completed with result: {validation_result['validation']['is_valid']}")
    print(f"Workflow state: {workflow_status['workflow_status']['current_state']}")

    # Test Case 2a: Try to execute assess_model_risk after validation failure
    print(f"\nTest Case 2a: Attempting to execute assess_model_risk after validation failure")

    session = engine.get_session(session_id)
    dependency_check = engine._validate_dependencies(session, "assess_model_risk")

    print(f"Dependency validation result: {dependency_check}")

    assert dependency_check['valid'] == False, \
        "CRITICAL BUG: assess_model_risk should be blocked when validation fails"
    assert "validation failed" in dependency_check['reason'].lower(), \
        "Error message should mention validation failure"

    print("✅ PASS: assess_model_risk correctly blocked after validation failure")

    # Test Case 2b: Try to execute functional_preview after validation failure
    print(f"\nTest Case 2b: Attempting to execute functional_preview after validation failure")

    dependency_check = engine._validate_dependencies(session, "functional_preview")

    print(f"Dependency validation result: {dependency_check}")

    assert dependency_check['valid'] == False, \
        "CRITICAL BUG: functional_preview should be blocked when validation fails"

    print("✅ PASS: functional_preview correctly blocked after validation failure")

    # Test Case 2c: Try auto-execution after validation failure
    print(f"\nTest Case 2c: Attempting auto-execution after validation failure")

    can_auto = engine._can_auto_execute(session)
    print(f"Can auto-execute: {can_auto}")

    assert can_auto == False, \
        "CRITICAL BUG: Auto-execution should be blocked when validation fails"

    print("✅ PASS: Auto-execution correctly blocked after validation failure")

    return True


def test_workflow_allows_valid_execution():
    """Test that workflow proceeds normally when validation passes."""
    print("\n" + "="*80)
    print("TEST 3: Workflow Execution Allowed After Successful Validation")
    print("="*80)

    engine = WorkflowEngine()

    # Create workflow with valid description
    valid_description = """
    This is a comprehensive AI-powered credit risk assessment system designed for
    financial institutions. The system uses advanced machine learning algorithms
    including gradient boosting and neural networks to analyze applicant data.

    Business Purpose: The system evaluates loan applications and provides risk
    scores to support credit decisions. It aims to improve approval accuracy and
    reduce default rates while ensuring fair lending practices.

    Data Sources: The system processes applicant financial history, credit bureau
    reports, transaction records, employment verification data, and demographic
    information. All data is stored in encrypted databases with access controls.

    Impact Scope: The system affects loan applicants by influencing approval
    decisions. It has financial impacts on both customers and the institution.
    Risk includes potential bias in lending decisions and financial harm from
    incorrect predictions.

    Decision Process: The system generates risk scores from 0-1000. Scores above
    700 receive automatic preliminary approval. Scores 400-699 require manual
    review. Below 400 are flagged for decline with human review required.

    Technical Architecture: The system uses a microservices architecture deployed
    on AWS cloud infrastructure. It integrates with core banking systems via REST
    APIs and includes real-time monitoring dashboards for model performance.
    """

    session_id = engine.create_session(
        project_name="Test Credit System Valid",
        project_description=valid_description,
        assessment_type=AssessmentType.OSFI_E23.value
    )

    print(f"\nCreated workflow session: {session_id}")

    # Simulate validation tool execution with SUCCESS result
    validation_result = {
        "validation": {
            "is_valid": True,
            "validation_message": "✅ Project description is adequate",
            "framework_readiness": {
                "aia_framework": True,
                "osfi_e23_framework": True,
                "combined_readiness": True
            }
        }
    }

    workflow_status = engine.execute_tool(
        session_id=session_id,
        tool_name="validate_project_description",
        tool_result=validation_result
    )

    print(f"\nValidation completed with result: {validation_result['validation']['is_valid']}")
    print(f"Workflow state: {workflow_status['workflow_status']['current_state']}")

    # Test Case 3a: Try to execute assess_model_risk after validation success
    print(f"\nTest Case 3a: Attempting to execute assess_model_risk after validation success")

    session = engine.get_session(session_id)
    dependency_check = engine._validate_dependencies(session, "assess_model_risk")

    print(f"Dependency validation result: {dependency_check}")

    assert dependency_check['valid'] == True, \
        "BUG: assess_model_risk should be allowed when validation passes"

    print("✅ PASS: assess_model_risk correctly allowed after validation success")

    # Test Case 3b: Verify auto-execution is allowed
    print(f"\nTest Case 3b: Checking auto-execution after validation success")

    can_auto = engine._can_auto_execute(session)
    print(f"Can auto-execute: {can_auto}")

    assert can_auto == True, \
        "BUG: Auto-execution should be allowed when validation passes"

    print("✅ PASS: Auto-execution correctly allowed after validation success")

    return True


def test_validation_state_helper():
    """Test the _check_validation_state helper method."""
    print("\n" + "="*80)
    print("TEST 4: Validation State Helper Method")
    print("="*80)

    engine = WorkflowEngine()

    # Test Case 4a: Validation not completed
    session_id = engine.create_session(
        project_name="Test",
        project_description="test description",
        assessment_type=AssessmentType.OSFI_E23.value
    )
    session = engine.get_session(session_id)

    validation_state = engine._check_validation_state(session)
    print(f"\nTest Case 4a: Validation state when not completed")
    print(f"Result: {validation_state}")

    assert validation_state['completed'] == False, \
        "Expected completed to be False when validation not run"
    assert validation_state['passed'] == False, \
        "Expected passed to be False when validation not run"

    print("✅ PASS: Validation state correctly reports not completed")

    # Test Case 4b: Validation completed and failed
    validation_result = {
        "validation": {
            "is_valid": False,
            "validation_message": "❌ Insufficient",
            "framework_readiness": {
                "aia_framework": False,
                "osfi_e23_framework": False,
                "combined_readiness": False
            }
        }
    }

    engine.execute_tool(session_id, "validate_project_description", validation_result)
    session = engine.get_session(session_id)

    validation_state = engine._check_validation_state(session)
    print(f"\nTest Case 4b: Validation state when completed but failed")
    print(f"Result: {validation_state}")

    assert validation_state['completed'] == True, \
        "Expected completed to be True when validation run"
    assert validation_state['passed'] == False, \
        "Expected passed to be False when validation failed"

    print("✅ PASS: Validation state correctly reports failed validation")

    # Test Case 4c: Validation completed and passed
    session_id2 = engine.create_session(
        project_name="Test2",
        project_description="test description",
        assessment_type=AssessmentType.OSFI_E23.value
    )

    validation_result_success = {
        "validation": {
            "is_valid": True,
            "validation_message": "✅ Valid",
            "framework_readiness": {
                "aia_framework": True,
                "osfi_e23_framework": True,
                "combined_readiness": True
            }
        }
    }

    engine.execute_tool(session_id2, "validate_project_description", validation_result_success)
    session2 = engine.get_session(session_id2)

    validation_state = engine._check_validation_state(session2)
    print(f"\nTest Case 4c: Validation state when completed and passed")
    print(f"Result: {validation_state}")

    assert validation_state['completed'] == True, \
        "Expected completed to be True when validation run"
    assert validation_state['passed'] == True, \
        "Expected passed to be True when validation succeeded"

    print("✅ PASS: Validation state correctly reports successful validation")

    return True


def main():
    """Run all validation enforcement tests."""
    print("\n" + "="*80)
    print("VALIDATION ENFORCEMENT FIX - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("\nTesting fixes for validation logic contradiction and workflow blocking")

    tests = [
        ("Validation Consistency", test_validation_consistency),
        ("Workflow Blocking", test_workflow_blocking),
        ("Valid Execution Allowed", test_workflow_allows_valid_execution),
        ("Validation State Helper", test_validation_state_helper),
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
        print("\n🎉 ALL TESTS PASSED! Validation enforcement fix is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
