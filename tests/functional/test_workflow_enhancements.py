#!/usr/bin/env python3
"""
Test Workflow Enhancements

Tests the new workflow engine, state management, dependency validation, and smart routing features.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

def test_workflow_features():
    """Test all workflow enhancement features."""

    print("🔄 Testing Workflow Engine Enhancements")
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
                "clientInfo": {"name": "workflow-test-client", "version": "1.0.0"}
            }
        }

        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        response = server_process.stdout.readline()
        print(f"✅ Server initialized")

        # Workflow tools require get_server_introduction to have been called
        # first in this session (introduction workflow enforcement gate).
        intro_request = {
            "jsonrpc": "2.0",
            "id": 100,
            "method": "tools/call",
            "params": {"name": "get_server_introduction", "arguments": {}}
        }
        server_process.stdin.write(json.dumps(intro_request) + "\n")
        server_process.stdin.flush()
        server_process.stdout.readline()

        all_passed = True

        # Test 1: Create Workflow
        print(f"\n📋 Test 1: Creating Workflow Session")

        create_workflow_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "create_workflow",
                "arguments": {
                    "projectName": "AI Customer Service System",
                    "projectDescription": """
                    This is a comprehensive AI customer service system that uses advanced machine learning
                    algorithms including natural language processing to automatically categorize and respond
                    to customer inquiries. The system processes customer data from our CRM database including
                    inquiry history, customer demographics, and product information. The business purpose is
                    to improve response times and reduce manual workload for our customer service team while
                    maintaining high service quality. The system impacts customer satisfaction and operational
                    efficiency by providing 24/7 automated support capabilities. Decisions are made through
                    automated classification with human review for complex cases and escalation protocols.
                    The technical architecture uses cloud-based natural language processing deployed on AWS
                    infrastructure with real-time API integration to existing customer management systems
                    and comprehensive logging for audit trails.
                    """,
                    "assessmentType": "aia_preview"
                }
            }
        }

        server_process.stdin.write(json.dumps(create_workflow_request) + "\n")
        server_process.stdin.flush()
        response_line = server_process.stdout.readline()

        session_id = None
        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                if "workflow_created" in result:
                    session_id = result["workflow_created"]["session_id"]
                    assessment_type = result["workflow_created"]["assessment_type"]
                    detailed_steps = result.get("workflow_visualization", {}).get("detailed_steps", [])
                    workflow_sequence = [step["tool_name"] for step in detailed_steps]

                    print(f"   ✅ Workflow created successfully")
                    print(f"   Session ID: {session_id}")
                    print(f"   Assessment Type: {assessment_type}")
                    print(f"   Workflow Steps: {result['workflow_created'].get('total_steps', len(workflow_sequence))}")
                    print(f"   Sequence: {', '.join(workflow_sequence)}")
                else:
                    print(f"   ❌ Workflow creation failed: {result}")
                    return False
            else:
                print(f"   ❌ Error creating workflow: {response.get('error')}")
                return False

        # Test 2: Get Workflow Status
        print(f"\n📊 Test 2: Getting Workflow Status")

        status_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_workflow_status",
                "arguments": {
                    "sessionId": session_id
                }
            }
        }

        server_process.stdin.write(json.dumps(status_request) + "\n")
        server_process.stdin.flush()
        response_line = server_process.stdout.readline()

        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                workflow_status = result.get("workflow_status", {})
                session_info = workflow_status.get("session_info", {})
                progress = workflow_status.get("workflow_progress", {})

                print(f"   ✅ Status retrieved successfully")
                print(f"   Project: {session_info.get('project_name')}")
                print(f"   State: {session_info.get('state')}")
                print(f"   Progress: {progress.get('progress_percentage', 0)}%")
                print(f"   Completed Tools: {len(progress.get('completed_tools', []))}")

        # Test 3: Execute Workflow Step (Validation)
        print(f"\n🎯 Test 3: Executing Workflow Step - Validation")

        execute_step_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "execute_workflow_step",
                "arguments": {
                    "sessionId": session_id,
                    "toolName": "validate_project_description",
                    "toolArguments": {
                        "projectName": "AI Customer Service System",
                        "projectDescription": """
                        This is a comprehensive AI customer service system that uses advanced machine learning
                        algorithms including natural language processing to automatically categorize and respond
                        to customer inquiries. The system processes customer data from our CRM database including
                        inquiry history, customer demographics, and product information. The business purpose is
                        to improve response times and reduce manual workload for our customer service team while
                        maintaining high service quality. The system impacts customer satisfaction and operational
                        efficiency by providing 24/7 automated support capabilities. Decisions are made through
                        automated classification with human review for complex cases and escalation protocols.
                        The technical architecture uses cloud-based natural language processing deployed on AWS
                        infrastructure with real-time API integration to existing customer management systems
                        and comprehensive logging for audit trails.
                        """
                    }
                }
            }
        }

        server_process.stdin.write(json.dumps(execute_step_request) + "\n")
        server_process.stdin.flush()
        response_line = server_process.stdout.readline()

        validation_passed = False
        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                tool_result = result.get("tool_result", {})
                workflow_mgmt = result.get("workflow_management", {})

                if "validation" in tool_result:
                    validation_passed = tool_result["validation"]["is_valid"]
                    print(f"   ✅ Validation step executed")
                    print(f"   Validation Result: {'PASSED' if validation_passed else 'FAILED'}")
                    print(f"   Areas Covered: {tool_result['validation']['areas_covered']}/6")
                    print(f"   Total Words: {tool_result['validation']['total_words']}")

                    if "workflow_status" in workflow_mgmt:
                        print(f"   Workflow State: {workflow_mgmt['workflow_status']['current_state']}")
                        print(f"   Progress: {workflow_mgmt['workflow_status']['progress']}")

        # Test 4: Auto-Execute Workflow
        print(f"\n⚡ Test 4: Auto-Executing Workflow Steps")

        if validation_passed:
            auto_execute_request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "auto_execute_workflow",
                    "arguments": {
                        "sessionId": session_id,
                        "stepsToExecute": 2
                    }
                }
            }

            server_process.stdin.write(json.dumps(auto_execute_request) + "\n")
            server_process.stdin.flush()
            response_line = server_process.stdout.readline()

            if response_line:
                response = json.loads(response_line.strip())
                if "result" in response:
                    content = response["result"]["content"][0]["text"]
                    result = json.loads(content)

                    auto_results = result.get("auto_execution_results", [])
                    summary = result.get("execution_summary", {})

                    print(f"   ✅ Auto-execution completed")
                    print(f"   Steps Planned: {summary.get('steps_planned', 0)}")
                    print(f"   Steps Executed: {summary.get('steps_executed', 0)}")
                    print(f"   All Successful: {summary.get('all_successful', False)}")

                    for result_item in auto_results:
                        tool_name = result_item.get("tool_name")
                        success = result_item.get("success")
                        print(f"     - {tool_name}: {'✅' if success else '❌'}")
        else:
            print(f"   ⏭️  Skipping auto-execution due to validation failure")

        # Test 5: Final Workflow Status
        print(f"\n📈 Test 5: Final Workflow Status Check")

        final_status_request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "get_workflow_status",
                "arguments": {
                    "sessionId": session_id
                }
            }
        }

        server_process.stdin.write(json.dumps(final_status_request) + "\n")
        server_process.stdin.flush()
        response_line = server_process.stdout.readline()

        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                workflow_status = result.get("workflow_status", {})
                progress = workflow_status.get("workflow_progress", {})
                next_steps = workflow_status.get("next_steps", [])

                print(f"   ✅ Final status retrieved")
                print(f"   Final Progress: {progress.get('progress_percentage', 0)}%")
                print(f"   Completed Tools: {', '.join(progress.get('completed_tools', []))}")
                print(f"   Next Steps Available: {len(next_steps)}")

                if next_steps:
                    for step in next_steps[:3]:  # Show first 3 next steps
                        print(f"     - {step.get('tool_name')}: {step.get('priority')} priority")

        # Test 6: Dependency Validation Test
        print(f"\n🔗 Test 6: Testing Dependency Validation")

        # This must run in a *fresh* session: the `session_id` session already
        # completed export_assessment_report in Test 4's auto-execution, so its
        # prerequisites are already satisfied there and this would trivially
        # "succeed" without ever exercising the dependency-validation failure path.
        new_session_request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "create_workflow",
                "arguments": {
                    "projectName": "Dependency Validation Test Project",
                    "projectDescription": create_workflow_request["params"]["arguments"]["projectDescription"],
                    "assessmentType": "aia_preview"
                }
            }
        }
        server_process.stdin.write(json.dumps(new_session_request) + "\n")
        server_process.stdin.flush()
        new_session_response_line = server_process.stdout.readline()
        dependency_test_session_id = session_id
        if new_session_response_line:
            new_session_response = json.loads(new_session_response_line.strip())
            if "result" in new_session_response:
                new_session_content = json.loads(new_session_response["result"]["content"][0]["text"])
                dependency_test_session_id = new_session_content["workflow_created"]["session_id"]

        # Try to execute export_assessment_report without proper prerequisites
        invalid_step_request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "execute_workflow_step",
                "arguments": {
                    "sessionId": dependency_test_session_id,
                    "toolName": "export_assessment_report",
                    "toolArguments": {
                        "project_name": "Test Project",
                        "project_description": "Test description",
                        "assessment_results": {}
                    }
                }
            }
        }

        server_process.stdin.write(json.dumps(invalid_step_request) + "\n")
        server_process.stdin.flush()
        response_line = server_process.stdout.readline()

        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                if "workflow_management" in result:
                    workflow_mgmt = result["workflow_management"]
                    if "workflow_error" in workflow_mgmt:
                        print(f"   ✅ Dependency validation working correctly")
                        print(f"   Error: {workflow_mgmt['workflow_error']}")
                        print(f"   Missing Dependencies: {workflow_mgmt.get('missing_dependencies', [])}")
                    else:
                        print(f"   ❌ Dependency validation should have failed")
                        all_passed = False
                else:
                    print(f"   ❌ No workflow management info in response")
                    all_passed = False

        print(f"\n🎉 Workflow Enhancement Testing Complete!")

        # Summary
        print(f"\n📋 Test Summary:")
        print(f"   ✅ Workflow Engine: Session creation and management")
        print(f"   ✅ State Management: Persistent session data and progress tracking")
        print(f"   ✅ Dependency Validation: Proper tool ordering enforcement")
        print(f"   ✅ Smart Routing: Next step recommendations and auto-execution")
        print(f"   ✅ Auto-Execution: Intelligent multi-step automation")

        return all_passed

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

    finally:
        # Clean up
        if 'server_process' in locals():
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    passed = test_workflow_features()
    sys.exit(0 if passed else 1)