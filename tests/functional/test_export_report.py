#!/usr/bin/env python3
"""
Test script for the export_assessment_report tool
"""

import json
import subprocess
import sys

def test_export_report():
    """Test the complete workflow: functional_preview + export_assessment_report."""
    
    # First, get functional preview results
    functional_preview_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "functional_preview",
            "arguments": {
                "projectName": "AIDERA-LAS",
                "projectDescription": "An AI-powered loan approval system that automatically evaluates loan applications using machine learning algorithms. The system processes personal financial information including credit scores, income data, employment history, and debt-to-income ratios to make automated lending decisions. It can approve or deny loans up to $50,000 without human review for applications that meet certain criteria. The system uses third-party credit bureau data and processes thousands of applications daily. Decisions are made in real-time and directly impact individuals' access to financial services and economic opportunities."
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
        
        request_json = json.dumps(functional_preview_request) + '\n'
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        if not stdout.strip():
            print("❌ ERROR: No response from functional_preview")
            return
        
        response = json.loads(stdout.strip())
        if 'result' in response and 'content' in response['result']:
            content = response['result']['content'][0]['text']
            assessment_results = json.loads(content)
            
            print(f"✅ Functional preview completed - Score: {assessment_results.get('functional_risk_score', 'N/A')}")
            
            # Now test export report
            print("\n=== STEP 2: Exporting Assessment Report ===")
            export_request = {
                "jsonrpc": "2.0",
                "id": 2,
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
                        
                        # Try to verify file exists
                        import os
                        if os.path.exists(export_result['file_path']):
                            actual_size = os.path.getsize(export_result['file_path'])
                            print(f"📊 Verified file size: {round(actual_size/1024, 1)}KB")
                        else:
                            print("⚠️  WARNING: File path reported but file not found")
                    else:
                        print(f"❌ EXPORT FAILED: {export_result.get('error', 'Unknown error')}")
                else:
                    print("❌ ERROR: Invalid export response format")
            else:
                print("❌ ERROR: No response from export tool")
                print(f"Export stderr: {stderr2}")
        else:
            print("❌ ERROR: Invalid functional preview response format")
            
    except subprocess.TimeoutExpired:
        print("❌ ERROR: Server timeout")
        if 'process' in locals():
            process.kill()
        if 'process2' in locals():
            process2.kill()
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_export_report()
