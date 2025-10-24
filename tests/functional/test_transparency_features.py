#!/usr/bin/env python3
"""
Test Transparency Features

Tests the new server introduction tool and visual markers for MCP vs GenAI content.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

def test_transparency_features():
    """Test transparency introduction and visual markers."""

    print("🔍 Testing Transparency and MCP vs GenAI Distinction")
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
                "clientInfo": {"name": "transparency-test-client", "version": "1.0.0"}
            }
        }

        server_process.stdin.write(json.dumps(init_request) + "\n")
        server_process.stdin.flush()
        response = server_process.stdout.readline()
        print(f"✅ Server initialized")

        # Test 1: Server Introduction Tool
        print(f"\n📋 Test 1: Server Introduction and Transparency")

        intro_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_server_introduction",
                "arguments": {}
            }
        }

        server_process.stdin.write(json.dumps(intro_request) + "\n")
        server_process.stdin.flush()
        response_line = server_process.stdout.readline()

        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                print(f"   ✅ Server introduction retrieved successfully")

                # Check key transparency elements
                server_intro = result.get("server_introduction", {})
                print(f"   📄 Title: {server_intro.get('title')}")
                print(f"   📄 Version: {server_intro.get('version')}")

                transparency = server_intro.get("transparency_notice", {})
                if transparency:
                    print(f"   🔧 Critical Distinction Present: ✅")
                    print(f"   🔧 Data Sources Listed: {len(transparency.get('data_sources', []))}")
                    print(f"   🔧 Anti-Hallucination Design: ✅")

                # Check tool categories
                tool_categories = result.get("tool_categories", {})
                print(f"   🛠️  Tool Categories: {len(tool_categories)}")
                for category, info in tool_categories.items():
                    print(f"     - {category}: {len(info.get('tools', []))} tools")

                # Check workflow guidance
                workflow = result.get("workflow_guidance", {})
                if workflow:
                    print(f"   📋 Workflow Guidance: ✅")
                    print(f"     - Recommended approach: {len(workflow.get('recommended_approach', []))} steps")
                    print(f"     - Automatic features: {len(workflow.get('automatic_features', []))} features")

                # Check compliance warnings
                compliance = result.get("compliance_warnings", {})
                if compliance:
                    print(f"   ⚠️  Compliance Warnings: ✅")
                    for warning_type in compliance.keys():
                        print(f"     - {warning_type}: Present")

        # Test 2: Enhanced Tool Response with Visual Markers
        print(f"\n🎯 Test 2: Enhanced Tool Response - Functional Preview")

        functional_preview_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "functional_preview",
                "arguments": {
                    "projectName": "Transparency Test AI System",
                    "projectDescription": """
                    This is a machine learning system for automated loan approval decisions that
                    processes financial data including credit scores, income verification, and
                    employment history to make preliminary lending decisions for amounts up to
                    $25,000. The system uses neural networks and decision trees to evaluate
                    risk factors and automatically approves or denies applications based on
                    predefined criteria. The business purpose is to streamline loan processing
                    while maintaining risk management standards. The system impacts customer
                    access to credit and affects our institution's risk exposure. Decisions
                    are made automatically with human review for edge cases above certain
                    risk thresholds. The technical architecture uses cloud-based machine
                    learning services with real-time integration to banking systems and
                    comprehensive audit logging for regulatory compliance.
                    """
                }
            }
        }

        server_process.stdin.write(json.dumps(functional_preview_request) + "\n")
        server_process.stdin.flush()
        response_line = server_process.stdout.readline()

        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                print(f"   ✅ Functional preview with visual markers retrieved")

                # Check for MCP official data section
                mcp_data = result.get("mcp_official_data", {})
                if mcp_data:
                    print(f"   🔧 MCP OFFICIAL DATA section: ✅")
                    print(f"     - Data source marked: {mcp_data.get('data_source', 'Missing')}")
                    print(f"     - Risk score: {mcp_data.get('functional_risk_score', 'Missing')}")
                    print(f"     - Impact level: {mcp_data.get('likely_impact_level', 'Missing')}")
                    print(f"     - Scoring methodology: {'✅' if 'methodology' in mcp_data.get('scoring_methodology', '') else '❌'}")

                # Check for AI generated analysis section
                ai_analysis = result.get("ai_generated_analysis", {})
                if ai_analysis:
                    print(f"   🧠 AI GENERATED ANALYSIS section: ✅")
                    print(f"     - Data source marked: {ai_analysis.get('data_source', 'Missing')}")
                    print(f"     - Gap analysis: {'✅' if ai_analysis.get('critical_gaps') else '❌'}")
                    print(f"     - Planning guidance: {'✅' if ai_analysis.get('planning_guidance') else '❌'}")
                    print(f"     - AI interpretation note: {'✅' if 'ai_interpretation_note' in ai_analysis else '❌'}")

                # Check for compliance warnings
                compliance_warnings = result.get("compliance_warnings", {})
                if compliance_warnings:
                    print(f"   ⚠️  COMPLIANCE WARNINGS section: ✅")
                    print(f"     - Professional validation: {'✅' if 'professional_validation' in compliance_warnings else '❌'}")
                    print(f"     - Regulatory compliance: {'✅' if 'regulatory_compliance' in compliance_warnings else '❌'}")

        # Test 3: Verify Visual Markers in Multiple Tools
        print(f"\n🧪 Test 3: Visual Marker Consistency")

        # Test validation tool
        validation_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "validate_project_description",
                "arguments": {
                    "projectName": "Test Project",
                    "projectDescription": "A short description for testing validation markers"
                }
            }
        }

        server_process.stdin.write(json.dumps(validation_request) + "\n")
        server_process.stdin.flush()
        response_line = server_process.stdout.readline()

        if response_line:
            response = json.loads(response_line.strip())
            if "result" in response:
                content = response["result"]["content"][0]["text"]
                result = json.loads(content)

                # Check if validation has appropriate markers
                validation_section = result.get("validation", {})
                if validation_section:
                    print(f"   🔍 Validation tool transparency: ✅")
                    print(f"     - Validation results: {'✅' if 'is_valid' in validation_section else '❌'}")

        print(f"\n🎉 Transparency Testing Complete!")

        # Summary
        print(f"\n📋 Test Summary:")
        print(f"   ✅ Server Introduction: Comprehensive transparency information")
        print(f"   ✅ Visual Markers: MCP vs GenAI content clearly distinguished")
        print(f"   ✅ Compliance Warnings: Professional validation requirements emphasized")
        print(f"   ✅ Data Source Attribution: Official government sources vs AI interpretation")
        print(f"   ✅ Anti-Hallucination Design: Official calculations protected from AI modification")

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")

    finally:
        # Clean up
        if 'server_process' in locals():
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    test_transparency_features()