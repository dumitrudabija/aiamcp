#!/usr/bin/env python3
"""
Comprehensive MCP Server Test Suite

Exercises the live JSON-RPC transport (protocol handshake, tool registration,
introduction gate, question retrieval) and cross-checks AIA scoring integrity
via a direct AIAProcessor import.

Note on scoring assertions: OSFI/AIA scoring weights and impact-level
thresholds are explicitly proof-of-concept and institution-tunable (see
CLAUDE.md). This suite therefore asserts *monotonic ordering* and *bounds*
across risk tiers rather than hardcoded absolute scores, since the latter
would silently go stale every time thresholds are retuned.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from typing import Dict, Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

# Long enough (100+ words) and covers system/technology, business purpose, data
# sources, impact scope, decision process, and technical architecture so it
# clears validate_project_description's coverage gate.
RICH_PROJECT_DESCRIPTION = (
    "This system is a machine learning platform that automates loan eligibility "
    "recommendations for a financial institution. The business purpose is to "
    "reduce manual underwriting workload and speed up decisions for customers "
    "applying for credit. The technical architecture consists of a gradient-"
    "boosted model served through an internal API, integrated with the bank's "
    "core loan origination software and database. Data sources include customer "
    "credit history, income records, and employment data collected directly "
    "from applicants and credit bureaus. The decision process involves the "
    "model producing a recommendation that a human underwriter reviews and "
    "approves before any decision is communicated to the customer. The impact "
    "scope covers individual credit applicants across all retail lending "
    "products offered by the institution."
)

from aia_processor import AIAProcessor  # noqa: E402
from config.tool_registry import ToolRegistry  # noqa: E402


class MCPServerTester:
    """Comprehensive tester for AIA Assessment MCP Server."""

    def __init__(self):
        self.server_process = None

        # Native AIAProcessor response format (question_id + selected_values),
        # used for direct scoring-integrity checks below.
        self.test_scenarios = {
            "low_risk": {
                "name": "Simple Internal File Organization Tool",
                "description": "Simple internal file organization tool with no user data. Helps employees organize documents in shared folders with basic categorization features.",
                "sample_responses": [
                    {"question_id": "businessDrivers9", "selected_values": ["item1-0"]},
                    {"question_id": "riskProfile1", "selected_values": ["item2-0"]},
                    {"question_id": "riskProfile2", "selected_values": ["item2-0"]},
                    {"question_id": "riskProfile4", "selected_values": ["item1-0"]},
                    {"question_id": "aboutSystem3", "selected_values": ["item1-0"]},
                    {"question_id": "aboutSystem11", "selected_values": ["item1-1"]},
                    {"question_id": "impact30", "selected_values": ["item2-2"]},
                    {"question_id": "impact3", "selected_values": ["item2-0"]},
                    {"question_id": "aboutDataSource1", "selected_values": ["item2-0"]},
                ],
            },
            "medium_risk": {
                "name": "Customer FAQ Chatbot",
                "description": "Customer FAQ chatbot using company knowledge base. Provides automated responses to common customer questions about products and services using natural language processing.",
                "sample_responses": [
                    {"question_id": "businessDrivers5", "selected_values": ["item1-2"]},
                    {"question_id": "businessDrivers9", "selected_values": ["item1-0"]},
                    {"question_id": "businessDrivers11", "selected_values": ["item1-2"]},
                    {"question_id": "projectAuthority1", "selected_values": ["item1-2"]},
                    {"question_id": "aboutSystem5", "selected_values": ["item3-2"]},
                    {"question_id": "aboutSystem6", "selected_values": ["item2-2"]},
                    {"question_id": "aboutSystem7", "selected_values": ["item2-2"]},
                    {"question_id": "aboutSystem11", "selected_values": ["item2-2"]},
                    {"question_id": "aboutAlgorithm2", "selected_values": ["item1-3"]},
                    {"question_id": "aboutAlgorithm8", "selected_values": ["item1-3"]},
                    {"question_id": "impact30", "selected_values": ["item2-2"]},
                    {"question_id": "impact3", "selected_values": ["item2-0"]},
                    {"question_id": "impact4A", "selected_values": ["item1-2"]},
                    {"question_id": "impact6", "selected_values": ["item2-2"]},
                    {"question_id": "impact7", "selected_values": ["item2-2"]},
                    {"question_id": "impact9", "selected_values": ["item2-2"]},
                    {"question_id": "aboutDataSource1", "selected_values": ["item1-2"]},
                    {"question_id": "aboutDataSource15", "selected_values": ["item2-2"]},
                ],
            },
            "high_risk": {
                "name": "AI Loan Recommendation System",
                "description": "AI loan recommendation system using customer financial data. Analyzes credit history, income, and financial behavior to provide loan approval recommendations to human underwriters.",
                "sample_responses": [
                    {"question_id": "riskProfile1", "selected_values": ["item1-3"]},
                    {"question_id": "riskProfile2", "selected_values": ["item1-3"]},
                    {"question_id": "riskProfile4", "selected_values": ["item3-4"]},
                    {"question_id": "riskProfile7", "selected_values": ["item1-3"]},
                    {"question_id": "businessDrivers5", "selected_values": ["item1-2"]},
                    {"question_id": "businessDrivers11", "selected_values": ["item1-2"]},
                    {"question_id": "projectAuthority1", "selected_values": ["item1-2"]},
                    {"question_id": "aboutSystem11", "selected_values": ["item3-3"]},
                    {"question_id": "aboutAlgorithm2", "selected_values": ["item1-3"]},
                    {"question_id": "aboutAlgorithm8", "selected_values": ["item1-3"]},
                    {"question_id": "aboutAlgorithm9", "selected_values": ["item1-2"]},
                    {"question_id": "aboutAlgorithm11", "selected_values": ["item2-2"]},
                    {"question_id": "decisionSector1", "selected_values": ["item2-1"]},
                    {"question_id": "impact30", "selected_values": ["item1-4"]},
                    {"question_id": "impact3", "selected_values": ["item1-4"]},
                    {"question_id": "impact4A", "selected_values": ["item1-2"]},
                    {"question_id": "impact6", "selected_values": ["item3-3"]},
                    {"question_id": "impact7", "selected_values": ["item3-3"]},
                    {"question_id": "impact9", "selected_values": ["item3-3"]},
                    {"question_id": "impact13", "selected_values": ["item3-3"]},
                    {"question_id": "aboutDataSource1", "selected_values": ["item1-2"]},
                    {"question_id": "aboutDataSource2", "selected_values": ["item4-3"]},
                    {"question_id": "aboutDataSource3", "selected_values": ["item3-3"]},
                    {"question_id": "aboutDataSource15", "selected_values": ["item2-2"]},
                    {"question_id": "aboutDataSource16", "selected_values": ["item1-2"]},
                ],
            },
            "very_high_risk": {
                "name": "Automated Criminal Justice Risk Assessment",
                "description": "Automated system for criminal justice risk assessment that determines bail, sentencing, and parole decisions. Uses AI to analyze criminal history, demographics, and behavioral patterns to make high-stakes decisions affecting individual liberty.",
                "sample_responses": [
                    {"question_id": "riskProfile1", "selected_values": ["item1-3"]},
                    {"question_id": "riskProfile2", "selected_values": ["item1-3"]},
                    {"question_id": "riskProfile4", "selected_values": ["item4-4"]},
                    {"question_id": "riskProfile7", "selected_values": ["item1-3"]},
                    {"question_id": "businessDrivers5", "selected_values": ["item1-2"]},
                    {"question_id": "businessDrivers11", "selected_values": ["item1-2"]},
                    {"question_id": "projectAuthority1", "selected_values": ["item1-2"]},
                    {"question_id": "aboutSystem11", "selected_values": ["item4-4"]},
                    {"question_id": "aboutAlgorithm2", "selected_values": ["item1-3"]},
                    {"question_id": "aboutAlgorithm8", "selected_values": ["item1-3"]},
                    {"question_id": "aboutAlgorithm9", "selected_values": ["item1-2"]},
                    {"question_id": "aboutAlgorithm11", "selected_values": ["item2-2"]},
                    {"question_id": "decisionSector1", "selected_values": ["item8-1"]},
                    {"question_id": "impact30", "selected_values": ["item1-4"]},
                    {"question_id": "impact3", "selected_values": ["item1-4"]},
                    {"question_id": "impact4A", "selected_values": ["item1-2"]},
                    {"question_id": "impact5", "selected_values": ["item1-2"]},
                    {"question_id": "impact6", "selected_values": ["item4-4"]},
                    {"question_id": "impact7", "selected_values": ["item4-4"]},
                    {"question_id": "impact9", "selected_values": ["item4-4"]},
                    {"question_id": "impact24", "selected_values": ["item4-4"]},
                    {"question_id": "impact11", "selected_values": ["item4-4"]},
                    {"question_id": "impact13", "selected_values": ["item4-4"]},
                    {"question_id": "impact15", "selected_values": ["item4-4"]},
                    {"question_id": "impact28", "selected_values": ["item4-4"]},
                    {"question_id": "impact18", "selected_values": ["item1-3"]},
                    {"question_id": "aboutDataSource1", "selected_values": ["item1-2"]},
                    {"question_id": "aboutDataSource2", "selected_values": ["item5-4"]},
                    {"question_id": "aboutDataSource3", "selected_values": ["item3-3"]},
                    {"question_id": "aboutDataSource4", "selected_values": ["item1-2"]},
                    {"question_id": "aboutDataSource5", "selected_values": ["item1-4"]},
                    {"question_id": "aboutDataSource6", "selected_values": ["item1-4"]},
                    {"question_id": "aboutDataSource7", "selected_values": ["item4-4"]},
                    {"question_id": "aboutDataSource8", "selected_values": ["item4-4"]},
                    {"question_id": "aboutDataSource15", "selected_values": ["item2-2"]},
                    {"question_id": "aboutDataSource16", "selected_values": ["item1-2"]},
                    {"question_id": "aboutDataType2", "selected_values": ["item2-4"]},
                    {"question_id": "consultationDesign6", "selected_values": ["item1-3"]},
                    {"question_id": "consultationDesign7", "selected_values": ["item1-3"]},
                    {"question_id": "dataQualityDesign1", "selected_values": ["item2-0"]},
                ],
            },
        }

    def start_server(self):
        """Start the MCP server process."""
        print("Starting MCP server...")
        self.server_process = subprocess.Popen(
            [sys.executable, "server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_ROOT,
        )
        time.sleep(2)  # Give server time to start
        print("✅ MCP server started")

    def stop_server(self):
        """Stop the MCP server process."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            print("✅ MCP server stopped")

    def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server."""
        try:
            request_json = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()

            response_line = self.server_process.stdout.readline()
            if response_line:
                return json.loads(response_line.strip())
            else:
                return {"error": "No response from server"}
        except Exception as e:
            return {"error": f"Communication error: {str(e)}"}

    def test_initialization(self):
        """Test MCP server initialization."""
        print("\n1. Testing MCP Server Initialization...")

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        response = self.send_request(request)

        if "result" in response:
            server_info = response["result"].get("serverInfo", {})
            print(f"   ✅ Server initialized: {server_info.get('name', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Initialization failed: {response.get('error', 'Unknown error')}")
            return False

    def test_tools_list(self):
        """Test that every tool declared in the registry is actually exposed over the transport."""
        print("\n2. Testing Tools List...")

        request = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        response = self.send_request(request)

        if "result" not in response:
            print(f"   ❌ Tools list failed: {response.get('error', 'Unknown error')}")
            return False

        tools = response["result"].get("tools", [])
        returned_names = {tool["name"] for tool in tools}
        expected_names = {tool["name"] for tool in ToolRegistry.get_tools()}

        print(f"   ✅ Found {len(tools)} tools (registry declares {len(expected_names)})")

        missing = expected_names - returned_names
        extra = returned_names - expected_names
        if missing:
            print(f"   ❌ Tools declared in registry but not returned over transport: {sorted(missing)}")
        if extra:
            print(f"   ❌ Tools returned over transport but not declared in registry: {sorted(extra)}")

        return not missing and not extra

    def test_get_questions(self):
        """Test the current get_questions tool (category/type filtering)."""
        print("\n3. Testing get_questions Tool...")

        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_questions",
                "arguments": {"category": "Impact", "type": "risk"},
            },
        }

        response = self.send_request(request)

        if "result" not in response:
            print(f"   ❌ get_questions failed: {response.get('error', 'Unknown error')}")
            return False

        content = response["result"].get("content", [])
        if not content:
            print("   ❌ No content in response")
            return False

        data = json.loads(content[0]["text"])
        total_available = data.get("total_available", 0)
        questions = data.get("questions", [])
        print(f"   ✅ Impact/risk questions: {total_available} total, {len(questions)} returned")
        return total_available > 0 and len(questions) > 0

    def test_assess_project_end_to_end(self):
        """
        Smoke-test the full assess_project transport path: get_server_introduction
        (required gate) -> get_questions (fetch a live question + choice) ->
        assess_project via camelCase questionId/selectedOption. This is the only
        check that exercises server.py's index->value response conversion.
        """
        print("\n4. Testing assess_project End-to-End (introduction gate + conversion)...")

        intro_response = self.send_request({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {"name": "get_server_introduction", "arguments": {}},
        })
        if "result" not in intro_response:
            print(f"   ❌ get_server_introduction failed: {intro_response.get('error', 'Unknown error')}")
            return False

        questions_response = self.send_request({
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {"name": "get_questions", "arguments": {}},
        })
        questions_content = questions_response.get("result", {}).get("content", [])
        if not questions_content:
            print("   ❌ Could not fetch a live question to build the assess_project request")
            return False

        questions_data = json.loads(questions_content[0]["text"])
        live_questions = [q for q in questions_data.get("questions", []) if q.get("choices")]
        if not live_questions:
            print("   ❌ No question with choices available")
            return False

        question = live_questions[0]

        assess_response = self.send_request({
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "assess_project",
                "arguments": {
                    "projectName": "End-to-End Smoke Test Project",
                    "projectDescription": RICH_PROJECT_DESCRIPTION,
                    "responses": [{"questionId": question["name"], "selectedOption": 0}],
                },
            },
        })

        if "result" not in assess_response:
            print(f"   ❌ assess_project failed: {assess_response.get('error', 'Unknown error')}")
            return False

        content = assess_response["result"].get("content", [])
        if not content:
            print("   ❌ No content in assess_project response")
            return False

        assessment_data = json.loads(content[0]["text"])
        has_score = "total_score" in assessment_data
        print(f"   ✅ assess_project responded with total_score={assessment_data.get('total_score')} "
              f"(status={assessment_data.get('status')})")
        return has_score

    def test_assessment_scenarios(self):
        """
        Scoring-integrity check via direct AIAProcessor import.

        Thresholds/weights are institution-tunable proof-of-concept logic (see
        CLAUDE.md), so this asserts monotonic score/level ordering across risk
        tiers and valid bounds rather than pinning exact historical numbers.
        """
        print("\n5. Testing Assessment Scenarios (scoring integrity)...")

        processor = AIAProcessor()
        max_possible_score = sum(q["max_score"] for q in processor.scorable_questions)

        scores = []
        levels = []
        for scenario_key, scenario in self.test_scenarios.items():
            result = processor.assess_project(
                project_name=scenario["name"],
                project_description=scenario["description"],
                responses=scenario["sample_responses"],
            )
            total_score = result.get("total_score", 0)
            impact_level = result.get("impact_level", 0)
            level_name = result.get("level_name", "Unknown")
            print(f"   {scenario_key}: score={total_score}, level={impact_level} ({level_name})")

            if not (0 <= total_score <= max_possible_score):
                print(f"      ❌ Score {total_score} outside valid bounds [0, {max_possible_score}]")
                return False
            if impact_level not in (1, 2, 3, 4):
                print(f"      ❌ Impact level {impact_level} outside valid range [1, 4]")
                return False

            scores.append(total_score)
            levels.append(impact_level)

        if scores != sorted(scores):
            print(f"   ❌ Scores are not monotonically non-decreasing across risk tiers: {scores}")
            return False
        if levels != sorted(levels):
            print(f"   ❌ Impact levels are not monotonically non-decreasing across risk tiers: {levels}")
            return False

        print("   ✅ Scores and impact levels increase monotonically across low->medium->high->very_high tiers")
        return True

    def test_edge_cases(self):
        """Edge cases via direct AIAProcessor import (no MCP calculate_assessment_score tool exists)."""
        print("\n6. Testing Edge Cases...")

        processor = AIAProcessor()

        print("   Testing: No responses at all (should request questions, not fabricate a score)")
        empty_result = processor.assess_project(
            project_name="Empty Responses Edge Case",
            project_description="Edge case with no question responses provided.",
            responses=None,
        )
        empty_status = empty_result.get("status")
        empty_ok = empty_status == "questions_required" and "total_score" not in empty_result
        print(f"      Status: {empty_status}")
        print("      ✅ Edge case passed" if empty_ok else "      ❌ Edge case failed: expected status 'questions_required' with no total_score")

        print("   Testing: Minimal single low-value response")
        minimal_result = processor.assess_project(
            project_name="Minimal Response Edge Case",
            project_description="Edge case with a single minimal-value response.",
            responses=[{"question_id": "riskProfile1", "selected_values": ["item2-0"]}],
        )
        minimal_score = minimal_result.get("total_score", -1)
        minimal_ok = minimal_score == 0
        print(f"      Score: {minimal_score}")
        print("      ✅ Edge case passed" if minimal_ok else "      ❌ Edge case failed: expected score 0")

        return empty_ok and minimal_ok

    def export_sample_reports(self):
        """Export sample assessment reports for verification (into a temp dir, not the repo)."""
        print("\n7. Exporting Sample Reports...")

        try:
            processor = AIAProcessor()

            with tempfile.TemporaryDirectory() as tmp_dir:
                for scenario_key, scenario in self.test_scenarios.items():
                    assessment_report = processor.generate_assessment_report(
                        project_name=scenario["name"],
                        project_description=scenario["description"],
                        responses=scenario["sample_responses"],
                    )

                    filename = os.path.join(tmp_dir, f"sample_report_{scenario_key}.json")
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(assessment_report, f, indent=2, default=str)

                    print(f"   ✅ Exported: {filename}")

            return True

        except Exception as e:
            print(f"   ❌ Export failed: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """Run the complete test suite."""
        print("AIA Assessment MCP Server - Comprehensive Test Suite")
        print("=" * 60)

        try:
            self.start_server()

            tests = [
                ("Initialization", self.test_initialization),
                ("Tools List", self.test_tools_list),
                ("Get Questions", self.test_get_questions),
                ("Assess Project End-to-End", self.test_assess_project_end_to_end),
                ("Assessment Scenarios", self.test_assessment_scenarios),
                ("Edge Cases", self.test_edge_cases),
                ("Sample Reports Export", self.export_sample_reports),
            ]

            results = []
            for test_name, test_func in tests:
                try:
                    result = test_func()
                    results.append((test_name, result))
                except Exception as e:
                    print(f"   ❌ {test_name} crashed: {str(e)}")
                    results.append((test_name, False))

            print(f"\n{'=' * 60}")
            print("TEST SUMMARY")
            print(f"{'=' * 60}")

            passed = sum(1 for _, success in results if success)
            total = len(results)

            for test_name, success in results:
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"{test_name}: {status}")

            print(f"\nOverall: {passed}/{total} tests passed")

            if passed == total:
                print("🎉 All tests passed! MCP server is ready for Claude Desktop integration.")
            else:
                print("⚠️  Some tests failed. Check the logs for details.")

            return passed == total

        finally:
            self.stop_server()


def main():
    """Main function to run the comprehensive test suite."""
    tester = MCPServerTester()
    success = tester.run_comprehensive_test()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
