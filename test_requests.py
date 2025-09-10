#!/usr/bin/env python3
"""
Test script for AIA Assessment FastAPI Server
Tests all endpoints to ensure they work correctly
"""

import requests
import json
import time

# Server configuration
BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint."""
    print("\nTesting / endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing root endpoint: {e}")
        return False

def test_questions_endpoint():
    """Test the questions endpoint."""
    print("\nTesting /questions endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/questions")
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing questions endpoint: {e}")
        return False

def test_assess_project_endpoint():
    """Test the assess-project endpoint."""
    print("\nTesting /assess-project endpoint...")
    try:
        test_data = {
            "project_description": "A machine learning system that automatically processes loan applications and makes approval decisions based on credit scores, income, and employment history. The system uses a random forest algorithm trained on historical data to predict default risk."
        }
        
        response = requests.post(
            f"{BASE_URL}/assess-project",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing assess-project endpoint: {e}")
        return False

def main():
    """Run all tests."""
    print("AIA Assessment API Test Suite")
    print("=" * 40)
    
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Root Endpoint", test_root_endpoint),
        ("Questions Endpoint", test_questions_endpoint),
        ("Assess Project Endpoint", test_assess_project_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        success = test_func()
        results.append((test_name, success))
        
        if success:
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")

if __name__ == "__main__":
    main()
