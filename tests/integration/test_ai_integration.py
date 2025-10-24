#!/usr/bin/env python3
"""
Test script for AI-powered AIA question answering
Tests the new AI integration features with a sample project
"""

import os
from aia_processor import AIAProcessor

def test_ai_integration():
    """Test the AI-powered question answering functionality."""
    print("AIA AI Integration Test")
    print("=" * 50)
    
    # Initialize processor
    print("1. Initializing AIAProcessor...")
    processor = AIAProcessor()
    
    # Sample project description
    project_description = "A chatbot that helps customers find products on our website. The chatbot uses natural language processing to understand customer queries and provides product recommendations based on their preferences. It integrates with our product database and can handle basic customer service inquiries like order status, return policies, and product availability."
    
    print(f"\n2. Project Description:")
    print(f"   {project_description}")
    
    # Test without API key (fallback mode)
    print(f"\n3. Testing AI integration without API key (fallback mode)...")
    result_no_key = processor.match_project_to_questions(project_description)
    
    print(f"   Success: {result_no_key['success']}")
    print(f"   Fallback mode: {result_no_key['fallback_mode']}")
    print(f"   Error: {result_no_key.get('error', 'None')}")
    
    # Check if API key is available
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key:
        print(f"\n4. Testing AI integration with API key...")
        result_with_key = processor.match_project_to_questions(project_description, api_key)
        
        print(f"   Success: {result_with_key['success']}")
        print(f"   Fallback mode: {result_with_key['fallback_mode']}")
        
        if result_with_key['success']:
            responses = result_with_key['automated_responses']
            print(f"   Total questions processed: {result_with_key['total_processed']}")
            
            # Show first few responses
            print(f"\n   Sample AI responses:")
            for i, response in enumerate(responses[:3]):
                print(f"   {i+1}. Question: {response.get('question_id', 'Unknown')}")
                print(f"      Selected: {response.get('selected_value', 'Unknown')}")
                print(f"      Confidence: {response.get('confidence', 0.0):.2f}")
                print(f"      Reasoning: {response.get('reasoning', 'No reasoning provided')[:100]}...")
                print()
            
            # Test reasoning generation
            print(f"\n5. Testing reasoning generation...")
            reasoning_result = processor.generate_reasoning(
                project_description, 
                responses[:3],  # Test with first 3 responses
                api_key
            )
            
            print(f"   Success: {reasoning_result['success']}")
            if reasoning_result['success']:
                print(f"   Total explanations: {reasoning_result['total_explanations']}")
                
                # Show sample reasoning
                reasoning = reasoning_result.get('reasoning', {})
                for question_id, details in list(reasoning.items())[:2]:
                    print(f"\n   Reasoning for {question_id}:")
                    print(f"   - Explanation: {details.get('explanation', 'No explanation')[:150]}...")
                    print(f"   - Risk Assessment: {details.get('risk_assessment', 'No assessment')}")
            else:
                print(f"   Error: {reasoning_result.get('error', 'Unknown error')}")
        else:
            print(f"   Error: {result_with_key.get('error', 'Unknown error')}")
    else:
        print(f"\n4. No ANTHROPIC_API_KEY found in environment variables.")
        print(f"   To test AI integration, set the API key:")
        print(f"   export ANTHROPIC_API_KEY='your-api-key-here'")
    
    # Test question categorization
    print(f"\n6. Question categorization summary:")
    categories = processor.question_categories
    print(f"   Technical questions (AI-answerable): {len(categories['technical'])}")
    print(f"   Impact/Risk questions: {len(categories['impact_risk'])}")
    print(f"   Manual questions: {len(categories['manual'])}")
    
    # Show some technical question examples
    print(f"\n   Sample technical questions that AI can answer:")
    questions_by_name = {q['name']: q for q in processor.scorable_questions}
    
    for i, question_name in enumerate(categories['technical'][:5]):
        if question_name in questions_by_name:
            question = questions_by_name[question_name]
            print(f"   {i+1}. {question['title'][:80]}...")
    
    print(f"\n✅ AI integration test completed!")
    print(f"🤖 The system can automatically answer {len(categories['technical'])} technical questions")
    print(f"🧠 Fallback mode ensures the system works even without AI")

if __name__ == "__main__":
    test_ai_integration()
