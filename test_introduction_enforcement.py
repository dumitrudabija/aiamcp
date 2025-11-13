#!/usr/bin/env python3
"""
Test Introduction Enforcement
Verifies that assessment tools cannot be called without first calling get_server_introduction
"""

import sys
import json
from server import MCPServer

def test_introduction_enforcement():
    """Test that assessment tools require introduction first."""
    print("\n" + "="*80)
    print("TESTING: Introduction Enforcement")
    print("="*80)

    server = MCPServer()

    # Test data
    test_project = {
        "projectName": "Test AI System",
        "projectDescription": "This is a comprehensive test of a machine learning system used for credit risk assessment in a financial institution. The system processes customer financial data including income, credit history, employment status, and transaction patterns. It uses ensemble machine learning models including gradient boosting and neural networks. The system makes automated lending decisions for loan amounts up to $50,000. It impacts customer access to credit and financial services. The technical architecture includes data preprocessing, feature engineering, model training pipeline, and a decision API."
    }

    # Tools that should be gated
    gated_tools = [
        ("assess_project", {"projectName": test_project["projectName"],
                           "projectDescription": test_project["projectDescription"],
                           "responses": []}),
        ("analyze_project_description", test_project),
        ("functional_preview", test_project),
        ("assess_model_risk", test_project),
        ("create_workflow", test_project),
        ("evaluate_lifecycle_compliance", {**test_project, "currentStage": "Design"}),
        ("generate_risk_rating", test_project),
        ("create_compliance_framework", {**test_project, "riskLevel": "Medium"}),
    ]

    print("\n1. Testing tools WITHOUT calling get_server_introduction first")
    print("-" * 80)

    all_blocked = True
    for tool_name, args in gated_tools:
        result = server._call_tool(1, {"name": tool_name, "arguments": args})

        # Parse result
        if "result" in result:
            content = json.loads(result["result"]["content"][0]["text"])
            if "error" in content and content["error"] == "INTRODUCTION_REQUIRED":
                print(f"✅ {tool_name}: Correctly blocked")
            else:
                print(f"❌ {tool_name}: NOT blocked - ENFORCEMENT FAILED!")
                print(f"   Response: {json.dumps(content, indent=2)[:200]}")
                all_blocked = False
        else:
            print(f"❌ {tool_name}: Unexpected error format")
            all_blocked = False

    print("\n2. Testing after calling get_server_introduction")
    print("-" * 80)

    # Call introduction
    intro_result = server._call_tool(1, {"name": "get_server_introduction", "arguments": {}})
    if "result" in intro_result:
        print("✅ get_server_introduction called successfully")
    else:
        print("❌ get_server_introduction failed!")
        return False

    # Now test that tools work
    print("\n3. Testing tools AFTER introduction")
    print("-" * 80)

    all_passed = True
    # Test a few tools (not all, to keep test fast)
    test_after_intro = [
        ("create_workflow", test_project),
        ("functional_preview", test_project),
        ("assess_model_risk", test_project),
    ]

    for tool_name, args in test_after_intro:
        result = server._call_tool(1, {"name": tool_name, "arguments": args})

        if "result" in result:
            content = json.loads(result["result"]["content"][0]["text"])
            if "error" in content and content["error"] == "INTRODUCTION_REQUIRED":
                print(f"❌ {tool_name}: Still blocked after introduction - LOGIC ERROR!")
                all_passed = False
            else:
                print(f"✅ {tool_name}: Correctly allowed after introduction")
        else:
            # Tool may fail for other reasons (like validation), but not due to introduction requirement
            print(f"⚠️  {tool_name}: Error occurred (not introduction requirement)")

    print("\n4. Testing introduction_shown flag state")
    print("-" * 80)

    if server.introduction_shown:
        print("✅ introduction_shown flag is True after calling get_server_introduction")
    else:
        print("❌ introduction_shown flag is False - FLAG NOT SET!")
        all_passed = False

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    if all_blocked and all_passed:
        print("✅ ALL TESTS PASSED - Introduction enforcement working correctly")
        print("\nKey verification points:")
        print("  ✓ All assessment tools blocked before introduction")
        print("  ✓ Tools allowed after calling get_server_introduction")
        print("  ✓ introduction_shown flag properly maintained")
        return True
    else:
        print("❌ SOME TESTS FAILED - Review implementation")
        if not all_blocked:
            print("  ✗ Some tools were not blocked before introduction")
        if not all_passed:
            print("  ✗ Some tools failed after introduction was called")
        return False

if __name__ == "__main__":
    success = test_introduction_enforcement()
    sys.exit(0 if success else 1)
