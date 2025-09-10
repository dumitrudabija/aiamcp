#!/usr/bin/env python3
"""
Comprehensive MCP Server Test Suite
Tests all MCP tools with different risk scenarios and validates scoring logic
"""

import json
import subprocess
import sys
import time
from typing import Dict, List, Any

class MCPServerTester:
    """Comprehensive tester for AIA Assessment MCP Server."""
    
    def __init__(self):
        self.server_process = None
        self.test_results = []
        
        # Test scenarios with expected outcomes based on actual survey analysis
        self.test_scenarios = {
            "low_risk": {
                "name": "Simple Internal File Organization Tool",
                "description": "Simple internal file organization tool with no user data. Helps employees organize documents in shared folders with basic categorization features.",
                "expected_level": 1,
                "expected_score_range": (0, 30),
                "sample_responses": [
                    {"question_id": "businessDrivers9", "selected_values": ["item1-0"]},  # Alternatives considered (0 pts)
                    {"question_id": "riskProfile1", "selected_values": ["item2-0"]},  # No public scrutiny (0 pts)
                    {"question_id": "riskProfile2", "selected_values": ["item2-0"]},  # No equity groups (0 pts)
                    {"question_id": "riskProfile4", "selected_values": ["item1-0"]},  # Accessibility assessed (0 pts)
                    {"question_id": "aboutSystem3", "selected_values": ["item1-0"]},  # Your institution (0 pts)
                    {"question_id": "aboutSystem11", "selected_values": ["item1-1"]},  # Little environmental impact (1 pt)
                    {"question_id": "impact30", "selected_values": ["item2-2"]},  # Partial automation (2 pts)
                    {"question_id": "impact3", "selected_values": ["item2-0"]},  # No judgment required (0 pts)
                    {"question_id": "aboutDataSource1", "selected_values": ["item2-0"]},  # No personal info (0 pts)
                ]
            },
            "medium_risk": {
                "name": "Customer FAQ Chatbot",
                "description": "Customer FAQ chatbot using company knowledge base. Provides automated responses to common customer questions about products and services using natural language processing.",
                "expected_level": 2,
                "expected_score_range": (31, 55),
                "sample_responses": [
                    {"question_id": "businessDrivers5", "selected_values": ["item1-2"]},  # Slightly effective (2 pts)
                    {"question_id": "businessDrivers9", "selected_values": ["item1-0"]},  # Alternatives considered (0 pts)
                    {"question_id": "businessDrivers11", "selected_values": ["item1-2"]},  # Service cannot be delivered (2 pts)
                    {"question_id": "projectAuthority1", "selected_values": ["item1-2"]},  # New authority needed (2 pts)
                    {"question_id": "aboutSystem5", "selected_values": ["item3-2"]},  # COTS (2 pts)
                    {"question_id": "aboutSystem6", "selected_values": ["item2-2"]},  # No accountability (2 pts)
                    {"question_id": "aboutSystem7", "selected_values": ["item2-2"]},  # No improvement group (2 pts)
                    {"question_id": "aboutSystem11", "selected_values": ["item2-2"]},  # Moderate environmental impact (2 pts)
                    {"question_id": "aboutAlgorithm2", "selected_values": ["item1-3"]},  # Difficult to interpret (3 pts)
                    {"question_id": "aboutAlgorithm8", "selected_values": ["item1-3"]},  # Continues learning (3 pts)
                    {"question_id": "impact30", "selected_values": ["item2-2"]},  # Partial automation (2 pts)
                    {"question_id": "impact3", "selected_values": ["item2-0"]},  # No judgment (0 pts)
                    {"question_id": "impact4A", "selected_values": ["item1-2"]},  # Major staff impact (2 pts)
                    {"question_id": "impact6", "selected_values": ["item2-2"]},  # Likely reversible (2 pts)
                    {"question_id": "impact7", "selected_values": ["item2-2"]},  # Months duration (2 pts)
                    {"question_id": "impact9", "selected_values": ["item2-2"]},  # Moderate rights impact (2 pts)
                    {"question_id": "aboutDataSource1", "selected_values": ["item1-2"]},  # Uses personal info (2 pts)
                    {"question_id": "aboutDataSource15", "selected_values": ["item2-2"]},  # Data not representative (2 pts)
                ]
            },
            "high_risk": {
                "name": "AI Loan Recommendation System",
                "description": "AI loan recommendation system using customer financial data. Analyzes credit history, income, and financial behavior to provide loan approval recommendations to human underwriters.",
                "expected_level": 3,
                "expected_score_range": (56, 75),
                "sample_responses": [
                    {"question_id": "riskProfile1", "selected_values": ["item1-3"]},  # Public scrutiny (3 pts)
                    {"question_id": "riskProfile2", "selected_values": ["item1-3"]},  # Equity groups (3 pts)
                    {"question_id": "riskProfile4", "selected_values": ["item3-4"]},  # Barriers identified, no measures (4 pts)
                    {"question_id": "riskProfile7", "selected_values": ["item1-3"]},  # Exploitation target (3 pts)
                    {"question_id": "businessDrivers5", "selected_values": ["item1-2"]},  # Slightly effective (2 pts)
                    {"question_id": "businessDrivers11", "selected_values": ["item1-2"]},  # Service cannot be delivered (2 pts)
                    {"question_id": "projectAuthority1", "selected_values": ["item1-2"]},  # New authority needed (2 pts)
                    {"question_id": "aboutSystem11", "selected_values": ["item3-3"]},  # High environmental impact (3 pts)
                    {"question_id": "aboutAlgorithm2", "selected_values": ["item1-3"]},  # Difficult to interpret (3 pts)
                    {"question_id": "aboutAlgorithm8", "selected_values": ["item1-3"]},  # Continues learning (3 pts)
                    {"question_id": "aboutAlgorithm9", "selected_values": ["item1-2"]},  # Uses protected characteristics (2 pts)
                    {"question_id": "aboutAlgorithm11", "selected_values": ["item2-2"]},  # No proxy evaluation (2 pts)
                    {"question_id": "decisionSector1", "selected_values": ["item2-1"]},  # Economic interests (1 pt)
                    {"question_id": "impact30", "selected_values": ["item1-4"]},  # Full automation (4 pts)
                    {"question_id": "impact3", "selected_values": ["item1-4"]},  # Requires judgment (4 pts)
                    {"question_id": "impact4A", "selected_values": ["item1-2"]},  # Major staff impact (2 pts)
                    {"question_id": "impact6", "selected_values": ["item3-3"]},  # Difficult to reverse (3 pts)
                    {"question_id": "impact7", "selected_values": ["item3-3"]},  # Years duration (3 pts)
                    {"question_id": "impact9", "selected_values": ["item3-3"]},  # High rights impact (3 pts)
                    {"question_id": "impact13", "selected_values": ["item3-3"]},  # High economic impact (3 pts)
                    {"question_id": "aboutDataSource1", "selected_values": ["item1-2"]},  # Uses personal info (2 pts)
                    {"question_id": "aboutDataSource2", "selected_values": ["item4-3"]},  # Protected B (3 pts)
                    {"question_id": "aboutDataSource3", "selected_values": ["item3-3"]},  # Private sector controls (3 pts)
                    {"question_id": "aboutDataSource15", "selected_values": ["item2-2"]},  # Data not representative (2 pts)
                    {"question_id": "aboutDataSource16", "selected_values": ["item1-2"]},  # Biases present (2 pts)
                ]
            },
            "very_high_risk": {
                "name": "Automated Criminal Justice Risk Assessment",
                "description": "Automated system for criminal justice risk assessment that determines bail, sentencing, and parole decisions. Uses AI to analyze criminal history, demographics, and behavioral patterns to make high-stakes decisions affecting individual liberty.",
                "expected_level": 4,
                "expected_score_range": (76, 999),
                "sample_responses": [
                    {"question_id": "riskProfile1", "selected_values": ["item1-3"]},  # Public scrutiny (3 pts)
                    {"question_id": "riskProfile2", "selected_values": ["item1-3"]},  # Equity groups (3 pts)
                    {"question_id": "riskProfile4", "selected_values": ["item4-4"]},  # No accessibility assessment (4 pts)
                    {"question_id": "riskProfile7", "selected_values": ["item1-3"]},  # Exploitation target (3 pts)
                    {"question_id": "businessDrivers5", "selected_values": ["item1-2"]},  # Slightly effective (2 pts)
                    {"question_id": "businessDrivers11", "selected_values": ["item1-2"]},  # Service cannot be delivered (2 pts)
                    {"question_id": "projectAuthority1", "selected_values": ["item1-2"]},  # New authority needed (2 pts)
                    {"question_id": "aboutSystem11", "selected_values": ["item4-4"]},  # Very high environmental impact (4 pts)
                    {"question_id": "aboutAlgorithm2", "selected_values": ["item1-3"]},  # Difficult to interpret (3 pts)
                    {"question_id": "aboutAlgorithm8", "selected_values": ["item1-3"]},  # Continues learning (3 pts)
                    {"question_id": "aboutAlgorithm9", "selected_values": ["item1-2"]},  # Uses protected characteristics (2 pts)
                    {"question_id": "aboutAlgorithm11", "selected_values": ["item2-2"]},  # No proxy evaluation (2 pts)
                    {"question_id": "decisionSector1", "selected_values": ["item8-1"]},  # Public safety/law enforcement (1 pt)
                    {"question_id": "impact30", "selected_values": ["item1-4"]},  # Full automation (4 pts)
                    {"question_id": "impact3", "selected_values": ["item1-4"]},  # Requires judgment (4 pts)
                    {"question_id": "impact4A", "selected_values": ["item1-2"]},  # Major staff impact (2 pts)
                    {"question_id": "impact5", "selected_values": ["item1-2"]},  # Different org uses (2 pts)
                    {"question_id": "impact6", "selected_values": ["item4-4"]},  # Irreversible (4 pts)
                    {"question_id": "impact7", "selected_values": ["item4-4"]},  # Perpetual impacts (4 pts)
                    {"question_id": "impact9", "selected_values": ["item4-4"]},  # Very high rights impact (4 pts)
                    {"question_id": "impact24", "selected_values": ["item4-4"]},  # Very high dignity impact (4 pts)
                    {"question_id": "impact11", "selected_values": ["item4-4"]},  # Very high health impact (4 pts)
                    {"question_id": "impact13", "selected_values": ["item4-4"]},  # Very high economic impact (4 pts)
                    {"question_id": "impact15", "selected_values": ["item4-4"]},  # Very high environmental impact (4 pts)
                    {"question_id": "impact28", "selected_values": ["item4-4"]},  # Very high wrongful impact (4 pts)
                    {"question_id": "impact18", "selected_values": ["item1-3"]},  # No assessment conducted (3 pts)
                    {"question_id": "aboutDataSource1", "selected_values": ["item1-2"]},  # Uses personal info (2 pts)
                    {"question_id": "aboutDataSource2", "selected_values": ["item5-4"]},  # Secret classification (4 pts)
                    {"question_id": "aboutDataSource3", "selected_values": ["item3-3"]},  # Private sector controls (3 pts)
                    {"question_id": "aboutDataSource4", "selected_values": ["item1-2"]},  # Multiple sources (2 pts)
                    {"question_id": "aboutDataSource5", "selected_values": ["item1-4"]},  # Network devices (4 pts)
                    {"question_id": "aboutDataSource6", "selected_values": ["item1-4"]},  # Interfaces with IT (4 pts)
                    {"question_id": "aboutDataSource7", "selected_values": ["item4-4"]},  # Foreign/third party collected training (4 pts)
                    {"question_id": "aboutDataSource8", "selected_values": ["item4-4"]},  # Foreign/third party collected input (4 pts)
                    {"question_id": "aboutDataSource15", "selected_values": ["item2-2"]},  # Data not representative (2 pts)
                    {"question_id": "aboutDataSource16", "selected_values": ["item1-2"]},  # Biases present (2 pts)
                    {"question_id": "aboutDataType2", "selected_values": ["item2-4"]},  # Images and videos (4 pts)
                    {"question_id": "consultationDesign6", "selected_values": ["item1-3"]},  # Will consult impacted (3 pts)
                    {"question_id": "consultationDesign7", "selected_values": ["item1-3"]},  # Will consult adversely impacted (3 pts)
                    {"question_id": "dataQualityDesign1", "selected_values": ["item2-0"]},  # No bias testing (0 pts)
                ]
            }
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
            cwd="."
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
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
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
        """Test listing available tools."""
        print("\n2. Testing Tools List...")
        
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = self.send_request(request)
        
        if "result" in response:
            tools = response["result"].get("tools", [])
            print(f"   ✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"      - {tool['name']}")
            return len(tools) == 4  # Expected 4 tools
        else:
            print(f"   ❌ Tools list failed: {response.get('error', 'Unknown error')}")
            return False
    
    def test_questions_summary(self):
        """Test get_questions_summary tool."""
        print("\n3. Testing Questions Summary Tool...")
        
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_questions_summary",
                "arguments": {}
            }
        }
        
        response = self.send_request(request)
        
        if "result" in response:
            content = response["result"].get("content", [])
            if content:
                summary_data = json.loads(content[0]["text"])
                summary = summary_data.get("summary", {})
                print(f"   ✅ Questions summary retrieved:")
                print(f"      - Framework: {summary.get('framework_name', 'Unknown')}")
                print(f"      - Total questions: {summary.get('total_questions', 0)}")
                print(f"      - Max score: {summary.get('max_possible_score', 0)}")
                return summary.get("total_questions", 0) == 162
            else:
                print("   ❌ No content in response")
                return False
        else:
            print(f"   ❌ Questions summary failed: {response.get('error', 'Unknown error')}")
            return False
    
    def test_questions_by_category(self):
        """Test get_questions_by_category tool."""
        print("\n4. Testing Questions by Category Tool...")
        
        categories = ["technical", "impact_risk", "manual"]
        results = []
        
        for category in categories:
            request = {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "get_questions_by_category",
                    "arguments": {
                        "category": category,
                        "limit": 5
                    }
                }
            }
            
            response = self.send_request(request)
            
            if "result" in response:
                content = response["result"].get("content", [])
                if content:
                    category_data = json.loads(content[0]["text"])
                    total_in_category = category_data.get("total_in_category", 0)
                    returned_count = category_data.get("returned_count", 0)
                    print(f"   ✅ {category.title()} questions: {total_in_category} total, {returned_count} returned")
                    results.append(total_in_category > 0)
                else:
                    print(f"   ❌ No content for {category}")
                    results.append(False)
            else:
                print(f"   ❌ {category} failed: {response.get('error', 'Unknown error')}")
                results.append(False)
        
        return all(results)
    
    def test_assessment_scenarios(self):
        """Test assessment scenarios with different risk levels."""
        print("\n5. Testing Assessment Scenarios...")
        
        scenario_results = []
        
        for scenario_key, scenario in self.test_scenarios.items():
            print(f"\n   Testing {scenario_key.upper()} scenario: {scenario['name']}")
            
            # Test assess_project tool
            request = {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "assess_project",
                    "arguments": {
                        "project_name": scenario["name"],
                        "project_description": scenario["description"],
                        "responses": scenario["sample_responses"]
                    }
                }
            }
            
            response = self.send_request(request)
            
            if "result" in response:
                content = response["result"].get("content", [])
                if content:
                    assessment_data = json.loads(content[0]["text"])
                    assessment = assessment_data.get("assessment", {})
                    
                    total_score = assessment.get("total_score", 0)
                    impact_level = assessment.get("impact_level", 0)
                    level_name = assessment.get("level_name", "Unknown")
                    
                    print(f"      Score: {total_score}")
                    print(f"      Impact Level: {impact_level} - {level_name}")
                    
                    # Validate results
                    expected_min, expected_max = scenario["expected_score_range"]
                    score_valid = expected_min <= total_score <= expected_max
                    level_valid = impact_level == scenario["expected_level"]
                    
                    if score_valid and level_valid:
                        print(f"      ✅ Scenario validation passed")
                        scenario_results.append(True)
                    else:
                        print(f"      ❌ Scenario validation failed")
                        print(f"         Expected score: {expected_min}-{expected_max}, got: {total_score}")
                        print(f"         Expected level: {scenario['expected_level']}, got: {impact_level}")
                        scenario_results.append(False)
                else:
                    print(f"      ❌ No content in response")
                    scenario_results.append(False)
            else:
                print(f"      ❌ Assessment failed: {response.get('error', 'Unknown error')}")
                scenario_results.append(False)
        
        return all(scenario_results)
    
    def test_edge_cases(self):
        """Test edge cases with extreme scoring scenarios."""
        print("\n6. Testing Edge Cases...")
        
        edge_cases = [
            {
                "name": "All Minimum Scores",
                "responses": [
                    {"question_id": "riskProfile1", "selected_values": ["item2-0"]},
                    {"question_id": "riskProfile2", "selected_values": ["item2-0"]},
                    {"question_id": "businessDrivers9", "selected_values": ["item1-0"]},
                ],
                "expected_score": 0,
                "expected_level": 1
            },
            {
                "name": "All Maximum Scores",
                "responses": [
                    {"question_id": "riskProfile1", "selected_values": ["item1-3"]},
                    {"question_id": "riskProfile2", "selected_values": ["item1-3"]},
                    {"question_id": "riskProfile4", "selected_values": ["item4-4"]},
                    {"question_id": "impact4A", "selected_values": ["item1-2"]},
                ],
                "expected_score": 12,  # 3+3+4+2 = 12 (actual test result)
                "expected_level": 1  # Still level 1 with just 4 questions
            }
        ]
        
        edge_results = []
        
        for case in edge_cases:
            print(f"   Testing: {case['name']}")
            
            request = {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "calculate_assessment_score",
                    "arguments": {
                        "responses": case["responses"]
                    }
                }
            }
            
            response = self.send_request(request)
            
            if "result" in response:
                content = response["result"].get("content", [])
                if content:
                    calc_data = json.loads(content[0]["text"])
                    calculation = calc_data.get("calculation", {})
                    
                    total_score = calculation.get("total_score", 0)
                    impact_level = calculation.get("impact_level", 0)
                    
                    print(f"      Score: {total_score}, Level: {impact_level}")
                    
                    score_valid = total_score == case["expected_score"]
                    level_valid = impact_level == case["expected_level"]
                    
                    if score_valid and level_valid:
                        print(f"      ✅ Edge case passed")
                        edge_results.append(True)
                    else:
                        print(f"      ❌ Edge case failed")
                        edge_results.append(False)
                else:
                    print(f"      ❌ No content in response")
                    edge_results.append(False)
            else:
                print(f"      ❌ Calculation failed: {response.get('error', 'Unknown error')}")
                edge_results.append(False)
        
        return all(edge_results)
    
    def export_sample_reports(self):
        """Export sample assessment reports for verification."""
        print("\n7. Exporting Sample Reports...")
        
        try:
            from aia_processor import AIAProcessor
            processor = AIAProcessor()
            
            for scenario_key, scenario in self.test_scenarios.items():
                # Generate assessment report
                assessment_report = processor.generate_assessment_report(
                    project_name=scenario["name"],
                    project_description=scenario["description"],
                    responses=scenario["sample_responses"]
                )
                
                # Export to JSON
                json_export = processor.export_assessment_json(assessment_report)
                
                # Save to file
                filename = f"sample_report_{scenario_key}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(json_export)
                
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
            
            # Run all tests
            tests = [
                ("Initialization", self.test_initialization),
                ("Tools List", self.test_tools_list),
                ("Questions Summary", self.test_questions_summary),
                ("Questions by Category", self.test_questions_by_category),
                ("Assessment Scenarios", self.test_assessment_scenarios),
                ("Edge Cases", self.test_edge_cases),
                ("Sample Reports Export", self.export_sample_reports)
            ]
            
            results = []
            for test_name, test_func in tests:
                try:
                    result = test_func()
                    results.append((test_name, result))
                except Exception as e:
                    print(f"   ❌ {test_name} crashed: {str(e)}")
                    results.append((test_name, False))
            
            # Summary
            print(f"\n{'='*60}")
            print("TEST SUMMARY")
            print(f"{'='*60}")
            
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
