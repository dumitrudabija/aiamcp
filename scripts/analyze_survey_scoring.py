#!/usr/bin/env python3
"""
Analyze survey data to find actual question IDs and their scoring values
for creating realistic test scenarios.
"""

import json
import re
from typing import Dict, List, Tuple

def analyze_survey_scoring():
    """Analyze the survey data to understand question scoring."""
    
    # Load survey data
    with open('data/survey-enfr.json', 'r', encoding='utf-8') as f:
        survey_data = json.load(f)
    
    scoring_questions = []
    
    # Analyze each page
    for page in survey_data.get('pages', []):
        page_name = page.get('name', '')
        print(f"\n=== PAGE: {page_name} ===")
        
        # Analyze elements in each page
        for element in page.get('elements', []):
            analyze_element(element, page_name, scoring_questions)
    
    # Sort by highest scores
    scoring_questions.sort(key=lambda x: x[2], reverse=True)
    
    print(f"\n=== TOP SCORING QUESTIONS ===")
    for question_id, question_type, max_score, choices in scoring_questions[:20]:
        print(f"{question_id}: {question_type} (max: {max_score})")
        for choice_value, choice_score in choices[:3]:  # Show top 3 choices
            print(f"  - {choice_value}: {choice_score} points")
    
    # Create test scenarios based on actual data
    create_test_scenarios(scoring_questions)

def analyze_element(element, page_name, scoring_questions):
    """Analyze a survey element for scoring information."""
    
    # Handle nested panels
    if element.get('type') == 'panel':
        for nested_element in element.get('elements', []):
            analyze_element(nested_element, page_name, scoring_questions)
        return
    
    if element.get('type') not in ['radiogroup', 'dropdown', 'checkbox']:
        return
    
    question_id = element.get('name', '')
    question_type = element.get('type', '')
    choices = element.get('choices', [])
    
    if not choices:
        return
    
    # Extract scoring from choice values
    choice_scores = []
    max_score = 0
    
    for choice in choices:
        value = choice.get('value', '')
        score = extract_score_from_value(value)
        if score is not None:
            choice_scores.append((value, score))
            max_score = max(max_score, score)
    
    if choice_scores:
        scoring_questions.append((question_id, question_type, max_score, choice_scores))
        print(f"  {question_id}: {question_type} (max: {max_score})")

def extract_score_from_value(value):
    """Extract numeric score from choice value."""
    # Look for patterns like "item1-3", "item2-4", etc.
    match = re.search(r'item\d+-(\d+)', value)
    if match:
        return int(match.group(1))
    return None

def create_test_scenarios(scoring_questions):
    """Create realistic test scenarios based on actual survey data."""
    
    # Filter questions by score ranges
    high_score_questions = [q for q in scoring_questions if q[2] >= 3]
    medium_score_questions = [q for q in scoring_questions if q[2] == 2]
    low_score_questions = [q for q in scoring_questions if q[2] <= 1]
    
    print(f"\n=== TEST SCENARIO RECOMMENDATIONS ===")
    print(f"High score questions (3-4 points): {len(high_score_questions)}")
    print(f"Medium score questions (2 points): {len(medium_score_questions)}")
    print(f"Low score questions (0-1 points): {len(low_score_questions)}")
    
    # Create scenarios for different risk levels
    scenarios = {
        "low_risk": {
            "target_score": 15,  # Level I (0-30)
            "questions": low_score_questions[:5] + medium_score_questions[:2]
        },
        "medium_risk": {
            "target_score": 45,  # Level II (31-55)
            "questions": medium_score_questions[:5] + high_score_questions[:3]
        },
        "high_risk": {
            "target_score": 65,  # Level III (56-75)
            "questions": high_score_questions[:8] + medium_score_questions[:3]
        },
        "very_high_risk": {
            "target_score": 85,  # Level IV (76+)
            "questions": high_score_questions[:12] + medium_score_questions[:2]
        }
    }
    
    print(f"\n=== RECOMMENDED TEST RESPONSES ===")
    for scenario_name, scenario in scenarios.items():
        print(f"\n{scenario_name.upper()}:")
        print(f"Target score: {scenario['target_score']}")
        
        responses = []
        total_score = 0
        
        for question_id, question_type, max_score, choices in scenario['questions']:
            if not choices:
                continue
                
            # Pick highest scoring choice for this question
            best_choice = max(choices, key=lambda x: x[1])
            responses.append({
                "question_id": question_id,
                "selected_values": [best_choice[0]]
            })
            total_score += best_choice[1]
            
            print(f"  {question_id}: {best_choice[0]} ({best_choice[1]} points)")
        
        print(f"  Estimated total: {total_score} points")
        
        # Save to file for easy copying
        with open(f'test_scenario_{scenario_name}.json', 'w') as f:
            json.dump({
                "name": scenario_name,
                "target_score": scenario['target_score'],
                "estimated_score": total_score,
                "responses": responses
            }, f, indent=2)

if __name__ == "__main__":
    analyze_survey_scoring()
