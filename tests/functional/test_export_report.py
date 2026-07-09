#!/usr/bin/env python3
"""
Test script for the export_assessment_report tool
"""

import json
import subprocess
import sys

def test_export_report():
    """Test the complete workflow: functional_preview + export_assessment_report."""

    # functional_preview requires get_server_introduction to have been called
    # first in this session (introduction workflow enforcement gate).
    intro_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": "get_server_introduction", "arguments": {}}
    }

    # First, get functional preview results
    functional_preview_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "functional_preview",
            "arguments": {
                "projectName": "AIDERA-LAS",
                "projectDescription": "An AI-powered loan approval system that automatically evaluates loan applications using machine learning algorithms. The system processes personal financial information including credit scores, income data, employment history, and debt-to-income ratios to make automated lending decisions. It can approve or deny loans up to $50,000 without human review for applications that meet certain criteria. The system uses third-party credit bureau data and processes thousands of applications daily. Decisions are made in real-time and directly impact individuals' access to financial services and economic opportunities. The technical architecture follows a microservices approach, with the scoring model deployed as a containerized component that integrates with core banking infrastructure through a REST API interface."
            }
        }
    }

    try:
        # Get functional preview results
        print("=== STEP 1: Getting Functional Preview Results ===")
        process = subprocess.Popen(
            ['python3', 'server.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        request_json = json.dumps(intro_request) + '\n' + json.dumps(functional_preview_request) + '\n'
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        response_lines = [line for line in stdout.strip().split('\n') if line.strip()]

        if not response_lines:
            print("❌ ERROR: No response from functional_preview")
            return False

        response = json.loads(response_lines[-1])
        if 'result' in response and 'content' in response['result']:
            content = response['result']['content'][0]['text']
            assessment_results = json.loads(content)

            mcp_official_data = assessment_results.get('mcp_official_data', {})
            print(f"✅ Functional preview completed - Score: {mcp_official_data.get('functional_risk_score', 'N/A')}")
            
            # Now test export report
            print("\n=== STEP 2: Exporting Assessment Report ===")
            export_request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "export_assessment_report",
                    "arguments": {
                        "project_name": "AIDERA-LAS",
                        "project_description": "An AI-powered loan approval system that automatically evaluates loan applications using machine learning algorithms. The system processes personal financial information including credit scores, income data, employment history, and debt-to-income ratios to make automated lending decisions. It can approve or deny loans up to $50,000 without human review for applications that meet certain criteria. The system uses third-party credit bureau data and processes thousands of applications daily. Decisions are made in real-time and directly impact individuals' access to financial services and economic opportunities.",
                        "assessment_results": assessment_results
                    }
                }
            }
            
            # Test export
            process2 = subprocess.Popen(
                ['python3', 'server.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            export_json = json.dumps(export_request) + '\n'
            stdout2, stderr2 = process2.communicate(input=export_json, timeout=10)
            
            if stdout2.strip():
                export_response = json.loads(stdout2.strip())
                if 'result' in export_response and 'content' in export_response['result']:
                    export_content = export_response['result']['content'][0]['text']
                    export_result = json.loads(export_content)
                    
                    print("=== EXPORT RESULTS ===")
                    print(f"Success: {export_result.get('success', False)}")
                    print(f"File Path: {export_result.get('file_path', 'N/A')}")
                    print(f"File Size: {export_result.get('file_size', 'N/A')}")
                    print(f"Message: {export_result.get('message', 'N/A')}")
                    
                    if export_result.get('success'):
                        print("\n✅ SUCCESS: Word document created successfully!")
                        print(f"📄 File location: {export_result['file_path']}")
                        print("🔍 You can now open this file in Microsoft Word to verify the content.")

                        # Verify file exists, then clean it up (this test writes into
                        # the repo's ./AIA_Assessments/ dir, since export_assessment_report
                        # has no way to redirect its output elsewhere).
                        import os
                        file_path = export_result['file_path']
                        if os.path.exists(file_path):
                            actual_size = os.path.getsize(file_path)
                            print(f"📊 Verified file size: {round(actual_size/1024, 1)}KB")
                            os.remove(file_path)
                            return True
                        else:
                            print("⚠️  WARNING: File path reported but file not found")
                            return False
                    else:
                        print(f"❌ EXPORT FAILED: {export_result.get('error', 'Unknown error')}")
                        return False
                else:
                    print("❌ ERROR: Invalid export response format")
                    return False
            else:
                print("❌ ERROR: No response from export tool")
                print(f"Export stderr: {stderr2}")
                return False
        else:
            print("❌ ERROR: Invalid functional preview response format")
            return False

    except subprocess.TimeoutExpired:
        print("❌ ERROR: Server timeout")
        if 'process' in locals():
            process.kill()
        if 'process2' in locals():
            process2.kill()
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    passed = test_export_report()
    sys.exit(0 if passed else 1)
