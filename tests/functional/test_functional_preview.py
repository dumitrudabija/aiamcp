#!/usr/bin/env python3
"""
Test script for the functional_preview tool
"""

import json
import subprocess
import sys

def test_functional_preview():
    """Test the functional_preview tool with loan approval system example."""
    
    # Test request for functional_preview
    test_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "functional_preview",
            "arguments": {
                "projectName": "AI Loan Approval System",
                "projectDescription": "An AI-powered loan approval system that automatically evaluates loan applications using machine learning algorithms. The system processes personal financial information including credit scores, income data, employment history, and debt-to-income ratios to make automated lending decisions. It can approve or deny loans up to $50,000 without human review for applications that meet certain criteria. The system uses third-party credit bureau data and processes thousands of applications daily. Decisions are made in real-time and directly impact individuals' access to financial services and economic opportunities."
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
        
        # Send the request
        request_json = json.dumps(test_request) + '\n'
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        print("=== FUNCTIONAL PREVIEW TEST RESULTS ===")
        print(f"Request sent: {json.dumps(test_request, indent=2)}")
        print(f"\nServer stderr: {stderr}")
        print(f"\nServer response: {stdout}")
        
        # Parse and analyze the response
        if stdout.strip():
            try:
                response = json.loads(stdout.strip())
                if 'result' in response and 'content' in response['result']:
                    content = response['result']['content'][0]['text']
                    result = json.loads(content)
                    
                    print("\n=== ANALYSIS ===")
                    print(f"Project: {result.get('project_name', 'N/A')}")
                    print(f"Functional Risk Score: {result.get('functional_risk_score', 'N/A')}")
                    print(f"Score Range: {result.get('score_range', 'N/A')}")
                    print(f"Likely Impact Level: {result.get('likely_impact_level', 'N/A')}")
                    print(f"Confidence: {result.get('confidence', 'N/A')}")
                    
                    print(f"\nCritical Gaps ({len(result.get('critical_gaps', []))}):")
                    for gap in result.get('critical_gaps', []):
                        print(f"  - {gap}")
                    
                    print(f"\nImportant Gaps ({len(result.get('important_gaps', []))}):")
                    for gap in result.get('important_gaps', []):
                        print(f"  - {gap}")
                    
                    print(f"\nPlanning Guidance ({len(result.get('planning_guidance', []))}):")
                    for guidance in result.get('planning_guidance', []):
                        print(f"  - {guidance}")
                    
                    print(f"\nScore Sensitivity:")
                    for key, value in result.get('score_sensitivity', {}).items():
                        print(f"  - {key}: {value}")
                    
                    # Verify expected scoring improvement
                    score = result.get('functional_risk_score', 0)
                    if score >= 35:
                        print(f"\n✅ SUCCESS: Score of {score} is in expected range (35-50+)")
                    else:
                        print(f"\n❌ ISSUE: Score of {score} is below expected range (35-50+)")
                    
                else:
                    print("❌ ERROR: Invalid response format")
            except json.JSONDecodeError as e:
                print(f"❌ ERROR: Could not parse response JSON: {e}")
        else:
            print("❌ ERROR: No response received")
            
    except subprocess.TimeoutExpired:
        print("❌ ERROR: Server timeout")
        process.kill()
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_functional_preview()
