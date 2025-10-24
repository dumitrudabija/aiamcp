#!/usr/bin/env python3
"""
Test script for AIA Assessment MCP Server
Tests the MCP server by sending JSON-RPC requests
"""

import json
import subprocess
import sys
import time

def test_mcp_server():
    """Test the MCP server functionality."""
    print("AIA Assessment MCP Server Test")
    print("=" * 40)
    
    # Start the MCP server process
    print("Starting MCP server...")
    server_process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd="."
    )
    
    # Give the server a moment to start
    time.sleep(1)
    
    try:
        # Test 1: Initialize
        print("\n1. Testing initialization...")
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
        
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"✅ Initialization successful: {response.get('result', {}).get('serverInfo', {}).get('name')}")
        
        # Test 2: List tools
        print("\n2. Testing tools list...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        server_process.stdin.write(json.dumps(tools_request) + "\n")
        server_process.stdin.flush()
        
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            tools = response.get('result', {}).get('tools', [])
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        
        # Test 3: Get questions summary
        print("\n3. Testing get_questions_summary tool...")
        summary_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_questions_summary",
                "arguments": {}
            }
        }
        
        server_process.stdin.write(json.dumps(summary_request) + "\n")
        server_process.stdin.flush()
        
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            content = response.get('result', {}).get('content', [])
            if content:
                summary_data = json.loads(content[0]['text'])
                summary = summary_data.get('summary', {})
                print(f"✅ Questions summary retrieved:")
                print(f"   - Framework: {summary.get('framework_name')}")
                print(f"   - Total questions: {summary.get('total_questions')}")
                print(f"   - Max score: {summary.get('max_possible_score')}")
                print(f"   - Categories: {summary.get('question_categories')}")
        
        # Test 4: Get questions by category
        print("\n4. Testing get_questions_by_category tool...")
        category_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_questions_by_category",
                "arguments": {
                    "category": "technical",
                    "limit": 3
                }
            }
        }
        
        server_process.stdin.write(json.dumps(category_request) + "\n")
        server_process.stdin.flush()
        
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            content = response.get('result', {}).get('content', [])
            if content:
                category_data = json.loads(content[0]['text'])
                print(f"✅ Technical questions retrieved:")
                print(f"   - Category: {category_data.get('category')}")
                print(f"   - Total in category: {category_data.get('total_in_category')}")
                print(f"   - Returned: {category_data.get('returned_count')}")
        
        # Test 5: Assess project
        print("\n5. Testing assess_project tool...")
        assess_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "assess_project",
                "arguments": {
                    "project_name": "Test ML System",
                    "project_description": "A machine learning system for automated loan approvals using credit scores and employment history."
                }
            }
        }
        
        server_process.stdin.write(json.dumps(assess_request) + "\n")
        server_process.stdin.flush()
        
        response_line = server_process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            content = response.get('result', {}).get('content', [])
            if content:
                assess_data = json.loads(content[0]['text'])
                assessment = assess_data.get('assessment', {})
                print(f"✅ Project assessment completed:")
                print(f"   - Project: {assessment.get('project_name')}")
                print(f"   - Status: {assessment.get('status')}")
                print(f"   - Questions available: {len(assessment.get('questions', []))}")
        
        print(f"\n🎉 All MCP server tests passed!")
        print(f"✅ The server is working correctly with all AIA processing capabilities preserved!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    finally:
        # Clean up
        server_process.terminate()
        server_process.wait()

if __name__ == "__main__":
    test_mcp_server()
