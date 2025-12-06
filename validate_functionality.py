#!/usr/bin/env python3
"""
Comprehensive Functionality Validation Script

This script validates that all core functionality works correctly.
Run this after every refactoring change to ensure no regressions.

Usage:
    python validate_functionality.py

Exit codes:
    0 - All validations passed
    1 - One or more validations failed
"""

import sys
import os
from typing import Dict, Any, List, Tuple

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")

def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} | {test_name}")
    if details:
        print(f"   {details}")

def validate_imports() -> Tuple[bool, List[str]]:
    """Validate that all core modules can be imported."""
    print_section("VALIDATION 1: Module Imports")

    modules_to_test = [
        "server",
        "aia_processor",
        "osfi_e23_processor",
        "osfi_e23_structure",
        "osfi_e23_report_generators",
        "workflow_engine",
        "description_validator",
    ]

    errors = []
    all_passed = True

    for module_name in modules_to_test:
        try:
            __import__(module_name)
            print_result(f"Import {module_name}", True)
        except Exception as e:
            print_result(f"Import {module_name}", False, str(e))
            errors.append(f"Failed to import {module_name}: {str(e)}")
            all_passed = False

    return all_passed, errors

def validate_server_initialization() -> Tuple[bool, List[str]]:
    """Validate that MCPServer can be initialized."""
    print_section("VALIDATION 2: Server Initialization")

    errors = []
    try:
        from server import MCPServer
        server = MCPServer()
        print_result("MCPServer instantiation", True)

        # Check key attributes exist
        required_attrs = [
            'aia_processor',
            'osfi_e23_processor',
            'workflow_engine',
            'description_validator'
        ]

        for attr in required_attrs:
            if hasattr(server, attr):
                print_result(f"Server has attribute '{attr}'", True)
            else:
                print_result(f"Server has attribute '{attr}'", False)
                errors.append(f"Missing attribute: {attr}")

        return len(errors) == 0, errors

    except Exception as e:
        print_result("MCPServer instantiation", False, str(e))
        return False, [f"Failed to initialize server: {str(e)}"]

def validate_framework_detection() -> Tuple[bool, List[str]]:
    """Validate framework detection logic."""
    print_section("VALIDATION 3: Framework Detection")

    errors = []
    try:
        from server import MCPServer
        server = MCPServer()

        test_cases = [
            ("Run through OSFI for my credit model", "osfi_e23", "OSFI detection"),
            ("I need an AIA assessment", "aia", "AIA detection"),
            ("Help assess my AI system", "both", "Unclear context defaults to both"),
        ]

        all_passed = True
        for context, expected, description in test_cases:
            result = server._detect_framework_context(context)
            passed = result == expected
            print_result(description, passed, f"Expected: {expected}, Got: {result}")
            if not passed:
                errors.append(f"{description} failed: expected {expected}, got {result}")
                all_passed = False

        return all_passed, errors

    except Exception as e:
        print_result("Framework detection", False, str(e))
        return False, [f"Framework detection failed: {str(e)}"]

def validate_tool_registration() -> Tuple[bool, List[str]]:
    """Validate that all expected tools are registered."""
    print_section("VALIDATION 4: Tool Registration")

    errors = []
    try:
        from server import MCPServer
        server = MCPServer()

        # Get tool list
        result = server._list_tools(1)
        tools = result.get("result", {}).get("tools", [])

        # v3.0: OSFI E-23 simplified to 3 steps:
        # (1) validate_project_description
        # (2) assess_model_risk (with extraction-based scoring)
        # (3) export_e23_report
        # Removed: evaluate_lifecycle_compliance, generate_risk_rating, create_compliance_framework
        expected_tools = [
            "get_server_introduction",
            "validate_project_description",
            "create_workflow",
            "execute_workflow_step",
            "get_workflow_status",
            "auto_execute_workflow",
            "analyze_project_description",
            "get_questions",
            "assess_project",
            "functional_preview",
            "export_assessment_report",
            "assess_model_risk",
            "export_e23_report",
        ]

        tool_names = [t["name"] for t in tools]

        print_result("Tool list retrieved", True, f"Found {len(tool_names)} tools")

        all_passed = True
        for expected_tool in expected_tools:
            if expected_tool in tool_names:
                print_result(f"Tool '{expected_tool}' registered", True)
            else:
                print_result(f"Tool '{expected_tool}' registered", False)
                errors.append(f"Missing tool: {expected_tool}")
                all_passed = False

        return all_passed, errors

    except Exception as e:
        print_result("Tool registration", False, str(e))
        return False, [f"Tool registration failed: {str(e)}"]

def validate_aia_processor() -> Tuple[bool, List[str]]:
    """Validate basic AIA processor functionality."""
    print_section("VALIDATION 5: AIA Processor")

    errors = []
    try:
        from aia_processor import AIAProcessor

        processor = AIAProcessor()
        print_result("AIAProcessor instantiation", True)

        # Check questions are loaded (scorable_questions is the key attribute)
        if hasattr(processor, 'scorable_questions') and len(processor.scorable_questions) > 0:
            question_count = len(processor.scorable_questions)
            print_result("AIA questions loaded", True, f"{question_count} scorable questions")
        else:
            print_result("AIA questions loaded", False)
            errors.append("AIA questions not loaded")

        # Check scorable questions
        if hasattr(processor, 'scorable_questions') and processor.scorable_questions:
            scorable_count = len(processor.scorable_questions)
            print_result("Scorable questions identified", True, f"{scorable_count} questions")
        else:
            print_result("Scorable questions identified", False)
            errors.append("Scorable questions not identified")

        return len(errors) == 0, errors

    except Exception as e:
        print_result("AIA processor", False, str(e))
        return False, [f"AIA processor validation failed: {str(e)}"]

def validate_osfi_processor() -> Tuple[bool, List[str]]:
    """Validate basic OSFI E-23 processor functionality."""
    print_section("VALIDATION 6: OSFI E-23 Processor")

    errors = []
    try:
        from osfi_e23_processor import OSFIE23Processor

        processor = OSFIE23Processor()
        print_result("OSFIE23Processor instantiation", True)

        # Check framework data loaded
        if hasattr(processor, 'framework_data') and processor.framework_data:
            print_result("OSFI framework data loaded", True)
        else:
            print_result("OSFI framework data loaded", False)
            errors.append("OSFI framework data not loaded")

        return len(errors) == 0, errors

    except Exception as e:
        print_result("OSFI processor", False, str(e))
        return False, [f"OSFI processor validation failed: {str(e)}"]

def validate_workflow_engine() -> Tuple[bool, List[str]]:
    """Validate workflow engine functionality."""
    print_section("VALIDATION 7: Workflow Engine")

    errors = []
    try:
        from workflow_engine import WorkflowEngine

        engine = WorkflowEngine()
        print_result("WorkflowEngine instantiation", True)

        # Check workflow definitions exist
        if hasattr(engine, 'workflows') and engine.workflows:
            workflow_count = len(engine.workflows)
            print_result("Workflow definitions loaded", True, f"{workflow_count} workflows")
        else:
            print_result("Workflow definitions loaded", False)
            errors.append("Workflow definitions not loaded")

        return len(errors) == 0, errors

    except Exception as e:
        print_result("Workflow engine", False, str(e))
        return False, [f"Workflow engine validation failed: {str(e)}"]

def validate_description_validator() -> Tuple[bool, List[str]]:
    """Validate description validator functionality."""
    print_section("VALIDATION 8: Description Validator")

    errors = []
    try:
        from description_validator import ProjectDescriptionValidator

        validator = ProjectDescriptionValidator()
        print_result("ProjectDescriptionValidator instantiation", True)

        # Test with sample description
        sample_description = """
        This is a credit risk assessment system for our financial institution.
        It uses machine learning to analyze customer data and predict default risk.
        The system processes transaction history, credit scores, and demographic information.
        """

        result = validator.validate_description(sample_description)
        print_result("Validation execution", True)

        # Check result structure
        required_keys = ["is_valid", "total_words", "areas_covered"]
        for key in required_keys:
            if key in result:
                print_result(f"Result contains '{key}'", True, f"Value: {result[key]}")
            else:
                print_result(f"Result contains '{key}'", False)
                errors.append(f"Missing key in validation result: {key}")

        return len(errors) == 0, errors

    except Exception as e:
        print_result("Description validator", False, str(e))
        return False, [f"Description validator validation failed: {str(e)}"]

def main():
    """Run all validations."""
    print("\n" + "=" * 80)
    print("  COMPREHENSIVE FUNCTIONALITY VALIDATION")
    print("  Testing all core functionality before/after refactoring")
    print("=" * 80)

    all_results = []
    all_errors = []

    # Run all validations
    validations = [
        ("Module Imports", validate_imports),
        ("Server Initialization", validate_server_initialization),
        ("Framework Detection", validate_framework_detection),
        ("Tool Registration", validate_tool_registration),
        ("AIA Processor", validate_aia_processor),
        ("OSFI Processor", validate_osfi_processor),
        ("Workflow Engine", validate_workflow_engine),
        ("Description Validator", validate_description_validator),
    ]

    for name, validation_func in validations:
        try:
            passed, errors = validation_func()
            all_results.append((name, passed))
            if errors:
                all_errors.extend(errors)
        except Exception as e:
            print(f"\n❌ Validation '{name}' crashed: {str(e)}\n")
            all_results.append((name, False))
            all_errors.append(f"{name} crashed: {str(e)}")

    # Print summary
    print_section("VALIDATION SUMMARY")

    passed_count = sum(1 for _, passed in all_results if passed)
    total_count = len(all_results)

    for name, passed in all_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {name}")

    print(f"\n{'=' * 80}")
    print(f"  OVERALL: {passed_count}/{total_count} validations passed")
    print(f"{'=' * 80}\n")

    if all_errors:
        print("\n⚠️  ERRORS ENCOUNTERED:\n")
        for error in all_errors:
            print(f"  • {error}")
        print()

    # Exit with appropriate code
    if passed_count == total_count:
        print("🎉 ALL VALIDATIONS PASSED - Safe to proceed with refactoring\n")
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED - Do NOT proceed with refactoring\n")
        print("Fix the issues above before starting refactoring.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
