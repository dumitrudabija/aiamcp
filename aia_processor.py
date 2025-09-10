"""
AIA Processor Module

Handles the core logic for processing Algorithmic Impact Assessments
based on Canada's AIA framework.
"""

import json
import os
import re
from typing import Dict, List, Any, Optional, Tuple
import logging
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

logger = logging.getLogger(__name__)

class AIAProcessor:
    """Processes AIA assessments and manages questionnaire data."""
    
    def __init__(self, data_path: str = "data/survey-enfr.json"):
        """
        Initialize the AIA processor.
        
        Args:
            data_path: Path to the survey data file
        """
        self.data_path = data_path
        self.survey_data = self._load_survey_data()
        self.scorable_questions = self.extract_questions()
        self.question_categories = self.classify_questions()
        
        # Load impact level thresholds from config
        self.impact_thresholds = self._load_impact_thresholds()
    
    def _load_survey_data(self) -> Dict[str, Any]:
        """Load survey data from JSON file."""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Successfully loaded survey data from {self.data_path}")
            return data
        except FileNotFoundError:
            logger.error(f"Survey data file not found: {self.data_path}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing survey data: {str(e)}")
            return {}
    
    def _load_impact_thresholds(self) -> Dict[int, Tuple[int, int]]:
        """Load impact level thresholds from config.json."""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            thresholds = {}
            scoring_config = config.get('scoring_thresholds', {})
            
            for level_key, level_data in scoring_config.items():
                if level_key.startswith('level_'):
                    level_num = int(level_key.split('_')[1])
                    min_score = level_data.get('min_score', 0)
                    max_score = level_data.get('max_score', 999)
                    thresholds[level_num] = (min_score, max_score)
            
            logger.info(f"Loaded impact thresholds from config: {thresholds}")
            return thresholds
            
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not load config thresholds, using defaults: {e}")
            # Fallback to original thresholds
            return {
                1: (0, 15),    # Level I: Very Low Impact
                2: (16, 30),   # Level II: Low Impact  
                3: (31, 50),   # Level III: Moderate Impact
                4: (51, 999)   # Level IV: High Impact
            }
    
    def extract_questions(self) -> List[Dict[str, Any]]:
        """
        Parse all scorable questions from the survey data.
        
        Returns:
            List of scorable questions with their metadata and scoring info
        """
        if not self.survey_data:
            return []
        
        scorable_questions = []
        
        # Navigate through the survey structure
        pages = self.survey_data.get('pages', [])
        
        for page in pages:
            elements = page.get('elements', [])
            
            for element in elements:
                # Handle panel elements that contain nested questions
                if element.get('type') == 'panel':
                    panel_elements = element.get('elements', [])
                    for panel_element in panel_elements:
                        question = self._process_question_element(panel_element)
                        if question:
                            scorable_questions.append(question)
                else:
                    # Handle direct question elements
                    question = self._process_question_element(element)
                    if question:
                        scorable_questions.append(question)
        
        logger.info(f"Extracted {len(scorable_questions)} scorable questions")
        return scorable_questions
    
    def _process_question_element(self, element: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a single question element and extract scoring information.
        
        Args:
            element: Question element from survey data
            
        Returns:
            Processed question dict or None if not scorable
        """
        question_type = element.get('type', '')
        question_name = element.get('name', '')
        
        # Skip non-question elements
        if question_type not in ['radiogroup', 'dropdown', 'checkbox'] or not question_name:
            return None
        
        # Extract choices and calculate scoring
        choices = element.get('choices', [])
        if not choices:
            return None
        
        # Process choices to extract scoring information
        processed_choices = []
        max_score = 0
        
        for choice in choices:
            choice_value = choice.get('value', '')
            choice_text = choice.get('text', {})
            
            # Extract score from choice value (format: item1-2, item2-1, etc.)
            score_match = re.search(r'item\d+-(\d+)', choice_value)
            score = int(score_match.group(1)) if score_match else 0
            
            # Handle text that might be a dict with language keys
            if isinstance(choice_text, dict):
                display_text = choice_text.get('default', choice_text.get('en', str(choice_text)))
            else:
                display_text = str(choice_text)
            
            processed_choices.append({
                'value': choice_value,
                'text': display_text,
                'score': score
            })
            
            max_score = max(max_score, score)
        
        # Handle title that might be a dict with language keys
        title = element.get('title', {})
        if isinstance(title, dict):
            display_title = title.get('default', title.get('en', str(title)))
        else:
            display_title = str(title)
        
        # Determine scoring type
        scoring_type = self._determine_scoring_type(question_type, processed_choices)
        
        return {
            'name': question_name,
            'type': question_type,
            'title': display_title,
            'choices': processed_choices,
            'max_score': max_score,
            'scoring_type': scoring_type
        }
    
    def _determine_scoring_type(self, question_type: str, choices: List[Dict]) -> str:
        """Determine the scoring type based on question type and choices."""
        if question_type == 'radiogroup':
            return 'single_choice'
        elif question_type == 'dropdown':
            return 'dropdown'
        elif question_type == 'checkbox':
            return 'multiple_choice'
        else:
            return 'unknown'
    
    def classify_questions(self) -> Dict[str, List[str]]:
        """
        Categorize questions based on whether they can be auto-filled, need reasoning, or require manual input.
        
        Returns:
            Dictionary with question names categorized by type
        """
        categories = {
            'technical': [],      # Can auto-fill from project description
            'impact_risk': [],    # Need reasoning/analysis
            'manual': []          # Require human input
        }
        
        # Define patterns for categorization
        technical_patterns = [
            'system', 'algorithm', 'data', 'technology', 'automated', 'machine learning',
            'artificial intelligence', 'processing', 'digital', 'software', 'platform'
        ]
        
        impact_risk_patterns = [
            'impact', 'risk', 'consequence', 'effect', 'harm', 'benefit', 'outcome',
            'result', 'influence', 'affect', 'damage', 'advantage', 'disadvantage'
        ]
        
        manual_patterns = [
            'consultation', 'approval', 'review', 'oversight', 'governance', 'policy',
            'legal', 'compliance', 'audit', 'assessment', 'evaluation', 'training',
            'staff', 'personnel', 'budget', 'cost', 'timeline', 'schedule'
        ]
        
        for question in self.scorable_questions:
            question_name = question['name'].lower()
            question_title = question['title'].lower()
            combined_text = f"{question_name} {question_title}"
            
            # Check for technical keywords
            if any(pattern in combined_text for pattern in technical_patterns):
                categories['technical'].append(question['name'])
            # Check for impact/risk keywords
            elif any(pattern in combined_text for pattern in impact_risk_patterns):
                categories['impact_risk'].append(question['name'])
            # Default to manual for everything else
            else:
                categories['manual'].append(question['name'])
        
        logger.info(f"Question categorization: Technical={len(categories['technical'])}, "
                   f"Impact/Risk={len(categories['impact_risk'])}, Manual={len(categories['manual'])}")
        
        return categories
    
    def calculate_score(self, responses: List[Dict[str, Any]]) -> int:
        """
        Calculate the total score based on question responses.
        
        Args:
            responses: List of responses with question_id and selected values
            
        Returns:
            Total calculated score
        """
        total_score = 0
        
        # Create a lookup dict for questions by name
        questions_by_name = {q['name']: q for q in self.scorable_questions}
        
        for response in responses:
            question_id = response.get('question_id', '')
            selected_values = response.get('selected_values', [])
            
            if not isinstance(selected_values, list):
                selected_values = [selected_values]
            
            question = questions_by_name.get(question_id)
            if not question:
                continue
            
            # Calculate score based on question type
            question_score = 0
            
            if question['scoring_type'] == 'single_choice':
                # For single choice, take the score of the selected option
                if selected_values:
                    selected_value = selected_values[0]
                    for choice in question['choices']:
                        if choice['value'] == selected_value:
                            question_score = choice['score']
                            break
            
            elif question['scoring_type'] == 'multiple_choice':
                # For multiple choice, sum all selected scores
                for selected_value in selected_values:
                    for choice in question['choices']:
                        if choice['value'] == selected_value:
                            question_score += choice['score']
            
            elif question['scoring_type'] == 'dropdown':
                # For dropdown, take the score of the selected option
                if selected_values:
                    selected_value = selected_values[0]
                    for choice in question['choices']:
                        if choice['value'] == selected_value:
                            question_score = choice['score']
                            break
            
            total_score += question_score
            logger.debug(f"Question {question_id}: score={question_score}, total={total_score}")
        
        logger.info(f"Total calculated score: {total_score}")
        return total_score
    
    def determine_impact_level(self, score: int) -> Tuple[int, str, str]:
        """
        Convert score to impact level (1-4) based on Canada's AIA framework.
        
        Args:
            score: Total assessment score
            
        Returns:
            Tuple of (level_number, level_name, description)
        """
        for level, (min_score, max_score) in self.impact_thresholds.items():
            if min_score <= score <= max_score:
                level_info = self._get_level_info(level)
                logger.info(f"Score {score} corresponds to Impact Level {level}: {level_info['name']}")
                return level, level_info['name'], level_info['description']
        
        # Fallback to highest level if score exceeds all thresholds
        level_info = self._get_level_info(4)
        return 4, level_info['name'], level_info['description']
    
    def _get_level_info(self, level: int) -> Dict[str, str]:
        """Get detailed information for an impact level."""
        level_details = {
            1: {
                'name': 'Level I - Very Low Impact',
                'description': 'Minimal oversight required. Standard operational procedures apply.'
            },
            2: {
                'name': 'Level II - Low Impact', 
                'description': 'Enhanced oversight required. Additional documentation and monitoring needed.'
            },
            3: {
                'name': 'Level III - Moderate Impact',
                'description': 'Qualified oversight required. Comprehensive governance and regular auditing needed.'
            },
            4: {
                'name': 'Level IV - High Impact',
                'description': 'Qualified oversight and approval required. Extensive governance, monitoring, and external validation needed.'
            }
        }
        
        return level_details.get(level, level_details[4])
    
    def get_questions_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the AIA framework and questions.
        
        Returns:
            Dictionary containing framework information and question statistics
        """
        total_questions = len(self.scorable_questions)
        max_possible_score = sum(q['max_score'] for q in self.scorable_questions)
        
        # Count questions by type
        question_types = {}
        for question in self.scorable_questions:
            q_type = question['type']
            question_types[q_type] = question_types.get(q_type, 0) + 1
        
        return {
            'framework_name': 'Canada\'s Algorithmic Impact Assessment',
            'total_questions': total_questions,
            'max_possible_score': max_possible_score,
            'question_types': question_types,
            'question_categories': {
                'technical': len(self.question_categories['technical']),
                'impact_risk': len(self.question_categories['impact_risk']),
                'manual': len(self.question_categories['manual'])
            },
            'impact_levels': {
                'Level I': '0-15 points (Very Low Impact)',
                'Level II': '16-30 points (Low Impact)',
                'Level III': '31-50 points (Moderate Impact)',
                'Level IV': '51+ points (High Impact)'
            },
            'data_loaded': bool(self.survey_data),
            'questions_extracted': total_questions > 0
        }
    
    def match_project_to_questions(self, project_description: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Use AI to automatically answer technical questions based on project description.
        
        Args:
            project_description: Detailed description of the project
            api_key: Optional Anthropic API key (can also be set via environment variable)
            
        Returns:
            Dictionary with automated answers and confidence scores
        """
        if not ANTHROPIC_AVAILABLE:
            logger.warning("Anthropic library not available. Falling back to manual mode.")
            return {
                'success': False,
                'error': 'AI integration not available - anthropic library not installed',
                'automated_responses': [],
                'fallback_mode': True
            }
        
        # Get API key from parameter or environment
        if not api_key:
            api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            logger.warning("No Anthropic API key provided. Falling back to manual mode.")
            return {
                'success': False,
                'error': 'No API key provided',
                'automated_responses': [],
                'fallback_mode': True
            }
        
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            # Get technical questions only
            technical_questions = []
            questions_by_name = {q['name']: q for q in self.scorable_questions}
            
            for question_name in self.question_categories['technical']:
                if question_name in questions_by_name:
                    technical_questions.append(questions_by_name[question_name])
            
            logger.info(f"Processing {len(technical_questions)} technical questions with AI")
            
            automated_responses = []
            
            # Process questions in batches to avoid token limits
            batch_size = 5
            for i in range(0, len(technical_questions), batch_size):
                batch = technical_questions[i:i+batch_size]
                batch_responses = self._process_question_batch(client, project_description, batch)
                automated_responses.extend(batch_responses)
            
            return {
                'success': True,
                'automated_responses': automated_responses,
                'total_processed': len(automated_responses),
                'fallback_mode': False
            }
            
        except Exception as e:
            logger.error(f"AI processing failed: {str(e)}")
            return {
                'success': False,
                'error': f'AI processing failed: {str(e)}',
                'automated_responses': [],
                'fallback_mode': True
            }
    
    def _process_question_batch(self, client, project_description: str, questions: List[Dict]) -> List[Dict]:
        """Process a batch of questions using the AI API."""
        
        # Build the prompt for this batch
        prompt = f"""You are an expert in Canada's Algorithmic Impact Assessment (AIA) framework. 

Project Description: {project_description}

Based on this project description, please answer the following AIA questions. For each question, select the most appropriate answer choice and provide a confidence score (0.0 to 1.0).

Questions:
"""
        
        for i, question in enumerate(questions, 1):
            prompt += f"\n{i}. Question ID: {question['name']}\n"
            prompt += f"   Question: {question['title']}\n"
            prompt += f"   Answer choices:\n"
            
            for choice in question['choices']:
                prompt += f"   - {choice['value']}: {choice['text']} (Score: {choice['score']})\n"
        
        prompt += """
Please respond in JSON format with an array of responses:
{
  "responses": [
    {
      "question_id": "question_name",
      "selected_value": "item_value",
      "confidence": 0.85,
      "reasoning": "Brief explanation of why this answer was selected"
    }
  ]
}

Focus on technical aspects that can be determined from the project description. Be conservative with confidence scores - use lower scores when uncertain.
"""
        
        try:
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the AI response
            response_text = response.content[0].text
            
            # Extract JSON from the response
            import json
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                ai_responses = json.loads(json_text)
                return ai_responses.get('responses', [])
            else:
                logger.error("Could not extract JSON from AI response")
                return []
                
        except Exception as e:
            logger.error(f"Error processing question batch: {str(e)}")
            return []
    
    def generate_reasoning(self, project_description: str, responses: List[Dict], api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate detailed reasoning for why each answer was selected.
        
        Args:
            project_description: Project description
            responses: List of question responses with answers
            api_key: Optional Anthropic API key
            
        Returns:
            Dictionary with detailed reasoning for each response
        """
        if not ANTHROPIC_AVAILABLE or not api_key:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            
        if not api_key:
            return {
                'success': False,
                'error': 'No API key available for reasoning generation',
                'reasoning': {}
            }
        
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            # Build prompt for reasoning
            questions_by_name = {q['name']: q for q in self.scorable_questions}
            
            prompt = f"""You are an expert in Canada's Algorithmic Impact Assessment (AIA) framework.

Project Description: {project_description}

The following answers were selected for AIA questions. Please provide detailed reasoning for each answer, explaining how the project description supports this choice and what specific aspects led to this decision.

Selected Answers:
"""
            
            for response in responses:
                question_id = response.get('question_id', '')
                selected_value = response.get('selected_value', '')
                
                if question_id in questions_by_name:
                    question = questions_by_name[question_id]
                    selected_choice = None
                    
                    for choice in question['choices']:
                        if choice['value'] == selected_value:
                            selected_choice = choice
                            break
                    
                    if selected_choice:
                        prompt += f"\nQuestion: {question['title']}\n"
                        prompt += f"Selected Answer: {selected_choice['text']} (Score: {selected_choice['score']})\n"
                        prompt += f"Question ID: {question_id}\n"
            
            prompt += """
Please provide detailed reasoning for each answer in JSON format:
{
  "reasoning": {
    "question_id": {
      "explanation": "Detailed explanation of why this answer was selected",
      "project_factors": ["List of specific project factors that support this choice"],
      "risk_assessment": "Assessment of risk level this choice represents",
      "confidence_factors": "What makes this choice more or less certain"
    }
  }
}
"""
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text
            
            # Extract JSON
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                reasoning_data = json.loads(json_text)
                
                return {
                    'success': True,
                    'reasoning': reasoning_data.get('reasoning', {}),
                    'total_explanations': len(reasoning_data.get('reasoning', {}))
                }
            else:
                return {
                    'success': False,
                    'error': 'Could not parse reasoning response',
                    'reasoning': {}
                }
                
        except Exception as e:
            logger.error(f"Error generating reasoning: {str(e)}")
            return {
                'success': False,
                'error': f'Reasoning generation failed: {str(e)}',
                'reasoning': {}
            }

    def generate_assessment_report(self, project_name: str, project_description: str, 
                                 responses: List[Dict], ai_responses: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive assessment report for compliance teams.
        
        Args:
            project_name: Name of the project
            project_description: Description of the project
            responses: List of all question responses
            ai_responses: Optional list of AI-generated responses with confidence scores
            
        Returns:
            Professional assessment report with recommendations
        """
        from datetime import datetime
        
        # Calculate score and impact level
        total_score = self.calculate_score(responses)
        impact_level, level_name, level_description = self.determine_impact_level(total_score)
        max_possible_score = sum(q['max_score'] for q in self.scorable_questions)
        
        # Categorize responses
        questions_by_name = {q['name']: q for q in self.scorable_questions}
        auto_populated = []
        manual_required = []
        
        # Track which questions were answered
        answered_questions = {r.get('question_id', '') for r in responses}
        
        # Process AI responses if available
        if ai_responses:
            ai_confidence_map = {r.get('question_id', ''): r for r in ai_responses}
            
            for response in responses:
                question_id = response.get('question_id', '')
                if question_id in ai_confidence_map and question_id in questions_by_name:
                    ai_data = ai_confidence_map[question_id]
                    question = questions_by_name[question_id]
                    
                    # Find selected choice text
                    selected_text = "Unknown"
                    for choice in question['choices']:
                        if choice['value'] == response.get('selected_values', [None])[0]:
                            selected_text = choice['text']
                            break
                    
                    auto_populated.append({
                        'question_id': question_id,
                        'question_title': question['title'],
                        'selected_answer': selected_text,
                        'confidence_score': ai_data.get('confidence', 0.0),
                        'ai_reasoning': ai_data.get('reasoning', 'No reasoning provided')
                    })
        
        # Identify questions requiring manual input
        for category in ['impact_risk', 'manual']:
            for question_name in self.question_categories[category]:
                if question_name not in answered_questions and question_name in questions_by_name:
                    question = questions_by_name[question_name]
                    manual_required.append({
                        'question_id': question_name,
                        'question_title': question['title'],
                        'category': category,
                        'choices': [{'value': c['value'], 'text': c['text'], 'score': c['score']} 
                                  for c in question['choices']]
                    })
        
        # Generate recommendations based on impact level
        recommendations = self._generate_compliance_recommendations(impact_level, total_score, max_possible_score)
        
        return {
            'assessment_summary': {
                'project_name': project_name,
                'project_description': project_description,
                'assessment_date': datetime.now().isoformat(),
                'total_score': total_score,
                'max_possible_score': max_possible_score,
                'score_percentage': round((total_score / max_possible_score) * 100, 1),
                'impact_level': impact_level,
                'level_name': level_name,
                'level_description': level_description
            },
            'automation_summary': {
                'total_questions': len(self.scorable_questions),
                'auto_populated_count': len(auto_populated),
                'manual_required_count': len(manual_required),
                'automation_rate': round((len(auto_populated) / len(self.scorable_questions)) * 100, 1)
            },
            'auto_populated_answers': auto_populated,
            'manual_input_required': manual_required,
            'recommendations': recommendations,
            'next_actions': self._get_next_actions(impact_level),
            'compliance_notes': self._get_compliance_notes(impact_level)
        }
    
    def prepare_jira_ticket(self, assessment_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format assessment results for JIRA ticket creation.
        
        Args:
            assessment_report: Output from generate_assessment_report()
            
        Returns:
            JIRA-formatted ticket data
        """
        summary = assessment_report['assessment_summary']
        automation = assessment_report['automation_summary']
        
        # Determine priority based on impact level
        priority_map = {
            1: "Low",
            2: "Medium", 
            3: "High",
            4: "Critical"
        }
        
        priority = priority_map.get(summary['impact_level'], "Medium")
        
        # Build description
        description = f"""
*Project:* {summary['project_name']}

*Assessment Summary:*
• Impact Level: {summary['level_name']}
• Total Score: {summary['total_score']}/{summary['max_possible_score']} ({summary['score_percentage']}%)
• Assessment Date: {summary['assessment_date'][:10]}

*Automation Results:*
• Questions Processed: {automation['total_questions']}
• Auto-populated: {automation['auto_populated_count']} ({automation['automation_rate']}%)
• Manual Input Required: {automation['manual_required_count']}

*Project Description:*
{summary['project_description']}

*Impact Level Description:*
{summary['level_description']}

*Required Actions:*
"""
        
        for action in assessment_report['next_actions']:
            description += f"• {action}\n"
        
        if assessment_report['manual_input_required']:
            description += f"\n*Questions Requiring Manual Review:*\n"
            for question in assessment_report['manual_input_required'][:5]:  # Limit to first 5
                description += f"• {question['question_title']}\n"
            
            if len(assessment_report['manual_input_required']) > 5:
                description += f"• ... and {len(assessment_report['manual_input_required']) - 5} more questions\n"
        
        description += f"\n*Compliance Notes:*\n"
        for note in assessment_report['compliance_notes']:
            description += f"• {note}\n"
        
        return {
            'summary': f"AIA Assessment Required - {summary['level_name']} - {summary['project_name']}",
            'description': description.strip(),
            'priority': priority,
            'issue_type': "Task",
            'labels': [
                "aia-assessment",
                f"impact-level-{summary['impact_level']}",
                "compliance",
                "automated-assessment"
            ],
            'components': ["Compliance", "Risk Management"],
            'custom_fields': {
                'aia_score': summary['total_score'],
                'aia_impact_level': summary['impact_level'],
                'automation_rate': automation['automation_rate']
            }
        }
    
    def export_assessment_json(self, assessment_report: Dict[str, Any], 
                             include_full_responses: bool = True) -> str:
        """
        Export full assessment data as JSON for compliance documentation.
        
        Args:
            assessment_report: Output from generate_assessment_report()
            include_full_responses: Whether to include detailed response data
            
        Returns:
            JSON string of complete assessment data
        """
        export_data = {
            'export_metadata': {
                'export_timestamp': self._get_timestamp(),
                'framework_version': 'Canada AIA v1.0',
                'export_format_version': '1.0',
                'generated_by': 'AIA Assessment MCP Server'
            },
            'assessment_report': assessment_report
        }
        
        if include_full_responses:
            export_data['framework_details'] = {
                'total_questions': len(self.scorable_questions),
                'question_categories': {
                    'technical': len(self.question_categories['technical']),
                    'impact_risk': len(self.question_categories['impact_risk']),
                    'manual': len(self.question_categories['manual'])
                },
                'scoring_thresholds': {
                    'Level I': '0-15 points (Very Low Impact)',
                    'Level II': '16-30 points (Low Impact)',
                    'Level III': '31-50 points (Moderate Impact)',
                    'Level IV': '51+ points (High Impact)'
                }
            }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def _generate_compliance_recommendations(self, impact_level: int, score: int, max_score: int) -> List[str]:
        """Generate compliance recommendations based on impact level."""
        recommendations = []
        
        if impact_level == 1:
            recommendations.extend([
                "Implement standard operational procedures and documentation",
                "Establish basic monitoring and logging mechanisms",
                "Conduct periodic reviews of system performance",
                "Maintain clear documentation of decision-making processes"
            ])
        elif impact_level == 2:
            recommendations.extend([
                "Implement enhanced oversight and monitoring procedures",
                "Establish clear audit trails for all automated decisions",
                "Conduct regular stakeholder consultations",
                "Implement bias detection and mitigation measures",
                "Establish clear escalation procedures for edge cases"
            ])
        elif impact_level == 3:
            recommendations.extend([
                "Implement comprehensive governance framework",
                "Establish qualified oversight committee",
                "Conduct regular third-party audits",
                "Implement robust bias testing and mitigation",
                "Establish clear appeals and recourse mechanisms",
                "Conduct comprehensive stakeholder engagement",
                "Implement continuous monitoring and alerting"
            ])
        else:  # Level 4
            recommendations.extend([
                "Obtain qualified oversight and formal approval before deployment",
                "Implement extensive governance and risk management framework",
                "Conduct comprehensive external validation and testing",
                "Establish independent oversight board",
                "Implement real-time monitoring and intervention capabilities",
                "Conduct ongoing impact assessments and audits",
                "Establish comprehensive appeals and recourse processes",
                "Implement robust transparency and explainability measures"
            ])
        
        return recommendations
    
    def _get_next_actions(self, impact_level: int) -> List[str]:
        """Get immediate next actions based on impact level."""
        actions = []
        
        if impact_level == 1:
            actions.extend([
                "Complete remaining manual questions",
                "Document standard operating procedures",
                "Schedule periodic review (annually)"
            ])
        elif impact_level == 2:
            actions.extend([
                "Complete remaining manual questions",
                "Establish enhanced monitoring procedures",
                "Schedule stakeholder consultation",
                "Plan quarterly reviews"
            ])
        elif impact_level == 3:
            actions.extend([
                "Complete remaining manual questions",
                "Establish governance committee",
                "Schedule third-party audit",
                "Implement comprehensive monitoring",
                "Plan monthly reviews"
            ])
        else:  # Level 4
            actions.extend([
                "URGENT: Obtain qualified oversight approval",
                "Complete all remaining questions immediately",
                "Establish independent oversight board",
                "Schedule external validation",
                "Implement continuous monitoring",
                "Plan weekly reviews until deployment"
            ])
        
        return actions
    
    def _get_compliance_notes(self, impact_level: int) -> List[str]:
        """Get compliance-specific notes based on impact level."""
        notes = []
        
        if impact_level >= 3:
            notes.append("High-impact system requires qualified oversight as per Treasury Board Directive")
        
        if impact_level == 4:
            notes.append("Critical system requires deputy head approval before deployment")
            notes.append("External validation and independent oversight mandatory")
        
        notes.extend([
            "All automated decisions must be explainable and auditable",
            "Regular bias testing and mitigation measures required",
            "Clear appeals process must be established for affected individuals"
        ])
        
        return notes
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

    def assess_project(self, project_name: str, project_description: str, 
                      responses: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Assess a project using the AIA framework.
        
        Args:
            project_name: Name of the project
            project_description: Description of the project
            responses: List of question responses (optional)
            
        Returns:
            Assessment results including risk score and recommendations
        """
        from datetime import datetime
        
        if responses:
            # Calculate score and determine impact level
            total_score = self.calculate_score(responses)
            impact_level, level_name, level_description = self.determine_impact_level(total_score)
            
            return {
                'project_name': project_name,
                'project_description': project_description,
                'timestamp': datetime.now().isoformat(),
                'total_score': total_score,
                'impact_level': impact_level,
                'level_name': level_name,
                'level_description': level_description,
                'max_possible_score': sum(q['max_score'] for q in self.scorable_questions),
                'responses_count': len(responses),
                'status': 'completed'
            }
        else:
            # Return questions that need to be answered
            return {
                'project_name': project_name,
                'project_description': project_description,
                'timestamp': datetime.now().isoformat(),
                'questions': self.scorable_questions,
                'question_categories': self.question_categories,
                'total_questions': len(self.scorable_questions),
                'status': 'questions_required'
            }
