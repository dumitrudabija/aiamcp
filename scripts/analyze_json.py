#!/usr/bin/env python3
"""
AIA Survey JSON Analyzer

This script analyzes the survey-enfr.json file to understand the structure
of the Algorithmic Impact Assessment questionnaire and extract scoring information.
"""

import json
import re
from typing import Dict, List, Any, Optional

def load_survey_data(file_path: str) -> Dict[str, Any]:
    """Load the survey JSON data."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_score_from_value(value: str) -> Optional[int]:
    """Extract numeric score from choice value (e.g., 'item1-3' -> 3)."""
    if not isinstance(value, str):
        return None
    
    # Look for pattern like "item1-3" where the number after dash is the score
    match = re.search(r'item\d+-(\d+)', value)
    if match:
        return int(match.group(1))
    return None

def analyze_question_element(element: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a single question element and extract scoring information."""
    question_info = {
        'name': element.get('name', ''),
        'type': element.get('type', ''),
        'title': element.get('title', {}),
        'has_scoring': False,
        'choices': [],
        'max_score': 0,
        'scoring_type': None
    }
    
    # Extract title text (default English)
    if isinstance(question_info['title'], dict):
        question_info['title_text'] = question_info['title'].get('default', '')
    else:
        question_info['title_text'] = str(question_info['title'])
    
    # Check if element has choices with scoring
    choices = element.get('choices', [])
    if choices:
        scored_choices = []
        max_score = 0
        
        for choice in choices:
            choice_info = {
                'value': choice.get('value', ''),
                'text': choice.get('text', {}),
                'score': None
            }
            
            # Extract choice text
            if isinstance(choice_info['text'], dict):
                choice_info['text_display'] = choice_info['text'].get('default', '')
            else:
                choice_info['text_display'] = str(choice_info['text'])
            
            # Extract score from value
            score = extract_score_from_value(choice_info['value'])
            if score is not None:
                choice_info['score'] = score
                question_info['has_scoring'] = True
                max_score = max(max_score, score)
            
            scored_choices.append(choice_info)
        
        question_info['choices'] = scored_choices
        question_info['max_score'] = max_score
        
        # Determine scoring type
        if question_info['has_scoring']:
            if element.get('type') == 'radiogroup':
                question_info['scoring_type'] = 'single_choice'
            elif element.get('type') == 'checkbox':
                question_info['scoring_type'] = 'multiple_choice'
            elif element.get('type') == 'dropdown':
                question_info['scoring_type'] = 'dropdown'
    
    return question_info

def analyze_survey_structure(survey_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the complete survey structure."""
    analysis = {
        'total_pages': 0,
        'total_questions': 0,
        'scorable_questions': 0,
        'pages': [],
        'scorable_questions_list': [],
        'question_types': {},
        'max_possible_score': 0
    }
    
    pages = survey_data.get('pages', [])
    analysis['total_pages'] = len(pages)
    
    for page in pages:
        page_info = {
            'name': page.get('name', ''),
            'title': page.get('title', {}),
            'elements': [],
            'scorable_count': 0
        }
        
        # Extract page title
        if isinstance(page_info['title'], dict):
            page_info['title_text'] = page_info['title'].get('default', page_info['name'])
        else:
            page_info['title_text'] = str(page_info['title'])
        
        elements = page.get('elements', [])
        for element in elements:
            # Handle panels that contain sub-elements
            if element.get('type') == 'panel':
                sub_elements = element.get('elements', [])
                for sub_element in sub_elements:
                    if sub_element.get('type') in ['radiogroup', 'checkbox', 'dropdown']:
                        analysis['total_questions'] += 1
                        question_info = analyze_question_element(sub_element)
                        page_info['elements'].append(question_info)
                        
                        # Track question types
                        q_type = question_info['type']
                        analysis['question_types'][q_type] = analysis['question_types'].get(q_type, 0) + 1
                        
                        if question_info['has_scoring']:
                            analysis['scorable_questions'] += 1
                            page_info['scorable_count'] += 1
                            analysis['scorable_questions_list'].append(question_info)
                            analysis['max_possible_score'] += question_info['max_score']
            
            # Handle direct elements
            elif element.get('type') in ['radiogroup', 'checkbox', 'dropdown']:
                analysis['total_questions'] += 1
                question_info = analyze_question_element(element)
                page_info['elements'].append(question_info)
                
                # Track question types
                q_type = question_info['type']
                analysis['question_types'][q_type] = analysis['question_types'].get(q_type, 0) + 1
                
                if question_info['has_scoring']:
                    analysis['scorable_questions'] += 1
                    page_info['scorable_count'] += 1
                    analysis['scorable_questions_list'].append(question_info)
                    analysis['max_possible_score'] += question_info['max_score']
        
        analysis['pages'].append(page_info)
    
    return analysis

def print_analysis_summary(analysis: Dict[str, Any]):
    """Print a summary of the analysis."""
    print("=" * 80)
    print("AIA SURVEY STRUCTURE ANALYSIS")
    print("=" * 80)
    
    print(f"\nOVERVIEW:")
    print(f"  Total Pages: {analysis['total_pages']}")
    print(f"  Total Questions: {analysis['total_questions']}")
    print(f"  Scorable Questions: {analysis['scorable_questions']}")
    print(f"  Maximum Possible Score: {analysis['max_possible_score']}")
    
    print(f"\nQUESTION TYPES:")
    for q_type, count in analysis['question_types'].items():
        print(f"  {q_type}: {count}")
    
    print(f"\nPAGES WITH SCORABLE QUESTIONS:")
    for page in analysis['pages']:
        if page['scorable_count'] > 0:
            print(f"  {page['name']} ({page['title_text']}): {page['scorable_count']} scorable questions")
    
    print(f"\nSCORABLE QUESTIONS DETAILS:")
    print("-" * 80)
    
    for i, question in enumerate(analysis['scorable_questions_list'], 1):
        print(f"\n{i}. {question['name']} (Type: {question['type']}, Max Score: {question['max_score']})")
        print(f"   Title: {question['title_text'][:100]}{'...' if len(question['title_text']) > 100 else ''}")
        print(f"   Scoring Type: {question['scoring_type']}")
        
        if question['choices']:
            print("   Choices:")
            for choice in question['choices']:
                score_text = f" (Score: {choice['score']})" if choice['score'] is not None else ""
                choice_text = choice['text_display'][:60] + ('...' if len(choice['text_display']) > 60 else '')
                print(f"     - {choice['value']}: {choice_text}{score_text}")

def save_summary_to_json(analysis: Dict[str, Any], output_file: str):
    """Save a summary of scorable questions to JSON file."""
    summary = {
        'metadata': {
            'total_pages': analysis['total_pages'],
            'total_questions': analysis['total_questions'],
            'scorable_questions': analysis['scorable_questions'],
            'max_possible_score': analysis['max_possible_score'],
            'question_types': analysis['question_types']
        },
        'scorable_questions': []
    }
    
    for question in analysis['scorable_questions_list']:
        question_summary = {
            'name': question['name'],
            'type': question['type'],
            'title': question['title_text'],
            'scoring_type': question['scoring_type'],
            'max_score': question['max_score'],
            'choices': [
                {
                    'value': choice['value'],
                    'text': choice['text_display'],
                    'score': choice['score']
                }
                for choice in question['choices']
                if choice['score'] is not None
            ]
        }
        summary['scorable_questions'].append(question_summary)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\nSummary saved to: {output_file}")

def main():
    """Main function to run the analysis."""
    input_file = "data/survey-enfr.json"
    output_file = "questions_summary.json"
    
    try:
        print("Loading survey data...")
        survey_data = load_survey_data(input_file)
        
        print("Analyzing survey structure...")
        analysis = analyze_survey_structure(survey_data)
        
        print_analysis_summary(analysis)
        
        save_summary_to_json(analysis, output_file)
        
        print(f"\nAnalysis complete!")
        
    except FileNotFoundError:
        print(f"Error: Could not find file '{input_file}'")
        print("Make sure the survey-enfr.json file exists in the data/ directory")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{input_file}': {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
