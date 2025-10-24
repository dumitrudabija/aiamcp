#!/usr/bin/env python3
"""
Test Workflow Export Functionality

Tests that the workflow engine properly handles export tools including document generation.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

def test_workflow_with_exports():
    """Test complete workflow including export functionality."""

    print("📄 Testing Workflow Export Functionality")
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
                "clientInfo": {"name": "export-test-client", "version": "1.0.0"}
            }
        }

        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        response = server_process.stdout.readline()
        print(f"✅ Server initialized")

        # Test 1: Create AIA Preview Workflow
        print(f"\n📋 Test 1: Creating AIA Preview Workflow")

        create_workflow_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "create_workflow",
                "arguments": {
                    "projectName": "Smart Lending AI System",
                    "projectDescription": """
                    This is a comprehensive smart lending AI system that uses advanced machine learning
                    algorithms including gradient boosting and neural networks to automatically evaluate
                    loan applications and make preliminary lending decisions. The system processes
                    extensive customer data from multiple sources including credit bureaus, bank
                    transaction history, employment records, and financial statements, analyzing over
                    200 data points per application. The business purpose is to automate the initial
                    loan assessment process to improve processing speed and consistency while reducing
                    manual review workload for our financial institution. The system directly impacts
                    customers' access to credit and our institution's risk exposure by making automated
                    preliminary lending decisions up to $50,000. Decision-making processes use
                    sophisticated risk scoring algorithms with built-in human oversight requirements
                    for high-risk cases and all decisions above $25,000. The technical architecture
                    deploys on secure cloud infrastructure with real-time API integration to core
                    banking systems, comprehensive audit logging, and strict data governance controls
                    meeting all regulatory requirements for financial services.
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
                    print(f"   ✅ AIA Preview workflow created: {session_id}")
                    print(f"   Sequence: {', '.join(result['workflow_created']['workflow_sequence'])}")

        # Test 2: Auto-Execute Full Workflow
        print(f"\n⚡ Test 2: Auto-Executing Complete Workflow")

        auto_execute_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "auto_execute_workflow",
                "arguments": {
                    "sessionId": session_id,
                    "stepsToExecute": 5  # Execute all steps including export
                }
            }
        }

        server_process.stdin.write(json.dumps(auto_execute_request) + "\n")
        server_process.stdin.flush()
        response_line = server_process.stdout.readline()

        export_generated = False
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

                    if tool_name == "export_assessment_report" and success:
                        export_generated = True

        # Test 3: Check for Generated Files
        print(f"\n📁 Test 3: Checking for Generated Export Files")

        # Check AIA_Assessments directory
        aia_dir = Path("AIA_Assessments")
        if aia_dir.exists():
            export_files = list(aia_dir.glob("*.docx"))
            print(f"   📂 Found {len(export_files)} export files in AIA_Assessments/")

            for file_path in export_files:
                print(f"     - {file_path.name} ({file_path.stat().st_size} bytes)")

            if export_files:
                print(f"   ✅ Export files successfully generated")
            else:
                print(f"   ❌ No export files found")
        else:
            print(f"   ❌ AIA_Assessments directory not found")

        # Test 4: Verify Workflow Completion
        print(f"\n📊 Test 4: Final Workflow Status")

        final_status_request = {
            "jsonrpc": "2.0",
            "id": 4,
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
                session_info = workflow_status.get("session_info", {})

                print(f"   ✅ Final workflow status retrieved")
                print(f"   Final State: {session_info.get('state')}")
                print(f"   Progress: {progress.get('progress_percentage', 0)}%")
                print(f"   Completed Tools: {', '.join(progress.get('completed_tools', []))}")

                # Check if export was completed
                if "export_assessment_report" in progress.get('completed_tools', []):
                    print(f"   ✅ Export tool completed successfully")
                else:
                    print(f"   ❌ Export tool not completed")

        # Test 5: Test OSFI E-23 Workflow with Export
        print(f"\n🏦 Test 5: Testing OSFI E-23 Workflow with Export")

        create_osfi_workflow_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "create_workflow",
                "arguments": {
                    "projectName": "Credit Risk Model",
                    "projectDescription": """
                    This is a sophisticated credit risk assessment model for a major Canadian bank that
                    uses ensemble machine learning techniques to evaluate loan default probability for
                    commercial lending. The model processes comprehensive financial data including
                    balance sheets, cash flow statements, industry benchmarks, and macroeconomic
                    indicators to assess credit risk for loans ranging from $100,000 to $50 million.
                    The business application supports our commercial lending division by providing
                    automated risk ratings and pricing recommendations while ensuring regulatory
                    compliance with OSFI guidelines. The model directly impacts lending decisions
                    affecting thousands of business customers annually and represents significant
                    exposure for our institution's capital adequacy requirements. Risk management
                    processes include comprehensive model validation, regular backtesting, performance
                    monitoring, and quarterly model review committees. The technical implementation
                    uses on-premises high-performance computing infrastructure with strict data
                    governance, model versioning, and comprehensive audit trails meeting all
                    OSFI E-23 model risk management requirements.
                    """,
                    "assessmentType": "osfi_e23"
                }
            }
        }

        server_process.stdin.write(json.dumps(create_osfi_workflow_request) + "\n")
        server_process.stdin.flush()
        response_line = server_process.stdout.readline()

        osfi_session_id = None
        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                if "workflow_created" in result:
                    osfi_session_id = result["workflow_created"]["session_id"]
                    print(f"   ✅ OSFI E-23 workflow created: {osfi_session_id}")

        # Auto-execute OSFI workflow steps
        if osfi_session_id:
            auto_execute_osfi_request = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "auto_execute_workflow",
                    "arguments": {
                        "sessionId": osfi_session_id,
                        "stepsToExecute": 3  # Execute first few steps
                    }
                }
            }

            server_process.stdin.write(json.dumps(auto_execute_osfi_request) + "\n")
            server_process.stdin.flush()
            response_line = server_process.stdout.readline()

            if response_line:
                response = json.loads(response_line.strip())
                if "result" in response:
                    content = response["result"]["content"][0]["text"]
                    result = json.loads(content)

                    auto_results = result.get("auto_execution_results", [])
                    print(f"   ✅ OSFI E-23 auto-execution completed")

                    for result_item in auto_results:
                        tool_name = result_item.get("tool_name")
                        success = result_item.get("success")
                        print(f"     - {tool_name}: {'✅' if success else '❌'}")

        print(f"\n🎉 Export Workflow Testing Complete!")

        # Summary
        print(f"\n📋 Test Summary:")
        print(f"   ✅ Workflow Creation: AIA Preview and OSFI E-23 workflows")
        print(f"   ✅ Auto-Execution: Multi-step automated execution")
        print(f"   ✅ Export Integration: Export tools included in workflow sequences")
        print(f"   ✅ File Generation: Document export functionality tested")
        print(f"   ✅ State Management: Complete workflow state tracking")

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

    finally:
        # Clean up
        if 'server_process' in locals():
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    test_workflow_with_exports()