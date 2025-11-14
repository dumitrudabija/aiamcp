#!/usr/bin/env python3
"""
Test automatic session management for direct OSFI E-23 tool calls.

This test simulates Claude calling tools directly (not through workflow),
and verifies that:
1. Auto-session is created automatically
2. assess_model_risk result is stored in session
3. export_e23_report auto-injects assessment_results from session
4. Generated report has COMPLETE data (not zeros)
"""

import sys
import json
from server import MCPServer

def test_auto_session_workflow():
    """Test that direct tool calls work with automatic session management."""

    print("=" * 80)
    print("TEST: Automatic Session Management for Direct OSFI E-23 Tool Calls")
    print("=" * 80)

    server = MCPServer()

    # Step 0: Call get_server_introduction (required first call)
    print("\n0. Calling get_server_introduction (required first)...")
    print("-" * 80)
    intro_params = {"name": "get_server_introduction", "arguments": {}}
    server._call_tool(request_id=0, params=intro_params)
    print("✅ Introduction shown")

    project_name = "Test Credit Model"
    project_desc = (
        "AI-powered credit scoring model using machine learning algorithms including random forests and gradient boosting for automated lending decisions. "
        "The system processes large-scale commercial loans exceeding $200M annually with direct financial impact on capital allocation and lending portfolio performance. "
        "Customer-facing system affecting creditworthiness determinations for business clients. "
        "Data sources include credit bureau data, financial statements, transaction histories from internal banking systems, and third-party economic indicators. "
        "Technical architecture uses Python-based microservices deployed on AWS cloud infrastructure with PostgreSQL databases and real-time API integrations. "
        "Automated decisions are made for loans under $500K with human review required for larger amounts."
    )

    # Step 1: Call assess_model_risk directly (simulating Claude)
    print("\n1. Calling assess_model_risk directly (as Claude would)...")
    print("-" * 80)

    assess_params = {
        "name": "assess_model_risk",
        "arguments": {
            "projectName": project_name,
            "projectDescription": project_desc
        }
    }

    assess_response = server._call_tool(request_id=1, params=assess_params)
    assess_result = json.loads(assess_response["result"]["content"][0]["text"])

    print(f"assess_model_risk response keys: {list(assess_result.keys())}")
    if 'assessment' in assess_result:
        print(f"WRAPPED in 'assessment' - status: {assess_result['assessment'].get('status')}")
        print(f"Full response: {json.dumps(assess_result, indent=2)[:500]}")

    print(f"✅ assess_model_risk completed")
    print(f"   Risk Score: {assess_result.get('risk_score')}")
    print(f"   Risk Level: {assess_result.get('risk_level')}")
    print(f"   Has risk_analysis? {('risk_analysis' in assess_result)}")

    if 'risk_analysis' in assess_result:
        print(f"   Quantitative indicators: {list(assess_result['risk_analysis']['quantitative_indicators'].keys())}")
        print(f"   Qualitative indicators: {list(assess_result['risk_analysis']['qualitative_indicators'].keys())}")

    # Step 2: Call export_e23_report WITHOUT assessment_results parameter
    print("\n2. Calling export_e23_report WITHOUT assessment_results (testing auto-inject)...")
    print("-" * 80)

    export_params = {
        "name": "export_e23_report",
        "arguments": {
            "project_name": project_name,
            "project_description": project_desc
            # NOTE: NOT passing assessment_results - should auto-inject from session!
        }
    }

    export_response = server._call_tool(request_id=2, params=export_params)
    export_result = json.loads(export_response["result"]["content"][0]["text"])

    if "error" in export_result:
        print(f"❌ FAILED: {export_result['error']}")
        print(f"   Reason: {export_result.get('reason')}")
        print(f"   Required Action: {export_result.get('required_action')}")
        return False

    print(f"✅ export_e23_report completed")
    print(f"   File: {export_result.get('file_path')}")
    print(f"   Size: {export_result.get('file_size')}")
    print(f"   Risk Level: {export_result.get('risk_level')}")

    # Step 3: Verify the generated document has complete data
    print("\n3. Verifying generated document has COMPLETE calculation data...")
    print("-" * 80)

    from docx import Document
    doc = Document(export_result['file_path'])

    has_indicators = False
    has_scoring = False
    has_zero_only = True

    for para in doc.paragraphs:
        text = para.text.strip()

        # Check for indicator detection
        if 'Financial Impact' in text or 'Customer Facing' in text or 'Ai Ml Usage' in text:
            has_indicators = True
            print(f"   ✅ Found indicator: {text[:60]}...")

        # Check for scoring
        if 'Subtotal:' in text and 'points' in text:
            has_scoring = True
            # Check if it's not zero
            if not '0 points' in text:
                has_zero_only = False
            print(f"   ✅ Found scoring: {text}")

    print("\n" + "=" * 80)
    print("TEST RESULTS:")
    print("=" * 80)

    if has_indicators and has_scoring and not has_zero_only:
        print("✅ SUCCESS: Auto-session management works correctly!")
        print("   - Assessment results automatically stored in session")
        print("   - Export automatically retrieved data from session")
        print("   - Generated document contains COMPLETE calculation data")
        return True
    else:
        print("❌ FAILURE: Auto-session management has issues")
        print(f"   - Has indicators: {has_indicators}")
        print(f"   - Has scoring: {has_scoring}")
        print(f"   - Has only zeros: {has_zero_only}")
        return False

if __name__ == "__main__":
    try:
        success = test_auto_session_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
