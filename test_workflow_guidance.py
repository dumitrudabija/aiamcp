#!/usr/bin/env python3
"""
Test script to verify get_server_introduction provides complete workflow guidance.

This test verifies:
1. get_server_introduction includes OSFI E-23 6-step workflow
2. get_server_introduction includes AIA 5-step workflow
3. Tool descriptions include step numbers
4. Introduction includes behavioral directives to present first
"""

import sys
import os
from server import MCPServer

def test_introduction_workflow_guidance():
    """Test that get_server_introduction provides comprehensive workflow guidance."""

    print("=" * 80)
    print("TESTING: get_server_introduction Workflow Guidance")
    print("=" * 80)

    # Initialize server
    server = MCPServer()

    # Get introduction
    print("\n1. Calling get_server_introduction...")
    print("-" * 80)
    intro_result = server._get_server_introduction({})

    # Check for assistant directives
    print("\n2. Checking Assistant Directives...")
    print("-" * 80)
    assert "assistant_directive" in intro_result, "Missing assistant_directive"
    assert "STOP AND PRESENT THIS INTRODUCTION FIRST" in intro_result["assistant_directive"]["critical_instruction"], \
        "Missing critical instruction to present first"
    print("✅ Assistant directive includes instruction to present first")
    print(f"   Critical instruction: {intro_result['assistant_directive']['critical_instruction'][:100]}...")

    # Check for OSFI E-23 workflow
    print("\n3. Checking OSFI E-23 Workflow Sequence...")
    print("-" * 80)
    assert "framework_workflows" in intro_result, "Missing framework_workflows"
    assert "osfi_e23_workflow" in intro_result["framework_workflows"], "Missing osfi_e23_workflow"

    osfi_workflow = intro_result["framework_workflows"]["osfi_e23_workflow"]
    assert "sequence" in osfi_workflow, "Missing OSFI workflow sequence"

    osfi_steps = osfi_workflow["sequence"]
    assert len(osfi_steps) == 6, f"Expected 6 OSFI steps, got {len(osfi_steps)}"

    print(f"✅ OSFI E-23 workflow has {len(osfi_steps)} steps:")
    for step in osfi_steps:
        print(f"   Step {step['step']}: {step['tool']} - {step['purpose']}")

    # Verify step sequence
    expected_tools = [
        "validate_project_description",
        "assess_model_risk",
        "evaluate_lifecycle_compliance",
        "generate_risk_rating",
        "create_compliance_framework",
        "export_e23_report"
    ]

    for i, (step, expected_tool) in enumerate(zip(osfi_steps, expected_tools), 1):
        assert step["step"] == i, f"Step number mismatch: expected {i}, got {step['step']}"
        assert expected_tool in step["tool"], f"Step {i}: expected {expected_tool}, got {step['tool']}"

    print("✅ OSFI E-23 workflow sequence is correct")

    # Check for AIA workflow
    print("\n4. Checking AIA Workflow Sequence...")
    print("-" * 80)
    assert "aia_workflow" in intro_result["framework_workflows"], "Missing aia_workflow"

    aia_workflow = intro_result["framework_workflows"]["aia_workflow"]
    aia_steps = aia_workflow["sequence"]
    assert len(aia_steps) == 5, f"Expected 5 AIA steps, got {len(aia_steps)}"

    print(f"✅ AIA workflow has {len(aia_steps)} steps:")
    for step in aia_steps:
        print(f"   Step {step['step']}: {step['tool']} - {step['purpose']}")

    # Check for next steps guidance
    print("\n5. Checking Next Steps Guidance...")
    print("-" * 80)
    assert "next_steps_guidance" in intro_result, "Missing next_steps_guidance"
    assert "user_choice_required" in intro_result["next_steps_guidance"], "Missing user_choice_required"
    assert "options" in intro_result["next_steps_guidance"], "Missing framework options"

    options = intro_result["next_steps_guidance"]["options"]
    assert len(options) == 4, f"Expected 4 options, got {len(options)}"
    print("✅ Next steps guidance includes 4 framework options:")
    for key, value in options.items():
        print(f"   {key}: {value}")

    # Check tool descriptions include step numbers
    print("\n6. Checking Tool Descriptions Include Step Numbers...")
    print("-" * 80)

    # Get tools list
    tools_response = server._list_tools(1)
    tools = tools_response["result"]["tools"]

    tool_checks = {
        "validate_project_description": "STEP 1",
        "assess_model_risk": "STEP 2 OF 6",
        "evaluate_lifecycle_compliance": "STEP 3 OF 6",
        "generate_risk_rating": "STEP 4 OF 6",
        "create_compliance_framework": "STEP 5 OF 6",
        "export_e23_report": "STEP 6 OF 6"
    }

    for tool in tools:
        if tool["name"] in tool_checks:
            expected_text = tool_checks[tool["name"]]
            assert expected_text in tool["description"], \
                f"Tool {tool['name']} description missing '{expected_text}'"
            print(f"✅ {tool['name']}: Contains '{expected_text}'")

    print("\n" + "=" * 80)
    print("ALL TESTS PASSED!")
    print("=" * 80)
    print("\n✅ get_server_introduction now provides:")
    print("   - Complete 6-step OSFI E-23 workflow sequence")
    print("   - Complete 5-step AIA workflow sequence")
    print("   - Explicit behavioral directive to present introduction first")
    print("   - 4 clear framework options for user selection")
    print("   - Step numbers in all OSFI E-23 tool descriptions")
    print()

if __name__ == "__main__":
    try:
        test_introduction_workflow_guidance()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
