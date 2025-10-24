#!/usr/bin/env python3
"""
Test script to verify the Design phase question filtering fix.
This will test that only Design phase questions are answered, ensuring completion percentage never exceeds 100%.
"""

import json
import sys
import os

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import MCPServer

def test_design_phase_filtering():
    """Test that the fix properly filters to only Design phase questions."""
    
    print("=" * 60)
    print("TESTING DESIGN PHASE QUESTION FILTERING FIX")
    print("=" * 60)
    
    # Initialize the MCP server (which contains the methods we need to test)
    server = MCPServer()
    
    # Test project description that should trigger many questions
    test_project = {
        "projectName": "Test Design Phase Filtering",
        "projectDescription": """A comprehensive AI-powered customer service chatbot system that will automatically categorize incoming customer inquiries, route them to appropriate departments, and provide automated responses for common questions. The system will use machine learning algorithms to analyze customer sentiment and escalate urgent issues to human agents. It will process personal customer data including contact information, purchase history, and communication preferences to provide personalized service recommendations. The system will make automated decisions about service priority, resource allocation, and customer eligibility for various programs."""
    }
    
    print(f"Project: {test_project['projectName']}")
    print(f"Description length: {len(test_project['projectDescription'])} characters")
    print()
    
    # Test the intelligent analysis (this should now filter to Design phase questions only)
    try:
        auto_responses = server._intelligent_project_analysis(
            test_project['projectDescription']
        )
        
        print("ANALYSIS RESULTS:")
        print("-" * 40)
        
        # The method returns a list of auto responses
        print(f"Auto-answered questions: {len(auto_responses)}")
        
        # Get all Design phase questions to calculate what's remaining
        design_questions = server._get_design_phase_questions()
        answered_question_ids = {r['question_id'] for r in auto_responses}
        manual_questions = [q for q in design_questions if q['name'] not in answered_question_ids]
        
        print(f"Manual questions remaining: {len(manual_questions)}")
        
        # Calculate completion percentage using total Design phase questions
        design_phase_scoring_questions = len([q for q in design_questions if q.get('max_score', 0) > 0])
        completion_percentage = round((len(auto_responses) / len(design_questions)) * 100)
        print(f"Completion percentage: {completion_percentage}%")
        print()
        
        # Verify the fix worked
        print("VERIFICATION:")
        print("-" * 40)
        
        # Check that completion percentage is logical (≤100%)
        if completion_percentage <= 100:
            print("✅ PASS: Completion percentage is ≤100%")
        else:
            print(f"❌ FAIL: Completion percentage is {completion_percentage}% (>100%)")
        
        # Check total questions answered
        total_answered = len(auto_responses) + len(manual_questions)
        print(f"Total questions to be answered: {total_answered}")
        print(f"Design phase questions available: {len(design_questions)}")
        print(f"Design phase scoring questions: {design_phase_scoring_questions}")
        
        # Before the fix, this would be ~147 questions (all questions)
        # After the fix, this should be ~109 questions (Design phase only)
        if total_answered <= 120:  # Allow some margin
            print("✅ PASS: Total questions is reasonable for Design phase (~109 expected)")
        else:
            print(f"❌ FAIL: Total questions ({total_answered}) seems too high for Design phase")
        
        print()
        print("SAMPLE AUTO-ANSWERED QUESTIONS:")
        print("-" * 40)
        for i, response in enumerate(auto_responses[:5]):  # Show first 5
            print(f"{i+1}. {response.get('question_id', 'Unknown')}")
            print(f"   Reasoning: {response.get('reasoning', 'No reasoning provided')[:80]}...")
        
        if len(auto_responses) > 5:
            print(f"... and {len(auto_responses) - 5} more")
        
        print()
        print("SAMPLE MANUAL QUESTIONS:")
        print("-" * 40)
        for i, question in enumerate(manual_questions[:3]):  # Show first 3
            print(f"{i+1}. {question.get('name', 'Unknown')}")
            print(f"   Title: {question.get('title', 'Unknown')[:80]}...")
        
        if len(manual_questions) > 3:
            print(f"... and {len(manual_questions) - 3} more")
            
        return completion_percentage <= 100 and total_answered <= 120
        
    except Exception as e:
        print(f"❌ ERROR during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_design_phase_question_method():
    """Test the new _get_design_phase_questions method directly."""
    
    print("\n" + "=" * 60)
    print("TESTING _get_design_phase_questions() METHOD")
    print("=" * 60)
    
    server = MCPServer()
    
    try:
        # Test the new method
        design_questions = server._get_design_phase_questions()
        
        print(f"Total Design phase questions: {len(design_questions)}")
        
        # Count scoring questions
        scoring_questions = [q for q in design_questions if q.get('max_score', 0) > 0]
        print(f"Design phase scoring questions: {len(scoring_questions)}")
        
        # This should be around 109 based on the original analysis
        if 100 <= len(design_questions) <= 120:
            print("✅ PASS: Design phase question count is in expected range")
        else:
            print(f"❌ FAIL: Design phase question count ({len(design_questions)}) is outside expected range")
        
        print()
        print("SAMPLE DESIGN PHASE QUESTIONS:")
        print("-" * 40)
        for i, question in enumerate(design_questions[:5]):
            visible_if = question.get('visibleIf', 'Always visible')
            print(f"{i+1}. {question.get('name', 'Unknown')}")
            print(f"   Visibility: {visible_if}")
            print(f"   Max Score: {question.get('max_score', 0)}")
        
        return 100 <= len(design_questions) <= 120
        
    except Exception as e:
        print(f"❌ ERROR testing method: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing the Design Phase Question Filtering Fix")
    print("This verifies that completion percentage never exceeds 100%")
    print()
    
    # Run tests
    test1_passed = test_design_phase_filtering()
    test2_passed = test_design_phase_question_method()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The fix successfully filters to Design phase questions only")
        print("✅ Completion percentage will never exceed 100%")
        print("✅ Question filtering logic is working correctly")
    else:
        print("❌ SOME TESTS FAILED")
        if not test1_passed:
            print("❌ Design phase filtering test failed")
        if not test2_passed:
            print("❌ Design phase question method test failed")
    
    print()
