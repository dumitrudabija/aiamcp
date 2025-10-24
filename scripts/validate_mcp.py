#!/usr/bin/env python3
"""
MCP Server Validation Script for Claude Desktop Integration
Tests all aspects of the AIA Assessment MCP server before Claude Desktop integration
"""

import json
import subprocess
import sys
import time
import os
import platform
from pathlib import Path
from typing import Dict, List, Any, Optional

class MCPValidator:
    """Comprehensive validator for AIA Assessment MCP Server Claude Desktop integration."""
    
    def __init__(self):
        self.server_process = None
        self.validation_results = []
        self.current_dir = Path.cwd()
        self.python_executable = self._detect_python_executable()
        
    def _detect_python_executable(self) -> str:
        """Detect the correct Python executable for the current system."""
        candidates = ['python3', 'python', 'py']
        
        for candidate in candidates:
            try:
                result = subprocess.run([candidate, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and 'Python 3' in result.stdout:
                    return candidate
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        return 'python3'  # Default fallback
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
    
    def print_step(self, step: str, status: str = ""):
        """Print a validation step."""
        if status:
            print(f"   {step}: {status}")
        else:
            print(f"\n{step}")
    
    def validate_system_requirements(self) -> bool:
        """Validate system requirements and dependencies."""
        self.print_header("SYSTEM REQUIREMENTS VALIDATION")
        
        results = []
        
        # Check Python version
        try:
            result = subprocess.run([self.python_executable, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                self.print_step(f"Python version", f"✅ {version}")
                results.append(True)
            else:
                self.print_step("Python version", "❌ Failed to get version")
                results.append(False)
        except Exception as e:
            self.print_step("Python version", f"❌ Error: {str(e)}")
            results.append(False)
        
        # Check required files
        required_files = ['server.py', 'aia_processor.py', 'config.json', 'data/survey-enfr.json']
        for file_path in required_files:
            if Path(file_path).exists():
                self.print_step(f"Required file: {file_path}", "✅ Found")
                results.append(True)
            else:
                self.print_step(f"Required file: {file_path}", "❌ Missing")
                results.append(False)
        
        # Check Python dependencies
        required_packages = ['json', 'sys', 'pathlib', 'typing']
        for package in required_packages:
            try:
                result = subprocess.run([self.python_executable, '-c', f'import {package}'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.print_step(f"Python package: {package}", "✅ Available")
                    results.append(True)
                else:
                    self.print_step(f"Python package: {package}", "❌ Missing")
                    results.append(False)
            except Exception as e:
                self.print_step(f"Python package: {package}", f"❌ Error: {str(e)}")
                results.append(False)
        
        # Check working directory permissions
        try:
            test_file = Path("test_permissions.tmp")
            test_file.write_text("test")
            test_file.unlink()
            self.print_step("Directory permissions", "✅ Read/Write access")
            results.append(True)
        except Exception as e:
            self.print_step("Directory permissions", f"❌ Error: {str(e)}")
            results.append(False)
        
        return all(results)
    
    def validate_server_startup(self) -> bool:
        """Validate that the MCP server starts correctly."""
        self.print_header("MCP SERVER STARTUP VALIDATION")
        
        try:
            self.print_step("Starting MCP server process...")
            self.server_process = subprocess.Popen(
                [self.python_executable, "server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.current_dir)
            )
            
            # Give server time to start
            time.sleep(3)
            
            # Check if process is still running
            if self.server_process.poll() is None:
                self.print_step("Server process status", "✅ Running")
                return True
            else:
                stderr_output = self.server_process.stderr.read()
                self.print_step("Server process status", f"❌ Crashed: {stderr_output}")
                return False
                
        except Exception as e:
            self.print_step("Server startup", f"❌ Error: {str(e)}")
            return False
    
    def send_json_rpc_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a JSON-RPC request to the server."""
        try:
            request_json = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()
            
            # Read response with timeout
            response_line = self.server_process.stdout.readline()
            if response_line:
                return json.loads(response_line.strip())
            else:
                return None
        except Exception as e:
            return {"error": f"Communication error: {str(e)}"}
    
    def validate_json_rpc_communication(self) -> bool:
        """Validate JSON-RPC communication with the server."""
        self.print_header("JSON-RPC COMMUNICATION VALIDATION")
        
        if not self.server_process or self.server_process.poll() is not None:
            self.print_step("Server availability", "❌ Server not running")
            return False
        
        # Test initialization
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "validation-client", "version": "1.0.0"}
            }
        }
        
        response = self.send_json_rpc_request(init_request)
        if response and "result" in response:
            server_info = response["result"].get("serverInfo", {})
            self.print_step("Server initialization", f"✅ {server_info.get('name', 'Unknown')}")
        else:
            self.print_step("Server initialization", f"❌ Failed: {response}")
            return False
        
        # Test tools list
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = self.send_json_rpc_request(tools_request)
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            self.print_step("Tools discovery", f"✅ Found {len(tools)} tools")
            for tool in tools:
                self.print_step(f"  - Tool: {tool['name']}", "✅ Available")
        else:
            self.print_step("Tools discovery", f"❌ Failed: {response}")
            return False
        
        return True
    
    def validate_tool_functionality(self) -> bool:
        """Validate that all 4 MCP tools work correctly."""
        self.print_header("TOOL FUNCTIONALITY VALIDATION")
        
        if not self.server_process or self.server_process.poll() is not None:
            self.print_step("Server availability", "❌ Server not running")
            return False
        
        tool_tests = [
            {
                "name": "get_questions_summary",
                "args": {},
                "expected_keys": ["summary"]
            },
            {
                "name": "get_questions_by_category", 
                "args": {"category": "technical", "limit": 3},
                "expected_keys": ["category", "questions"]
            },
            {
                "name": "calculate_assessment_score",
                "args": {
                    "responses": [
                        {"question_id": "riskProfile1", "selected_values": ["item2-0"]},
                        {"question_id": "businessDrivers9", "selected_values": ["item1-0"]}
                    ]
                },
                "expected_keys": ["calculation"]
            },
            {
                "name": "assess_project",
                "args": {
                    "project_name": "Test Project",
                    "project_description": "Simple test project for validation",
                    "responses": [
                        {"question_id": "riskProfile1", "selected_values": ["item2-0"]},
                        {"question_id": "businessDrivers9", "selected_values": ["item1-0"]}
                    ]
                },
                "expected_keys": ["assessment"]
            }
        ]
        
        results = []
        
        for test in tool_tests:
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": test["name"],
                    "arguments": test["args"]
                }
            }
            
            response = self.send_json_rpc_request(request)
            
            if response and "result" in response:
                content = response["result"].get("content", [])
                if content:
                    try:
                        data = json.loads(content[0]["text"])
                        has_expected_keys = all(key in data for key in test["expected_keys"])
                        if has_expected_keys:
                            self.print_step(f"Tool: {test['name']}", "✅ Working")
                            results.append(True)
                        else:
                            self.print_step(f"Tool: {test['name']}", f"❌ Missing keys: {test['expected_keys']}")
                            results.append(False)
                    except json.JSONDecodeError:
                        self.print_step(f"Tool: {test['name']}", "❌ Invalid JSON response")
                        results.append(False)
                else:
                    self.print_step(f"Tool: {test['name']}", "❌ No content in response")
                    results.append(False)
            else:
                self.print_step(f"Tool: {test['name']}", f"❌ Failed: {response}")
                results.append(False)
        
        return all(results)
    
    def validate_claude_desktop_config(self) -> bool:
        """Validate Claude Desktop configuration files."""
        self.print_header("CLAUDE DESKTOP CONFIGURATION VALIDATION")
        
        results = []
        
        # Check configuration files exist
        config_files = [
            "claude_desktop_config.json",
            "claude_desktop_config_windows.json", 
            "claude_desktop_config_linux.json"
        ]
        
        for config_file in config_files:
            if Path(config_file).exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    # Validate structure
                    if "mcpServers" in config and "aia-assessment" in config["mcpServers"]:
                        server_config = config["mcpServers"]["aia-assessment"]
                        required_keys = ["command", "args", "cwd"]
                        
                        if all(key in server_config for key in required_keys):
                            self.print_step(f"Config file: {config_file}", "✅ Valid structure")
                            results.append(True)
                        else:
                            self.print_step(f"Config file: {config_file}", "❌ Missing required keys")
                            results.append(False)
                    else:
                        self.print_step(f"Config file: {config_file}", "❌ Invalid structure")
                        results.append(False)
                        
                except json.JSONDecodeError:
                    self.print_step(f"Config file: {config_file}", "❌ Invalid JSON")
                    results.append(False)
            else:
                self.print_step(f"Config file: {config_file}", "❌ Missing")
                results.append(False)
        
        # Validate paths in current system config
        current_config = "claude_desktop_config.json"
        if Path(current_config).exists():
            try:
                with open(current_config, 'r') as f:
                    config = json.load(f)
                
                server_config = config["mcpServers"]["aia-assessment"]
                cwd_path = Path(server_config["cwd"])
                
                if cwd_path.exists():
                    self.print_step("Working directory path", "✅ Exists")
                    results.append(True)
                else:
                    self.print_step("Working directory path", f"❌ Not found: {cwd_path}")
                    results.append(False)
                    
            except Exception as e:
                self.print_step("Path validation", f"❌ Error: {str(e)}")
                results.append(False)
        
        return all(results)
    
    def cleanup(self):
        """Clean up server process."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.print_step("Server cleanup", "✅ Stopped")
    
    def run_full_validation(self) -> bool:
        """Run the complete validation suite."""
        self.print_header("AIA ASSESSMENT MCP SERVER - CLAUDE DESKTOP VALIDATION")
        print(f"System: {platform.system()} {platform.release()}")
        print(f"Python: {self.python_executable}")
        print(f"Working Directory: {self.current_dir}")
        
        try:
            # Run all validation steps
            validations = [
                ("System Requirements", self.validate_system_requirements),
                ("Server Startup", self.validate_server_startup),
                ("JSON-RPC Communication", self.validate_json_rpc_communication),
                ("Tool Functionality", self.validate_tool_functionality),
                ("Claude Desktop Config", self.validate_claude_desktop_config)
            ]
            
            results = []
            for name, validation_func in validations:
                try:
                    result = validation_func()
                    results.append((name, result))
                except Exception as e:
                    self.print_step(f"{name} validation", f"❌ Crashed: {str(e)}")
                    results.append((name, False))
            
            # Summary
            self.print_header("VALIDATION SUMMARY")
            
            passed = sum(1 for _, success in results if success)
            total = len(results)
            
            for name, success in results:
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"{name}: {status}")
            
            print(f"\nOverall: {passed}/{total} validations passed")
            
            if passed == total:
                print("\n🎉 ALL VALIDATIONS PASSED!")
                print("✅ MCP server is ready for Claude Desktop integration")
                print("\nNext steps:")
                print("1. Copy the appropriate claude_desktop_config_*.json to your Claude Desktop settings")
                print("2. Restart Claude Desktop")
                print("3. Test the integration using the conversation templates")
                return True
            else:
                print("\n⚠️  SOME VALIDATIONS FAILED!")
                print("❌ Fix the issues above before proceeding with Claude Desktop integration")
                return False
                
        finally:
            self.cleanup()

def main():
    """Main function to run the validation suite."""
    validator = MCPValidator()
    success = validator.run_full_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
