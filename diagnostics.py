#!/usr/bin/env python3
"""
Comprehensive Diagnostics and Troubleshooting for AIA Assessment MCP Server
Provides detailed analysis of system health, performance, and common issues
"""

import json
import subprocess
import sys
import time
import os
import platform
import psutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class AIADiagnostics:
    """Comprehensive diagnostics for AIA Assessment MCP Server."""
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.log_file = self.current_dir / "diagnostics.log"
        self.setup_logging()
        self.server_process = None
        self.performance_metrics = {}
        
    def setup_logging(self):
        """Setup detailed logging for diagnostics."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{'='*70}")
        print(f"{title}")
        print(f"{'='*70}")
        self.logger.info(f"Starting: {title}")
    
    def print_section(self, title: str):
        """Print a section header."""
        print(f"\n{'-'*50}")
        print(f"{title}")
        print(f"{'-'*50}")
    
    def print_result(self, test: str, status: str, details: str = ""):
        """Print a test result."""
        status_icon = "✅" if "PASS" in status else "❌" if "FAIL" in status else "⚠️"
        print(f"   {status_icon} {test}: {status}")
        if details:
            print(f"      {details}")
        self.logger.info(f"{test}: {status} - {details}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Collect comprehensive system information."""
        self.print_header("SYSTEM INFORMATION COLLECTION")
        
        info = {
            "timestamp": datetime.now().isoformat(),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
                "executable": sys.executable
            },
            "resources": {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "disk_free": psutil.disk_usage('.').free
            },
            "environment": {
                "cwd": str(self.current_dir),
                "pythonpath": os.environ.get("PYTHONPATH", "Not set"),
                "path": os.environ.get("PATH", "")[:200] + "..."
            }
        }
        
        # Display key information
        print(f"System: {info['platform']['system']} {info['platform']['release']}")
        print(f"Python: {info['python']['version']} ({info['python']['implementation']})")
        print(f"CPU Cores: {info['resources']['cpu_count']}")
        print(f"Memory: {info['resources']['memory_available'] / (1024**3):.1f}GB available")
        print(f"Working Directory: {info['environment']['cwd']}")
        
        return info
    
    def diagnose_file_system(self) -> Dict[str, Any]:
        """Diagnose file system issues."""
        self.print_section("FILE SYSTEM DIAGNOSTICS")
        
        results = {"status": "PASS", "issues": [], "files": {}}
        
        # Check required files
        required_files = [
            "server.py",
            "aia_processor.py", 
            "config.json",
            "data/survey-enfr.json",
            "claude_desktop_config.json",
            "validate_mcp.py"
        ]
        
        for file_path in required_files:
            path = Path(file_path)
            if path.exists():
                stat = path.stat()
                results["files"][file_path] = {
                    "exists": True,
                    "size": stat.st_size,
                    "readable": os.access(path, os.R_OK),
                    "writable": os.access(path, os.W_OK),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
                self.print_result(f"File: {file_path}", "PASS", 
                                f"Size: {stat.st_size} bytes, Modified: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')}")
            else:
                results["files"][file_path] = {"exists": False}
                results["issues"].append(f"Missing file: {file_path}")
                results["status"] = "FAIL"
                self.print_result(f"File: {file_path}", "FAIL", "File not found")
        
        # Check directory permissions
        try:
            test_file = Path("diagnostic_test.tmp")
            test_file.write_text("test")
            test_file.unlink()
            self.print_result("Directory permissions", "PASS", "Read/write access confirmed")
        except Exception as e:
            results["issues"].append(f"Directory permission error: {str(e)}")
            results["status"] = "FAIL"
            self.print_result("Directory permissions", "FAIL", str(e))
        
        return results
    
    def diagnose_python_environment(self) -> Dict[str, Any]:
        """Diagnose Python environment issues."""
        self.print_section("PYTHON ENVIRONMENT DIAGNOSTICS")
        
        results = {"status": "PASS", "issues": [], "packages": {}}
        
        # Check Python version
        python_version = platform.python_version_tuple()
        if int(python_version[0]) >= 3 and int(python_version[1]) >= 7:
            self.print_result("Python version", "PASS", f"Python {platform.python_version()}")
        else:
            results["issues"].append(f"Python version too old: {platform.python_version()}")
            results["status"] = "FAIL"
            self.print_result("Python version", "FAIL", f"Need Python 3.7+, got {platform.python_version()}")
        
        # Check required packages
        required_packages = ["json", "sys", "pathlib", "typing", "subprocess", "time"]
        for package in required_packages:
            try:
                __import__(package)
                results["packages"][package] = {"available": True}
                self.print_result(f"Package: {package}", "PASS")
            except ImportError as e:
                results["packages"][package] = {"available": False, "error": str(e)}
                results["issues"].append(f"Missing package: {package}")
                results["status"] = "FAIL"
                self.print_result(f"Package: {package}", "FAIL", str(e))
        
        # Check optional packages
        optional_packages = ["psutil"]
        for package in optional_packages:
            try:
                __import__(package)
                results["packages"][package] = {"available": True, "optional": True}
                self.print_result(f"Optional package: {package}", "PASS")
            except ImportError:
                results["packages"][package] = {"available": False, "optional": True}
                self.print_result(f"Optional package: {package}", "WARN", "Not installed (optional)")
        
        return results
    
    def diagnose_server_startup(self) -> Dict[str, Any]:
        """Diagnose server startup issues."""
        self.print_section("SERVER STARTUP DIAGNOSTICS")
        
        results = {"status": "PASS", "issues": [], "startup_time": None, "process_info": {}}
        
        try:
            # Start server process
            start_time = time.time()
            self.server_process = subprocess.Popen(
                [sys.executable, "server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.current_dir)
            )
            
            # Wait for startup
            time.sleep(3)
            startup_time = time.time() - start_time
            results["startup_time"] = startup_time
            
            # Check if process is running
            if self.server_process.poll() is None:
                results["process_info"] = {
                    "pid": self.server_process.pid,
                    "running": True,
                    "startup_time": startup_time
                }
                self.print_result("Server startup", "PASS", f"Started in {startup_time:.2f}s, PID: {self.server_process.pid}")
            else:
                # Process crashed
                stderr_output = self.server_process.stderr.read()
                stdout_output = self.server_process.stdout.read()
                results["issues"].append(f"Server crashed on startup: {stderr_output}")
                results["status"] = "FAIL"
                results["process_info"] = {
                    "running": False,
                    "stderr": stderr_output,
                    "stdout": stdout_output,
                    "return_code": self.server_process.returncode
                }
                self.print_result("Server startup", "FAIL", f"Process crashed: {stderr_output}")
                
        except Exception as e:
            results["issues"].append(f"Failed to start server: {str(e)}")
            results["status"] = "FAIL"
            self.print_result("Server startup", "FAIL", str(e))
        
        return results
    
    def diagnose_communication(self) -> Dict[str, Any]:
        """Diagnose JSON-RPC communication issues."""
        self.print_section("COMMUNICATION DIAGNOSTICS")
        
        results = {"status": "PASS", "issues": [], "response_times": {}, "responses": {}}
        
        if not self.server_process or self.server_process.poll() is not None:
            results["issues"].append("Server not running")
            results["status"] = "FAIL"
            self.print_result("Server availability", "FAIL", "Server process not running")
            return results
        
        # Test initialization
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "diagnostic-client", "version": "1.0.0"}
            }
        }
        
        start_time = time.time()
        response = self._send_request(init_request)
        response_time = time.time() - start_time
        results["response_times"]["initialize"] = response_time
        
        if response and "result" in response:
            results["responses"]["initialize"] = response
            self.print_result("Initialization", "PASS", f"Response time: {response_time:.3f}s")
        else:
            results["issues"].append(f"Initialization failed: {response}")
            results["status"] = "FAIL"
            self.print_result("Initialization", "FAIL", f"Bad response: {response}")
            return results
        
        # Test tools list
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        start_time = time.time()
        response = self._send_request(tools_request)
        response_time = time.time() - start_time
        results["response_times"]["tools_list"] = response_time
        
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            results["responses"]["tools_list"] = response
            self.print_result("Tools list", "PASS", f"{len(tools)} tools, Response time: {response_time:.3f}s")
        else:
            results["issues"].append(f"Tools list failed: {response}")
            results["status"] = "FAIL"
            self.print_result("Tools list", "FAIL", f"Bad response: {response}")
        
        return results
    
    def diagnose_tool_performance(self) -> Dict[str, Any]:
        """Diagnose individual tool performance."""
        self.print_section("TOOL PERFORMANCE DIAGNOSTICS")
        
        results = {"status": "PASS", "issues": [], "tools": {}}
        
        if not self.server_process or self.server_process.poll() is not None:
            results["issues"].append("Server not running")
            results["status"] = "FAIL"
            return results
        
        # Test each tool
        tool_tests = [
            {
                "name": "get_questions_summary",
                "args": {},
                "expected_time": 1.0
            },
            {
                "name": "get_questions_by_category",
                "args": {"category": "technical", "limit": 3},
                "expected_time": 2.0
            },
            {
                "name": "calculate_assessment_score",
                "args": {
                    "responses": [
                        {"question_id": "riskProfile1", "selected_values": ["item2-0"]},
                        {"question_id": "businessDrivers9", "selected_values": ["item1-0"]}
                    ]
                },
                "expected_time": 3.0
            },
            {
                "name": "assess_project",
                "args": {
                    "project_name": "Test Project",
                    "project_description": "Simple test project for diagnostics",
                    "responses": [
                        {"question_id": "riskProfile1", "selected_values": ["item2-0"]},
                        {"question_id": "businessDrivers9", "selected_values": ["item1-0"]}
                    ]
                },
                "expected_time": 5.0
            }
        ]
        
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
            
            start_time = time.time()
            response = self._send_request(request)
            response_time = time.time() - start_time
            
            tool_result = {
                "response_time": response_time,
                "expected_time": test["expected_time"],
                "success": False,
                "response": response
            }
            
            if response and "result" in response:
                content = response["result"].get("content", [])
                if content:
                    try:
                        json.loads(content[0]["text"])
                        tool_result["success"] = True
                        
                        # Check performance
                        if response_time <= test["expected_time"]:
                            status = "PASS"
                            details = f"Response time: {response_time:.3f}s (expected: <{test['expected_time']}s)"
                        else:
                            status = "WARN"
                            details = f"Slow response: {response_time:.3f}s (expected: <{test['expected_time']}s)"
                            
                        self.print_result(f"Tool: {test['name']}", status, details)
                        
                    except json.JSONDecodeError:
                        tool_result["success"] = False
                        results["issues"].append(f"{test['name']}: Invalid JSON response")
                        self.print_result(f"Tool: {test['name']}", "FAIL", "Invalid JSON response")
                else:
                    tool_result["success"] = False
                    results["issues"].append(f"{test['name']}: No content in response")
                    self.print_result(f"Tool: {test['name']}", "FAIL", "No content in response")
            else:
                tool_result["success"] = False
                results["issues"].append(f"{test['name']}: Request failed")
                self.print_result(f"Tool: {test['name']}", "FAIL", f"Request failed: {response}")
            
            results["tools"][test["name"]] = tool_result
        
        # Overall status
        if all(tool["success"] for tool in results["tools"].values()):
            results["status"] = "PASS"
        else:
            results["status"] = "FAIL"
        
        return results
    
    def diagnose_claude_desktop_config(self) -> Dict[str, Any]:
        """Diagnose Claude Desktop configuration issues."""
        self.print_section("CLAUDE DESKTOP CONFIGURATION DIAGNOSTICS")
        
        results = {"status": "PASS", "issues": [], "configs": {}}
        
        config_files = [
            ("macOS", "claude_desktop_config.json"),
            ("Windows", "claude_desktop_config_windows.json"),
            ("Linux", "claude_desktop_config_linux.json")
        ]
        
        for platform_name, config_file in config_files:
            config_path = Path(config_file)
            config_result = {"exists": False, "valid_json": False, "valid_structure": False}
            
            if config_path.exists():
                config_result["exists"] = True
                
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    config_result["valid_json"] = True
                    config_result["content"] = config
                    
                    # Validate structure
                    if ("mcpServers" in config and 
                        "aia-assessment" in config["mcpServers"] and
                        all(key in config["mcpServers"]["aia-assessment"] 
                            for key in ["command", "args", "cwd"])):
                        config_result["valid_structure"] = True
                        
                        # Check paths for current platform
                        if platform.system().lower() in platform_name.lower():
                            cwd_path = Path(config["mcpServers"]["aia-assessment"]["cwd"])
                            config_result["path_exists"] = cwd_path.exists()
                            
                            if cwd_path.exists():
                                self.print_result(f"Config: {platform_name}", "PASS", 
                                                f"Valid structure, path exists")
                            else:
                                results["issues"].append(f"{platform_name} config has invalid path: {cwd_path}")
                                self.print_result(f"Config: {platform_name}", "FAIL", 
                                                f"Path does not exist: {cwd_path}")
                        else:
                            self.print_result(f"Config: {platform_name}", "PASS", "Valid structure")
                    else:
                        results["issues"].append(f"{platform_name} config has invalid structure")
                        self.print_result(f"Config: {platform_name}", "FAIL", "Invalid structure")
                        
                except json.JSONDecodeError as e:
                    results["issues"].append(f"{platform_name} config has invalid JSON: {str(e)}")
                    self.print_result(f"Config: {platform_name}", "FAIL", f"Invalid JSON: {str(e)}")
            else:
                results["issues"].append(f"Missing config file: {config_file}")
                self.print_result(f"Config: {platform_name}", "FAIL", "File not found")
            
            results["configs"][platform_name] = config_result
        
        if results["issues"]:
            results["status"] = "FAIL"
        
        return results
    
    def _send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a JSON-RPC request to the server."""
        try:
            request_json = json.dumps(request) + "\n"
            self.server_process.stdin.write(request_json)
            self.server_process.stdin.flush()
            
            response_line = self.server_process.stdout.readline()
            if response_line:
                return json.loads(response_line.strip())
            else:
                return None
        except Exception as e:
            return {"error": f"Communication error: {str(e)}"}
    
    def cleanup(self):
        """Clean up server process."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
            self.logger.info("Server process terminated")
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive diagnostic report."""
        report = []
        report.append("# AIA Assessment MCP Server - Diagnostic Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        overall_status = "PASS" if all(
            result.get("status") == "PASS" 
            for result in results.values() 
            if isinstance(result, dict) and "status" in result
        ) else "FAIL"
        
        report.append(f"## Overall Status: {overall_status}")
        report.append("")
        
        # System Information
        if "system_info" in results:
            info = results["system_info"]
            report.append("## System Information")
            report.append(f"- Platform: {info['platform']['system']} {info['platform']['release']}")
            report.append(f"- Python: {info['python']['version']}")
            report.append(f"- CPU Cores: {info['resources']['cpu_count']}")
            report.append(f"- Memory: {info['resources']['memory_available'] / (1024**3):.1f}GB available")
            report.append("")
        
        # Issues Summary
        all_issues = []
        for result in results.values():
            if isinstance(result, dict) and "issues" in result:
                all_issues.extend(result["issues"])
        
        if all_issues:
            report.append("## Issues Found")
            for issue in all_issues:
                report.append(f"- {issue}")
            report.append("")
        
        # Performance Summary
        if "tool_performance" in results and "tools" in results["tool_performance"]:
            report.append("## Performance Summary")
            for tool_name, tool_data in results["tool_performance"]["tools"].items():
                response_time = tool_data.get("response_time", 0)
                expected_time = tool_data.get("expected_time", 0)
                status = "✅" if tool_data.get("success") and response_time <= expected_time else "⚠️"
                report.append(f"- {tool_name}: {response_time:.3f}s {status}")
            report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        if not all_issues:
            report.append("- All diagnostics passed. System is ready for production use.")
        else:
            report.append("- Address the issues listed above before proceeding.")
            report.append("- Run `python3 validate_mcp.py` after fixing issues.")
            report.append("- Check the troubleshooting guide in CLAUDE_DESKTOP_INTEGRATION.md")
        
        return "\n".join(report)
    
    def run_full_diagnostics(self) -> Dict[str, Any]:
        """Run complete diagnostic suite."""
        self.print_header("AIA ASSESSMENT MCP SERVER - COMPREHENSIVE DIAGNOSTICS")
        
        results = {}
        
        try:
            # Collect system information
            results["system_info"] = self.get_system_info()
            
            # Run diagnostics
            results["file_system"] = self.diagnose_file_system()
            results["python_environment"] = self.diagnose_python_environment()
            results["server_startup"] = self.diagnose_server_startup()
            results["communication"] = self.diagnose_communication()
            results["tool_performance"] = self.diagnose_tool_performance()
            results["claude_desktop_config"] = self.diagnose_claude_desktop_config()
            
            # Generate report
            report = self.generate_report(results)
            
            # Save report
            report_file = self.current_dir / "diagnostic_report.md"
            with open(report_file, 'w') as f:
                f.write(report)
            
            self.print_header("DIAGNOSTIC SUMMARY")
            print(report)
            print(f"\nFull report saved to: {report_file}")
            
            return results
            
        finally:
            self.cleanup()

def main():
    """Main function to run diagnostics."""
    diagnostics = AIADiagnostics()
    results = diagnostics.run_full_diagnostics()
    
    # Exit with appropriate code
    overall_success = all(
        result.get("status") == "PASS" 
        for result in results.values() 
        if isinstance(result, dict) and "status" in result
    )
    
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()
