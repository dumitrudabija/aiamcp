#!/usr/bin/env python3
"""
Test Project Description Validation

Tests the new project description validation functionality.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

def test_validation_scenarios():
    """Test various validation scenarios."""

    test_cases = [
        {
            "name": "Insufficient Description (Title Only)",
            "project_name": "AI System",
            "project_description": "An AI system for customer service",
            "expected_valid": False
        },
        {
            "name": "Minimal Valid Description",
            "project_name": "Customer Service AI",
            "project_description": """
            This is a customer service AI system that uses machine learning algorithms to automatically
            categorize and respond to customer inquiries. The system processes customer data from our
            CRM database including inquiry history, customer demographics, and product information.
            The business purpose is to improve response times and reduce manual workload for our
            customer service team. The system impacts customer satisfaction and operational efficiency.
            Decisions are made through automated classification with human review for complex cases.
            The technical architecture uses natural language processing deployed on cloud infrastructure
            with API integration to our existing customer management systems.
            """,
            "expected_valid": True
        },
        {
            "name": "Comprehensive Description",
            "project_name": "Financial Risk Assessment Model",
            "project_description": """
            This is a comprehensive financial risk assessment model that uses advanced machine learning
            algorithms including gradient boosting and neural networks to evaluate credit risk for
            loan applications. The system processes structured data from credit bureaus, transaction
            history, employment records, and financial statements, totaling approximately 500+ data
            points per applicant. The business purpose is to automate preliminary credit risk assessment
            to improve processing speed while maintaining risk management standards for our financial
            institution. The system directly impacts loan approval decisions, affecting customers'
            access to credit and the institution's risk exposure. Decisions are made through automated
            scoring with mandatory human review for high-risk cases and all decisions above $100,000.
            The technical architecture deploys on-premises servers with real-time API integration to
            core banking systems, implementing comprehensive data validation, model monitoring, and
            audit trail capabilities with governance oversight from our Model Risk Management team.
            """,
            "expected_valid": True
        }
    ]

    print("🧪 Testing Project Description Validation")
    print("=" * 60)

    # Start MCP server
    try:
        server_process = subprocess.Popen(
            [sys.executable, "server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(Path.cwd())
        )

        # Give server time to start
        time.sleep(2)

        # Initialize server
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }

        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        response = server_process.stdout.readline()
        print(f"✅ Server initialized")

        # Test each validation scenario
        for i, test_case in enumerate(test_cases, 2):
            print(f"\n📋 Testing: {test_case['name']}")
            print(f"Description length: {len(test_case['project_description'])} characters")

            # Test validation tool
            validation_request = {
                "jsonrpc": "2.0",
                "id": i,
                "method": "tools/call",
                "params": {
                    "name": "validate_project_description",
                    "arguments": {
                        "projectName": test_case["project_name"],
                        "projectDescription": test_case["project_description"]
                    }
                }
            }

            server_process.stdin.write(json.dumps(validation_request) + "\n")
            server_process.stdin.flush()
            response_line = server_process.stdout.readline()

            if response_line:
                try:
                    response = json.loads(response_line.strip())
                    if "result" in response:
                        content = response["result"]["content"][0]["text"]
                        result = json.loads(content)

                        is_valid = result["validation"]["is_valid"]
                        areas_covered = result["validation"]["areas_covered"]
                        total_words = result["validation"]["total_words"]

                        print(f"   Valid: {is_valid} (expected: {test_case['expected_valid']})")
                        print(f"   Areas covered: {areas_covered}/6")
                        print(f"   Total words: {total_words}")

                        if is_valid == test_case["expected_valid"]:
                            print(f"   ✅ Test passed")
                        else:
                            print(f"   ❌ Test failed - expected {test_case['expected_valid']}, got {is_valid}")

                        # Show missing areas if invalid
                        if not is_valid:
                            missing = result["validation"]["areas_missing"]
                            print(f"   Missing areas: {', '.join(missing)}")

                    else:
                        print(f"   ❌ Error in response: {response.get('error', 'Unknown error')}")

                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON response: {response_line}")
            else:
                print(f"   ❌ No response received")

        # Test integration with assessment tools
        print(f"\n🔗 Testing Integration with Assessment Tools")

        # Test with insufficient description
        assessment_request = {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "assess_project",
                "arguments": {
                    "projectName": "Simple AI",
                    "projectDescription": "A simple AI system",
                    "responses": []
                }
            }
        }

        server_process.stdin.write(json.dumps(assessment_request) + "\n")
        server_process.stdin.flush()
        response_line = server_process.stdout.readline()

        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                if result.get("assessment", {}).get("status") == "validation_failed":
                    print("   ✅ Assessment correctly rejected insufficient description")
                else:
                    print("   ❌ Assessment should have rejected insufficient description")
            else:
                print(f"   ❌ Error in assessment response: {response.get('error')}")

        print(f"\n🎉 Validation testing complete!")

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

    finally:
        # Clean up
        if 'server_process' in locals():
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    test_validation_scenarios()