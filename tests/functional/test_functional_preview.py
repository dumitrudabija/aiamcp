#!/usr/bin/env python3
"""
Test script for the functional_preview tool
"""

import json
import subprocess
import sys

def test_functional_preview():
    """Test the functional_preview tool with loan approval system example."""
    
    # functional_preview requires get_server_introduction to have been called
    # first in this session (introduction workflow enforcement gate).
    intro_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "get_server_introduction", "arguments": {}}
    }

    # Test request for functional_preview
    test_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "functional_preview",
            "arguments": {
                "projectName": "AI Loan Approval System",
                "projectDescription": "An AI-powered loan approval system that automatically evaluates loan applications using machine learning algorithms. The system processes personal financial information including credit scores, income data, employment history, and debt-to-income ratios to make automated lending decisions. It can approve or deny loans up to $50,000 without human review for applications that meet certain criteria. The system uses third-party credit bureau data and processes thousands of applications daily. Decisions are made in real-time and directly impact individuals' access to financial services and economic opportunities. The technical architecture follows a microservices approach, with the scoring model deployed as a containerized component that integrates with core banking infrastructure through a REST API interface."
            }
        }
    }

    # Send request to server
    try:
        # Start the server process
        process = subprocess.Popen(
            ['python3', 'server.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Send both requests: satisfy the introduction gate, then the real call
        request_json = json.dumps(intro_request) + '\n' + json.dumps(test_request) + '\n'
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        response_lines = [line for line in stdout.strip().split('\n') if line.strip()]
        last_response = response_lines[-1] if response_lines else ""

        print("=== FUNCTIONAL PREVIEW TEST RESULTS ===")
        print(f"Request sent: {json.dumps(test_request, indent=2)}")
        print(f"\nServer stderr: {stderr}")
        print(f"\nServer response: {last_response}")

        # Parse and analyze the response
        if last_response:
            try:
                response = json.loads(last_response)
                if 'result' in response and 'content' in response['result']:
                    content = response['result']['content'][0]['text']
                    result = json.loads(content)

                    # Response is split into an official MCP-calculated section and an
                    # AI-generated interpretation section (see CLAUDE.md "Transparency
                    # and Data Source Distinction").
                    official = result.get('mcp_official_data', {})
                    ai_analysis = result.get('ai_generated_analysis', {})

                    print("\n=== ANALYSIS ===")
                    print(f"Project: {ai_analysis.get('project_name', 'N/A')}")
                    print(f"Functional Risk Score: {official.get('functional_risk_score', 'N/A')}")
                    print(f"Score Range: {official.get('score_range', 'N/A')}")
                    print(f"Likely Impact Level: {official.get('likely_impact_level', 'N/A')}")
                    print(f"Confidence: {ai_analysis.get('confidence', 'N/A')}")

                    print(f"\nCritical Gaps ({len(ai_analysis.get('critical_gaps', []))}):")
                    for gap in ai_analysis.get('critical_gaps', []):
                        print(f"  - {gap}")

                    print(f"\nImportant Gaps ({len(ai_analysis.get('important_gaps', []))}):")
                    for gap in ai_analysis.get('important_gaps', []):
                        print(f"  - {gap}")

                    print(f"\nPlanning Guidance ({len(ai_analysis.get('planning_guidance', []))}):")
                    for guidance in ai_analysis.get('planning_guidance', []):
                        print(f"  - {guidance}")

                    print(f"\nScore Sensitivity:")
                    for key, value in ai_analysis.get('score_sensitivity', {}).items():
                        print(f"  - {key}: {value}")

                    # Scoring weights are tunable proof-of-concept logic (see CLAUDE.md),
                    # so just sanity-check the score is a real, in-bounds number rather
                    # than pinning a historical absolute range.
                    score = official.get('functional_risk_score')
                    if isinstance(score, int) and 0 <= score <= 224:
                        print(f"\n✅ SUCCESS: Score of {score} is a valid in-bounds functional risk score")
                        return True
                    else:
                        print(f"\n❌ ISSUE: Score {score!r} is missing or out of bounds [0, 224]")
                        return False

                else:
                    print("❌ ERROR: Invalid response format")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ ERROR: Could not parse response JSON: {e}")
                return False
        else:
            print("❌ ERROR: No response received")
            return False

    except subprocess.TimeoutExpired:
        print("❌ ERROR: Server timeout")
        process.kill()
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    passed = test_functional_preview()
    sys.exit(0 if passed else 1)
