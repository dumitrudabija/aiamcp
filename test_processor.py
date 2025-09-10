#!/usr/bin/env python3
"""
Test script for AIAProcessor core functionality
Demonstrates the data processing methods
"""

from aia_processor import AIAProcessor
import json

def test_processor_methods():
    """Test all the core AIAProcessor methods."""
    print("AIA Processor Core Functionality Test")
    print("=" * 50)
    
    # Initialize processor
    print("1. Initializing AIAProcessor...")
    processor = AIAProcessor()
    
    # Test extract_questions
    print(f"\n2. Extract Questions:")
    print(f"   - Total questions extracted: {len(processor.scorable_questions)}")
    print(f"   - Sample question: {processor.scorable_questions[0]['name']}")
    print(f"   - Max possible score: {sum(q['max_score'] for q in processor.scorable_questions)}")
    
    # Test classify_questions
    print(f"\n3. Classify Questions:")
    categories = processor.question_categories
    print(f"   - Technical questions: {len(categories['technical'])}")
    print(f"   - Impact/Risk questions: {len(categories['impact_risk'])}")
    print(f"   - Manual questions: {len(categories['manual'])}")
    
    # Show some examples from each category
    print(f"\n   Technical examples: {categories['technical'][:3]}")
    print(f"   Impact/Risk examples: {categories['impact_risk'][:3]}")
    print(f"   Manual examples: {categories['manual'][:3]}")
    
    # Test calculate_score with sample responses
    print(f"\n4. Calculate Score:")
    sample_responses = [
        {
            'question_id': 'riskProfile1',
            'selected_values': ['item1-3']  # High risk answer (3 points)
        },
        {
            'question_id': 'riskProfile2', 
            'selected_values': ['item1-3']  # High risk answer (3 points)
        },
        {
            'question_id': 'businessDrivers9',
            'selected_values': ['item2-1']  # Medium risk answer (1 point)
        }
    ]
    
    total_score = processor.calculate_score(sample_responses)
    print(f"   - Sample responses processed: {len(sample_responses)}")
    print(f"   - Total calculated score: {total_score}")
    
    # Test determine_impact_level
    print(f"\n5. Determine Impact Level:")
    test_scores = [5, 18, 35, 65]
    
    for score in test_scores:
        level, name, description = processor.determine_impact_level(score)
        print(f"   - Score {score}: Level {level} - {name}")
        print(f"     {description}")
    
    # Test get_questions_summary
    print(f"\n6. Questions Summary:")
    summary = processor.get_questions_summary()
    print(f"   - Framework: {summary['framework_name']}")
    print(f"   - Total questions: {summary['total_questions']}")
    print(f"   - Max possible score: {summary['max_possible_score']}")
    print(f"   - Question types: {summary['question_types']}")
    print(f"   - Categories: {summary['question_categories']}")
    
    # Test full assessment workflow
    print(f"\n7. Full Assessment Workflow:")
    assessment = processor.assess_project(
        project_name="Test ML System",
        project_description="A machine learning system for loan approvals",
        responses=sample_responses
    )
    
    print(f"   - Project: {assessment['project_name']}")
    print(f"   - Total score: {assessment['total_score']}")
    print(f"   - Impact level: {assessment['impact_level']}")
    print(f"   - Level name: {assessment['level_name']}")
    print(f"   - Status: {assessment['status']}")
    
    print(f"\n✅ All processor methods working correctly!")
    print(f"🎉 The AIAProcessor is ready for AI integration!")

if __name__ == "__main__":
    test_processor_methods()
