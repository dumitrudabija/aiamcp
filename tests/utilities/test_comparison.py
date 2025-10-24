#!/usr/bin/env python3
"""
Test script to compare functional_preview results for different risk levels
"""

import json
import subprocess
import sys

def test_system(name, description):
    """Test a system and return the results."""
    test_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "functional_preview",
            "arguments": {
                "projectName": name,
                "projectDescription": description
            }
        }
    }
    
    try:
        process = subprocess.Popen(
            ['python3', 'server.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        request_json = json.dumps(test_request) + '\n'
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        if stdout.strip():
            response = json.loads(stdout.strip())
            if 'result' in response and 'content' in response['result']:
                content = response['result']['content'][0]['text']
                result = json.loads(content)
                return result
        
    except Exception as e:
        print(f"Error testing {name}: {e}")
    
    return None

def main():
    """Test multiple systems to show scoring differences."""
    
    systems = [
        {
            "name": "AI Loan Approval System",
            "description": "An AI-powered loan approval system that automatically evaluates loan applications using machine learning algorithms. The system processes personal financial information including credit scores, income data, employment history, and debt-to-income ratios to make automated lending decisions. It can approve or deny loans up to $50,000 without human review for applications that meet certain criteria. The system uses third-party credit bureau data and processes thousands of applications daily. Decisions are made in real-time and directly impact individuals' access to financial services and economic opportunities."
        },
        {
            "name": "Simple Document Classifier",
            "description": "A basic document classification system that categorizes incoming documents into predefined categories like 'invoice', 'contract', or 'report'. The system uses simple keyword matching and does not process personal information. All classifications are reviewed by human staff before final categorization. The system handles about 50 documents per day and is used internally for office organization."
        },
        {
            "name": "Healthcare AI Diagnostic Tool",
            "description": "An AI system that analyzes medical images to assist doctors in diagnosing conditions. The system processes sensitive health information and medical records. It provides diagnostic recommendations that doctors use to make treatment decisions affecting patient health outcomes. The system uses machine learning trained on thousands of medical cases and operates in real-time during patient consultations."
        }
    ]
    
    print("=== FUNCTIONAL PREVIEW COMPARISON TEST ===\n")
    
    for system in systems:
        print(f"Testing: {system['name']}")
        print("-" * 50)
        
        result = test_system(system['name'], system['description'])
        
        if result:
            score = result.get('functional_risk_score', 0)
            level = result.get('likely_impact_level', 'N/A')
            guidance_count = len(result.get('planning_guidance', []))
            
            print(f"Score: {score}")
            print(f"Impact Level: {level}")
            print(f"Planning Guidance Items: {guidance_count}")
            
            # Show first few guidance items
            guidance = result.get('planning_guidance', [])
            if guidance:
                print("Key Guidance:")
                for item in guidance[:3]:
                    print(f"  - {item}")
            
            print()
        else:
            print("❌ Test failed\n")
    
    print("=== SUMMARY ===")
    print("Expected results:")
    print("- AI Loan Approval: High score (80-100), Level IV, extensive guidance")
    print("- Document Classifier: Low score (0-20), Level I, minimal guidance") 
    print("- Healthcare AI: High score (60-90), Level III-IV, medical-specific guidance")

if __name__ == "__main__":
    main()
