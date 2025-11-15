#!/usr/bin/env python3
"""
Test framework detection logic for smart UX improvements.

This test validates that the MCP server correctly detects which framework
to show based on user context, reducing cognitive load.
"""

import sys
from server import MCPServer

def test_framework_detection():
    """Test the framework detection logic with various user scenarios."""

    server = MCPServer()

    test_cases = [
        # OSFI E-23 Detection Tests
        {
            "name": "OSFI Explicit Mention",
            "context": "Run through OSFI framework for my credit model",
            "expected": "osfi_e23",
            "description": "User explicitly mentions OSFI"
        },
        {
            "name": "Bank Context",
            "context": "I need to assess my model for our bank's lending system",
            "expected": "osfi_e23",
            "description": "User mentions 'bank'"
        },
        {
            "name": "Financial Institution",
            "context": "Help with compliance for our financial institution's risk model",
            "expected": "osfi_e23",
            "description": "User mentions 'financial institution'"
        },
        {
            "name": "Credit Risk Model",
            "context": "We have a credit risk model that needs assessment",
            "expected": "osfi_e23",
            "description": "User mentions 'credit risk model'"
        },
        {
            "name": "E-23 Guideline",
            "context": "Need help with E-23 guideline compliance",
            "expected": "osfi_e23",
            "description": "User mentions 'E-23'"
        },

        # AIA Detection Tests
        {
            "name": "AIA Explicit Mention",
            "context": "I need to complete an AIA for our benefits system",
            "expected": "aia",
            "description": "User explicitly mentions AIA"
        },
        {
            "name": "Government Context",
            "context": "This is for a federal government automated decision system",
            "expected": "aia",
            "description": "User mentions 'federal government'"
        },
        {
            "name": "Algorithmic Impact",
            "context": "We need an algorithmic impact assessment",
            "expected": "aia",
            "description": "User mentions 'algorithmic impact assessment'"
        },
        {
            "name": "Public Service",
            "context": "Our public service program needs compliance assessment",
            "expected": "aia",
            "description": "User mentions 'public service'"
        },
        {
            "name": "Automated Decision",
            "context": "Help with automated decision-making compliance for eligibility",
            "expected": "aia",
            "description": "User mentions 'automated decision-making'"
        },

        # Combined/Both Detection Tests
        {
            "name": "Explicit Both Request",
            "context": "I need both AIA and OSFI assessments",
            "expected": "both",
            "description": "User explicitly asks for both"
        },
        {
            "name": "Government and Bank",
            "context": "This is for government services provided through a bank",
            "expected": "aia",  # Primary context is government service
            "description": "User mentions government primarily, bank secondarily (correct to detect AIA)"
        },
        {
            "name": "Combined Assessment",
            "context": "Need a combined assessment for our system",
            "expected": "both",
            "description": "User mentions 'combined assessment'"
        },

        # Unclear Context Tests (should default to 'both')
        {
            "name": "Generic AI System",
            "context": "Help me assess my AI system",
            "expected": "both",
            "description": "Generic request without framework indicators"
        },
        {
            "name": "Machine Learning Model",
            "context": "I have a machine learning model",
            "expected": "both",
            "description": "Generic ML mention without context"
        },
        {
            "name": "Empty Context",
            "context": "",
            "expected": "both",
            "description": "No context provided"
        }
    ]

    print("=" * 80)
    print("FRAMEWORK DETECTION TEST SUITE")
    print("=" * 80)
    print()

    passed = 0
    failed = 0

    for test in test_cases:
        result = server._detect_framework_context(test["context"])

        if result == test["expected"]:
            passed += 1
            status = "✅ PASS"
        else:
            failed += 1
            status = "❌ FAIL"

        print(f"{status} | {test['name']}")
        print(f"   Context: '{test['context']}'")
        print(f"   Expected: {test['expected']} | Got: {result}")
        print(f"   Description: {test['description']}")
        print()

    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)

    return failed == 0


def test_introduction_response_structure():
    """Test that the introduction response has the correct structure for each framework."""

    server = MCPServer()

    print("\n" + "=" * 80)
    print("INTRODUCTION RESPONSE STRUCTURE TEST")
    print("=" * 80)
    print()

    test_cases = [
        {
            "name": "OSFI E-23 Introduction",
            "arguments": {"user_context": "Run through OSFI for my credit model"},
            "should_have": ["framework_workflow"],
            "should_not_have": ["framework_workflows"],
            "workflow_title_contains": "OSFI E-23"
        },
        {
            "name": "AIA Introduction",
            "arguments": {"user_context": "I need an AIA assessment"},
            "should_have": ["framework_workflow"],
            "should_not_have": ["framework_workflows"],
            "workflow_title_contains": "AIA"
        },
        {
            "name": "Both Frameworks Introduction",
            "arguments": {"user_context": "Help me assess my AI system"},
            "should_have": ["framework_workflows"],
            "should_not_have": ["framework_workflow"],
            "workflow_title_contains": None
        }
    ]

    passed = 0
    failed = 0

    for test in test_cases:
        try:
            response = server._get_server_introduction(test["arguments"])

            # Check required fields
            has_required = all(field in response for field in test["should_have"])
            lacks_forbidden = all(field not in response for field in test["should_not_have"])

            # Check workflow title if specified
            title_check = True
            if test["workflow_title_contains"]:
                if "framework_workflow" in response:
                    title_check = test["workflow_title_contains"] in response["framework_workflow"]["title"]

            if has_required and lacks_forbidden and title_check:
                passed += 1
                print(f"✅ PASS | {test['name']}")
                if "framework_workflow" in response:
                    print(f"   Single workflow: {response['framework_workflow']['title']}")
                else:
                    print(f"   Multiple workflows: AIA + OSFI E-23")
            else:
                failed += 1
                print(f"❌ FAIL | {test['name']}")
                print(f"   Has required fields: {has_required}")
                print(f"   Lacks forbidden fields: {lacks_forbidden}")
                print(f"   Title check: {title_check}")

        except Exception as e:
            failed += 1
            print(f"❌ FAIL | {test['name']}")
            print(f"   Exception: {str(e)}")

        print()

    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    detection_passed = test_framework_detection()
    structure_passed = test_introduction_response_structure()

    if detection_passed and structure_passed:
        print("\n🎉 ALL TESTS PASSED! Framework detection is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED. Please review the output above.")
        sys.exit(1)
