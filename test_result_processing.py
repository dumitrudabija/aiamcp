#!/usr/bin/env python3
"""
Test script for result processing functionality
Tests the new compliance-ready output methods
"""

import json
from aia_processor import AIAProcessor

def test_result_processing():
    """Test the result processing and compliance output functionality."""
    print("AIA Result Processing Test")
    print("=" * 50)
    
    # Initialize processor
    print("1. Initializing AIAProcessor...")
    processor = AIAProcessor()
    
    # Sample project and responses
    project_name = "Customer Service Chatbot"
    project_description = "A chatbot that helps customers find products on our website. The chatbot uses natural language processing to understand customer queries and provides product recommendations based on their preferences. It integrates with our product database and can handle basic customer service inquiries like order status, return policies, and product availability."
    
    # Sample responses (simulating some answered questions)
    sample_responses = [
        {
            'question_id': 'riskProfile1',
            'selected_values': ['item2-0']  # No - not in area of intense scrutiny
        },
        {
            'question_id': 'riskProfile2', 
            'selected_values': ['item2-0']  # No - doesn't serve equity denied groups
        },
        {
            'question_id': 'businessDrivers9',
            'selected_values': ['item1-0']  # Yes - alternative processes considered
        },
        {
            'question_id': 'aboutSystem1',
            'selected_values': ['item2-1']  # Medium effectiveness
        },
        {
            'question_id': 'aboutAlgorithm1',
            'selected_values': ['item1-0']  # Uses machine learning
        }
    ]
    
    # Sample AI responses (simulating AI-generated answers with confidence)
    sample_ai_responses = [
        {
            'question_id': 'riskProfile1',
            'selected_value': 'item2-0',
            'confidence': 0.85,
            'reasoning': 'Customer service chatbot for product recommendations is not in an area of intense public scrutiny'
        },
        {
            'question_id': 'businessDrivers9',
            'selected_value': 'item1-0',
            'confidence': 0.75,
            'reasoning': 'Project description mentions this is an enhancement to existing customer service, suggesting alternatives were considered'
        },
        {
            'question_id': 'aboutAlgorithm1',
            'selected_value': 'item1-0',
            'confidence': 0.90,
            'reasoning': 'Project explicitly mentions using natural language processing and machine learning for recommendations'
        }
    ]
    
    print(f"\n2. Project: {project_name}")
    print(f"   Description: {project_description[:100]}...")
    print(f"   Sample responses: {len(sample_responses)}")
    print(f"   AI responses: {len(sample_ai_responses)}")
    
    # Test generate_assessment_report
    print(f"\n3. Testing generate_assessment_report()...")
    assessment_report = processor.generate_assessment_report(
        project_name=project_name,
        project_description=project_description,
        responses=sample_responses,
        ai_responses=sample_ai_responses
    )
    
    summary = assessment_report['assessment_summary']
    automation = assessment_report['automation_summary']
    
    print(f"   ✅ Assessment Summary:")
    print(f"      - Impact Level: {summary['level_name']}")
    print(f"      - Total Score: {summary['total_score']}/{summary['max_possible_score']} ({summary['score_percentage']}%)")
    print(f"      - Assessment Date: {summary['assessment_date'][:10]}")
    
    print(f"   ✅ Automation Summary:")
    print(f"      - Total Questions: {automation['total_questions']}")
    print(f"      - Auto-populated: {automation['auto_populated_count']} ({automation['automation_rate']}%)")
    print(f"      - Manual Required: {automation['manual_required_count']}")
    
    print(f"   ✅ Recommendations: {len(assessment_report['recommendations'])}")
    print(f"   ✅ Next Actions: {len(assessment_report['next_actions'])}")
    print(f"   ✅ Compliance Notes: {len(assessment_report['compliance_notes'])}")
    
    # Show sample auto-populated answers
    if assessment_report['auto_populated_answers']:
        print(f"\n   Sample Auto-populated Answers:")
        for answer in assessment_report['auto_populated_answers'][:2]:
            print(f"      - {answer['question_title'][:60]}...")
            print(f"        Answer: {answer['selected_answer']}")
            print(f"        Confidence: {answer['confidence_score']:.2f}")
    
    # Test prepare_jira_ticket
    print(f"\n4. Testing prepare_jira_ticket()...")
    jira_ticket = processor.prepare_jira_ticket(assessment_report)
    
    print(f"   ✅ JIRA Ticket Created:")
    print(f"      - Summary: {jira_ticket['summary']}")
    print(f"      - Priority: {jira_ticket['priority']}")
    print(f"      - Issue Type: {jira_ticket['issue_type']}")
    print(f"      - Labels: {', '.join(jira_ticket['labels'])}")
    print(f"      - Components: {', '.join(jira_ticket['components'])}")
    
    print(f"\n   Description Preview:")
    description_lines = jira_ticket['description'].split('\n')
    for line in description_lines[:10]:  # Show first 10 lines
        print(f"      {line}")
    if len(description_lines) > 10:
        print(f"      ... ({len(description_lines) - 10} more lines)")
    
    # Test export_assessment_json
    print(f"\n5. Testing export_assessment_json()...")
    json_export = processor.export_assessment_json(assessment_report, include_full_responses=True)
    
    # Parse to verify it's valid JSON
    try:
        export_data = json.loads(json_export)
        print(f"   ✅ JSON Export Created:")
        print(f"      - Export Size: {len(json_export)} characters")
        print(f"      - Framework Version: {export_data['export_metadata']['framework_version']}")
        print(f"      - Export Timestamp: {export_data['export_metadata']['export_timestamp'][:19]}")
        print(f"      - Includes Framework Details: {'framework_details' in export_data}")
        
        # Show structure
        print(f"\n   Export Structure:")
        for key in export_data.keys():
            print(f"      - {key}")
            if isinstance(export_data[key], dict):
                for subkey in list(export_data[key].keys())[:3]:
                    print(f"        - {subkey}")
                if len(export_data[key]) > 3:
                    print(f"        - ... ({len(export_data[key]) - 3} more)")
    
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON Export Error: {e}")
    
    # Test different impact levels
    print(f"\n6. Testing different impact levels...")
    
    # High-risk responses for testing
    high_risk_responses = [
        {'question_id': 'riskProfile1', 'selected_values': ['item1-3']},  # High scrutiny
        {'question_id': 'riskProfile2', 'selected_values': ['item1-3']},  # Serves equity denied groups
        {'question_id': 'riskProfile7', 'selected_values': ['item1-3']},  # High exploitation risk
        {'question_id': 'impact4A', 'selected_values': ['item1-4']},     # High impact
    ]
    
    high_risk_report = processor.generate_assessment_report(
        project_name="High-Risk AI System",
        project_description="High-impact automated decision system",
        responses=high_risk_responses
    )
    
    high_risk_jira = processor.prepare_jira_ticket(high_risk_report)
    
    print(f"   High-Risk System:")
    print(f"      - Impact Level: {high_risk_report['assessment_summary']['level_name']}")
    print(f"      - JIRA Priority: {high_risk_jira['priority']}")
    print(f"      - Next Actions: {len(high_risk_report['next_actions'])}")
    print(f"      - Sample Action: {high_risk_report['next_actions'][0] if high_risk_report['next_actions'] else 'None'}")
    
    print(f"\n✅ Result processing test completed!")
    print(f"🏢 Professional compliance reports generated")
    print(f"📋 JIRA tickets ready for workflow integration")
    print(f"📄 JSON exports ready for documentation")

if __name__ == "__main__":
    test_result_processing()
