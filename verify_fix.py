#!/usr/bin/env python3
"""
Quick verification script to demonstrate the validation enforcement fix.
Run this to see the before/after behavior.
"""

from description_validator import ProjectDescriptionValidator
from workflow_engine import WorkflowEngine, AssessmentType

def demonstrate_fix():
    """Demonstrate the validation enforcement fix."""
    print("="*80)
    print("VALIDATION ENFORCEMENT FIX - DEMONSTRATION")
    print("="*80)

    # Create validator
    validator = ProjectDescriptionValidator()

    # Test with insufficient description (the problematic scenario)
    insufficient_description = """
    AI credit risk model for banking using machine learning algorithms
    to process customer data and make loan approval decisions automatically.
    """

    print("\n📝 Testing with INSUFFICIENT description:")
    print(f"Description: {insufficient_description.strip()}")
    print(f"Length: {len(insufficient_description.split())} words")

    result = validator.validate_description(insufficient_description)

    print(f"\n📊 VALIDATION RESULTS:")
    print(f"  is_valid: {result['is_valid']}")
    print(f"  total_words: {result['total_words']} (minimum: 100)")
    print(f"  areas_covered: {result['areas_covered']} (minimum: 3)")
    print(f"\n🎯 FRAMEWORK READINESS:")
    print(f"  aia_framework: {result['framework_readiness']['aia_framework']}")
    print(f"  osfi_e23_framework: {result['framework_readiness']['osfi_e23_framework']}")
    print(f"  combined_readiness: {result['framework_readiness']['combined_readiness']}")

    # Check for consistency
    is_consistent = (
        result['is_valid'] == result['framework_readiness']['aia_framework'] and
        result['is_valid'] == result['framework_readiness']['osfi_e23_framework'] and
        result['is_valid'] == result['framework_readiness']['combined_readiness']
    )

    if is_consistent:
        print(f"\n✅ CONSISTENCY CHECK: PASSED")
        print("   All framework flags match is_valid status")
    else:
        print(f"\n❌ CONSISTENCY CHECK: FAILED")
        print("   Framework flags contradict is_valid status")

    # Test workflow blocking
    print("\n" + "="*80)
    print("WORKFLOW EXECUTION BLOCKING TEST")
    print("="*80)

    engine = WorkflowEngine()
    session_id = engine.create_session(
        project_name="Test Credit Risk Model",
        project_description=insufficient_description,
        assessment_type=AssessmentType.OSFI_E23.value
    )

    print(f"\n✅ Created workflow session: {session_id[:8]}...")

    # Simulate validation
    validation_result = {
        "validation": {
            "is_valid": result['is_valid'],
            "validation_message": result['validation_message'],
            "framework_readiness": result['framework_readiness']
        }
    }

    engine.execute_tool(session_id, "validate_project_description", validation_result)
    print(f"✅ Executed validate_project_description")

    # Try to execute assessment tool
    session = engine.get_session(session_id)
    dependency_check = engine._validate_dependencies(session, "assess_model_risk")

    print(f"\n🔍 Attempting to execute 'assess_model_risk':")
    print(f"  Can execute: {dependency_check['valid']}")

    if not dependency_check['valid']:
        print(f"  ❌ BLOCKED: {dependency_check['reason']}")
        print(f"  Recommended action: {dependency_check['recommended_action']}")
        print(f"\n✅ FIX WORKING: Assessment tools are properly blocked when validation fails")
    else:
        print(f"  ⚠️  WARNING: Assessment tool was allowed to execute despite validation failure!")
        print(f"  ❌ FIX NOT WORKING: Validation enforcement is not blocking execution")

    # Test auto-execution blocking
    can_auto = engine._can_auto_execute(session)
    print(f"\n🔍 Checking auto-execution capability:")
    print(f"  Can auto-execute: {can_auto}")

    if not can_auto:
        print(f"  ✅ FIX WORKING: Auto-execution properly blocked when validation fails")
    else:
        print(f"  ❌ FIX NOT WORKING: Auto-execution allowed despite validation failure")

    # Summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)

    all_checks_passed = (
        is_consistent and
        not dependency_check['valid'] and
        not can_auto
    )

    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Validation enforcement fix is working correctly!")
        print("\nWhat this means:")
        print("  1. Framework readiness flags are consistent with is_valid")
        print("  2. Assessment tools are blocked when validation fails")
        print("  3. Auto-execution is blocked when validation fails")
        print("  4. Clear error messages guide users to fix descriptions")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Please review the output above")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(demonstrate_fix())
