#!/usr/bin/env python3
"""
AIA Assessment MCP Server
A Model Context Protocol server for Canada's Algorithmic Impact Assessment (AIA)

IMPORTANT: AIA refers specifically to Canada's Algorithmic Impact Assessment framework,
a mandatory assessment tool for Canadian federal government institutions to evaluate
the impact of automated decision systems. This is NOT a generic AI assessment tool.

Framework Details:
- Official Government of Canada requirement (Treasury Board Directive)
- Applies to automated decision systems used by federal institutions
- Measures impact on rights, health, economic interests, and environment
- Results in Impact Levels I-IV with corresponding mitigation requirements
- Based on specific questionnaire with 48+ questions across 8 categories
"""

import json
import logging
import sys
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from docx import Document
from docx.shared import Inches
from aia_processor import AIAProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

class MCPServer:
    """Simple MCP server implementation using JSON-RPC over stdio."""
    
    def __init__(self):
        # Change to the script's directory to ensure data files are found
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print(f"DEBUG: Changed working directory to: {script_dir}", file=sys.stderr)
        
        self.aia_processor = AIAProcessor()
        self.server_info = {
            "name": "aia-assessment-server",
            "version": "1.0.0"
        }
        
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        try:
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")
            
            print(f"Handling request - Method: {method}, ID: {request_id}", file=sys.stderr)
            
            if method == "initialize":
                return self._initialize(request_id, params)
            elif method == "tools/list":
                return self._list_tools(request_id)
            elif method == "tools/call":
                return self._call_tool(request_id, params)
            elif method == "notifications/initialized":
                # Handle notification - no response needed
                print(f"Received notification: {method}", file=sys.stderr)
                return None
            elif method in ["prompts/list", "resources/list"]:
                # Handle unsupported methods gracefully
                print(f"Unsupported method: {method}", file=sys.stderr)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            else:
                print(f"Unknown method: {method}", file=sys.stderr)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            print(f"ERROR in handle_request: {str(e)}", file=sys.stderr)
            import traceback
            print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
            logger.error(f"Error handling request: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    def _initialize(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request."""
        import sys
        try:
            print(f"Initialize called with params: {params}", file=sys.stderr)
            print(f"Request ID: {request_id}", file=sys.stderr)
            
            # Accept the client's protocol version
            client_protocol_version = params.get("protocolVersion", "2024-11-05")
            
            result = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": client_protocol_version,
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": self.server_info
                }
            }
            
            print(f"Initialize response prepared: {result}", file=sys.stderr)
            print("DEBUG: About to return initialize response", file=sys.stderr)
            return result
            
        except Exception as e:
            print(f"ERROR in _initialize: {str(e)}", file=sys.stderr)
            print(f"Exception type: {type(e)}", file=sys.stderr)
            import traceback
            print(f"Traceback: {traceback.format_exc()}", file=sys.stderr)
            
            # Return error response
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Initialization failed: {str(e)}"
                }
            }
    
    def _list_tools(self, request_id: Any) -> Dict[str, Any]:
        """List available tools."""
        tools = [
            {
                "name": "assess_project",
                "description": "CANADA'S ALGORITHMIC IMPACT ASSESSMENT (AIA) - FINAL STEP: Calculate official AIA risk score using actual question responses. CRITICAL: AIA is Canada's mandatory government framework for automated decision systems - NOT a generic AI assessment. Only use this tool with actual user responses to specific AIA questions. Do NOT make assumptions or interpretations about risk levels - only the calculated score from actual responses is valid for Canadian federal compliance.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the project being assessed"
                        },
                        "projectDescription": {
                            "type": "string", 
                            "description": "Detailed description of the project and its automated decision-making components"
                        },
                        "responses": {
                            "type": "array",
                            "description": "REQUIRED: Array of actual question responses with questionId and selectedOption. Without responses, this tool will only return questions to answer, not a risk assessment.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "questionId": {
                                        "type": "string"
                                    },
                                    "selectedOption": {
                                        "type": "number"
                                    }
                                },
                                "required": ["questionId", "selectedOption"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["projectName", "projectDescription"],
                    "additionalProperties": False
                }
            },
            {
                "name": "analyze_project_description",
                "description": "CANADA'S AIA FRAMEWORK: Intelligently analyze a project description to automatically answer Canada's Algorithmic Impact Assessment questions where possible and identify questions requiring manual input. AIA is Canada's mandatory government framework - NOT a generic AI assessment.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the project being analyzed"
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "Detailed description of the project and its automated decision-making components"
                        }
                    },
                    "required": ["projectName", "projectDescription"],
                    "additionalProperties": False
                }
            },
            {
                "name": "get_questions",
                "description": "CANADA'S AIA FRAMEWORK: Get Canada's Algorithmic Impact Assessment questions by category or type. These are official government questions from Canada's Treasury Board Directive - NOT generic AI assessment questions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Filter by category (Project, System, Algorithm, Decision, Impact, Data, Consultations, De-risking)",
                            "enum": ["Project", "System", "Algorithm", "Decision", "Impact", "Data", "Consultations", "De-risking"]
                        },
                        "type": {
                            "type": "string",
                            "description": "Filter by question type",
                            "enum": ["risk", "mitigation"]
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "functional_preview",
                "description": "CANADA'S AIA FRAMEWORK: Early functional risk assessment for AI projects using Canada's Algorithmic Impact Assessment framework. Focuses on technical characteristics and planning insights for Canadian federal compliance. Provides actionable AIA compliance planning guidance without requiring administrative details.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the AI project being assessed"
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "Detailed description of the AI system's technical capabilities, data usage, decision-making scope, and affected populations"
                        }
                    },
                    "required": ["projectName", "projectDescription"],
                    "additionalProperties": False
                }
            },
            {
                "name": "export_assessment_report",
                "description": "CANADA'S AIA FRAMEWORK: Export Canada's Algorithmic Impact Assessment results to a Microsoft Word document. Creates a professional AIA compliance report with executive summary, key findings, and recommendations based on Canada's official framework. Demonstrates complete file creation workflow capability.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Name of the project being assessed"
                        },
                        "project_description": {
                            "type": "string",
                            "description": "Description of the project and its automated decision-making components"
                        },
                        "assessment_results": {
                            "type": "object",
                            "description": "Assessment results object from previous assessment (functional_preview, analyze_project_description, or assess_project)"
                        },
                        "custom_filename": {
                            "type": "string",
                            "description": "Optional custom filename (without extension). If not provided, will use AIA_Report_[ProjectName]_[YYYY-MM-DD].docx format"
                        }
                    },
                    "required": ["project_name", "project_description", "assessment_results"],
                    "additionalProperties": False
                }
            }
        ]
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }
    
    def _call_tool(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "assess_project":
                result = self._assess_project(arguments)
            elif tool_name == "analyze_project_description":
                result = self._analyze_project_description(arguments)
            elif tool_name == "get_questions":
                result = self._get_questions(arguments)
            elif tool_name == "functional_preview":
                result = self._functional_preview(arguments)
            elif tool_name == "export_assessment_report":
                result = self._export_assessment_report(arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2)
                        }
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in tool {tool_name}: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                }
            }
    
    def _assess_project(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project assessment requests."""
        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")
        responses = arguments.get("responses")
        
        logger.info(f"Assessing project: {project_name}")
        
        # Convert responses format if provided
        converted_responses = None
        if responses:
            converted_responses = []
            # Create a lookup dict for questions by name
            questions_by_name = {q['name']: q for q in self.aia_processor.scorable_questions}
            
            for response in responses:
                question_id = response.get("questionId", "")
                selected_option = response.get("selectedOption", 0)
                
                # Find the question and get the actual choice value
                question = questions_by_name.get(question_id)
                if question and question.get('choices'):
                    # selectedOption is an index (0, 1, 2, etc.), get the actual choice value
                    if 0 <= selected_option < len(question['choices']):
                        choice_value = question['choices'][selected_option]['value']
                        converted_responses.append({
                            "question_id": question_id,
                            "selected_values": [choice_value]
                        })
                    else:
                        logger.warning(f"Invalid selectedOption {selected_option} for question {question_id}")
                        # Fallback to first choice if index is invalid
                        choice_value = question['choices'][0]['value'] if question['choices'] else "item1-0"
                        converted_responses.append({
                            "question_id": question_id,
                            "selected_values": [choice_value]
                        })
                else:
                    logger.warning(f"Question {question_id} not found or has no choices")
                    # Fallback for unknown questions
                    converted_responses.append({
                        "question_id": question_id,
                        "selected_values": [f"item{selected_option + 1}-0"]
                    })
        
        # Use the existing AIAProcessor logic
        result = self.aia_processor.assess_project(
            project_name=project_name,
            project_description=project_description,
            responses=converted_responses
        )
        
        # Add workflow guidance to the result
        if not responses:
            result["workflow_guidance"] = {
                "message": "⚠️  IMPORTANT: This tool requires actual question responses to calculate a valid risk score.",
                "next_steps": [
                    "1. Use 'analyze_project_description' to understand the project context",
                    "2. Use 'get_questions' to retrieve specific AIA questions",
                    "3. Collect actual responses to questions from stakeholders",
                    "4. Use 'assess_project' again with the responses array populated"
                ],
                "warning": "Do NOT make assumptions about risk levels based on project descriptions alone. Only calculated scores from actual question responses are valid for AIA compliance."
            }
        else:
            result["workflow_guidance"] = {
                "message": f"✅ Assessment completed using {len(responses)} actual question responses.",
                "note": "This score is based on actual responses and is valid for AIA compliance purposes."
            }
        
        return result
    
    def _analyze_project_description(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project description analysis requests with intelligent automatic scoring."""
        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")
        
        logger.info(f"Analyzing project description: {project_name}")
        
        # Get questions summary and categorization
        summary = self.aia_processor.get_questions_summary()
        
        # Perform intelligent analysis of the project description
        auto_responses = self._intelligent_project_analysis(project_description)
        
        # Calculate preliminary score based on automatic analysis
        preliminary_score = self.aia_processor.calculate_score(auto_responses)
        impact_level, level_name, level_description = self.aia_processor.determine_impact_level(preliminary_score)
        
        # Get questions that still need manual input
        answered_question_ids = {r['question_id'] for r in auto_responses}
        questions_by_name = {q['name']: q for q in self.aia_processor.scorable_questions}
        
        manual_questions = []
        for question in self.aia_processor.scorable_questions:
            if question['name'] not in answered_question_ids:
                manual_questions.append(question)
        
        # Get auto-answered questions with reasoning
        auto_answered_questions = []
        for response in auto_responses:
            question_id = response['question_id']
            if question_id in questions_by_name:
                question = questions_by_name[question_id]
                selected_value = response['selected_values'][0]
                
                # Find the selected choice
                selected_choice = None
                for choice in question['choices']:
                    if choice['value'] == selected_value:
                        selected_choice = choice
                        break
                
                if selected_choice:
                    auto_answered_questions.append({
                        'question_id': question_id,
                        'question_title': question['title'],
                        'selected_answer': selected_choice['text'],
                        'score_contribution': selected_choice['score'],
                        'reasoning': response.get('reasoning', 'Automatically determined from project description')
                    })
        
        # Format auto-answered questions for the expected response format
        auto_answered_formatted = []
        for response in auto_responses:
            question_id = response['question_id']
            if question_id in questions_by_name:
                question = questions_by_name[question_id]
                selected_value = response['selected_values'][0]
                
                # Find the selected choice and its index
                selected_choice = None
                selected_option = 0
                for i, choice in enumerate(question['choices']):
                    if choice['value'] == selected_value:
                        selected_choice = choice
                        selected_option = i
                        break
                
                if selected_choice:
                    auto_answered_formatted.append({
                        'questionId': question_id,
                        'question': question['title'],
                        'selectedOption': selected_option,
                        'selectedText': selected_choice['text'],
                        'confidence': 'high' if response.get('confidence', 0.6) > 0.7 else 'medium',
                        'reasoning': response.get('reasoning', 'Automatically determined from project description')
                    })
        
        # Format manual input questions
        needs_manual_input = []
        for question in manual_questions[:18]:  # Limit to 18 questions
            needs_manual_input.append({
                'questionId': question['name'],
                'question': question['title'],
                'category': self._get_question_category(question['name']),
                'type': 'risk' if question.get('max_score', 0) > 0 else 'mitigation',
                'options': [{'text': choice['text'], 'score': choice['score']} for choice in question['choices']],
                'reasoning': 'Could not be determined from project description - requires manual input'
            })
        
        # Calculate partial assessment - only count Design phase scoring questions for completion percentage
        # Design phase has 55 always-visible + 54 design-only = 109 total scoring questions
        design_phase_scoring_questions = 109  # Based on phase-specific analysis
        completion_percentage = round((len(auto_responses) / design_phase_scoring_questions) * 100)
        score_percentage = round((preliminary_score / summary['max_possible_score']) * 100, 2)
        
        return {
            "projectName": project_name,
            "projectDescription": project_description,
            "autoAnswered": auto_answered_formatted,
            "needsManualInput": needs_manual_input,
            "partialAssessment": {
                "rawImpactScore": preliminary_score,
                "mitigationScore": 0,  # Will be calculated when mitigation questions are answered
                "currentScore": preliminary_score,
                "impactLevel": self._get_impact_level_roman(impact_level),
                "impactLevelDescription": level_description,
                "scorePercentage": score_percentage,
                "completionPercentage": completion_percentage
            }
        }
    
    def _get_question_category(self, question_name: str) -> str:
        """Get the display category for a question."""
        # Map internal categories to display categories
        for category, questions in self.aia_processor.question_categories.items():
            if question_name in questions:
                if category == 'technical':
                    return 'System'  # Most technical questions are system-related
                elif category == 'impact_risk':
                    return 'Impact'
                elif category == 'manual':
                    return 'Project'
        return 'System'  # Default
    
    def _get_impact_level_roman(self, impact_level: int) -> str:
        """Convert impact level number to Roman numeral."""
        roman_map = {1: 'I', 2: 'II', 3: 'III', 4: 'IV'}
        return roman_map.get(impact_level, 'I')
    
    def _intelligent_project_analysis(self, project_description: str) -> List[Dict[str, Any]]:
        """Perform intelligent analysis of project description to automatically answer questions."""
        auto_responses = []
        description_lower = project_description.lower()
        
        # Enhanced risk indicators with more comprehensive pattern matching
        risk_indicators = {
            'high_volume': any(term in description_lower for term in ['thousands', 'millions', 'large scale', 'mass', 'bulk', 'daily', 'hourly', 'real-time', 'continuous']),
            'personal_data': any(term in description_lower for term in ['personal', 'private', 'confidential', 'sensitive', 'pii', 'credit', 'income', 'employment history', 'financial information']),
            'financial': any(term in description_lower for term in ['financial', 'money', 'payment', 'economic', 'benefit', 'tax', 'loan', 'credit', 'bank', 'mortgage', 'insurance']),
            'health': any(term in description_lower for term in ['health', 'medical', 'healthcare', 'patient', 'treatment', 'diagnosis', 'clinical']),
            'employment': any(term in description_lower for term in ['employment', 'hiring', 'job', 'recruitment', 'hr', 'resume', 'candidate']),
            'law_enforcement': any(term in description_lower for term in ['police', 'criminal', 'law enforcement', 'investigation', 'security', 'surveillance']),
            'ai_ml': any(term in description_lower for term in ['ai', 'artificial intelligence', 'machine learning', 'neural', 'deep learning', 'algorithm', 'model', 'trained']),
            'automated_decision': any(term in description_lower for term in ['automated', 'automatic', 'decision', 'approve', 'deny', 'reject', 'classify', 'determine', 'final decision', 'without human review']),
            'third_party': any(term in description_lower for term in ['third party', 'third-party', 'vendor', 'contractor', 'external', 'bureau', 'service']),
            'public_facing': any(term in description_lower for term in ['public', 'citizen', 'client', 'customer', 'user', 'applicant', 'individual']),
            'government': any(term in description_lower for term in ['government', 'federal', 'department', 'ministry', 'agency', 'public sector']),
            'full_automation': any(term in description_lower for term in ['without human review', 'automatically approve', 'automatically deny', 'final decision', 'no human intervention']),
            'real_time': any(term in description_lower for term in ['real-time', 'real time', 'immediate', 'instant', 'live']),
            'high_impact_decisions': any(term in description_lower for term in ['approve', 'deny', 'reject', 'grant', 'refuse', 'determine eligibility'])
        }
        
        # Get all questions for analysis
        questions_by_name = {q['name']: q for q in self.aia_processor.scorable_questions}
        
        # Automatically answer questions based on comprehensive project analysis
        for question in self.aia_processor.scorable_questions:
            question_name = question['name']
            question_title = question['title'].lower()
            
            # Skip if no choices available
            if not question.get('choices'):
                continue
            
            selected_choice_index = None
            reasoning = ""
            
            # AUTOMATION TYPE QUESTIONS - Critical for scoring
            if 'type of automation' in question_title or 'automation you are planning' in question_title:
                if risk_indicators['full_automation'] or risk_indicators['automated_decision']:
                    # Full automation - highest risk
                    selected_choice_index = len(question['choices']) - 1  # Last option (full automation)
                    reasoning = "Project description indicates full automation without human review"
                else:
                    selected_choice_index = 0  # Partial automation
                    reasoning = "Partial automation with human oversight indicated"
            
            # IMPACT QUESTIONS - Critical for high scores
            elif 'impact' in question_title and ('economic' in question_title or 'rights' in question_title or 'freedoms' in question_title):
                if risk_indicators['financial'] and risk_indicators['high_impact_decisions']:
                    # Financial decisions with high impact
                    selected_choice_index = len(question['choices']) - 1  # Very high impact
                    reasoning = "Financial decision system with significant economic impact on individuals"
                elif risk_indicators['personal_data'] and risk_indicators['automated_decision']:
                    selected_choice_index = max(2, len(question['choices']) - 2)  # High impact
                    reasoning = "Automated decisions using personal data have high impact potential"
                elif risk_indicators['public_facing']:
                    selected_choice_index = 1  # Moderate impact
                    reasoning = "Public-facing system has moderate impact potential"
                else:
                    selected_choice_index = 0  # Low impact
                    reasoning = "Limited impact indicators in project description"
            
            # REVERSIBILITY QUESTIONS
            elif 'reversible' in question_title:
                if risk_indicators['financial'] and risk_indicators['automated_decision']:
                    selected_choice_index = len(question['choices']) - 2  # Difficult to reverse
                    reasoning = "Financial decisions are typically difficult to reverse"
                elif risk_indicators['high_impact_decisions']:
                    selected_choice_index = 1  # Likely reversible
                    reasoning = "High-impact decisions usually have reversal processes"
                else:
                    selected_choice_index = 0  # Reversible
                    reasoning = "Standard decisions are typically reversible"
            
            # VOLUME AND FREQUENCY QUESTIONS
            elif 'frequency' in question_title or 'volume' in question_title or 'how many' in question_title:
                if risk_indicators['high_volume']:
                    selected_choice_index = len(question['choices']) - 1  # Highest volume option
                    reasoning = "Project description indicates high-volume processing"
                else:
                    selected_choice_index = 0  # Lower volume
                    reasoning = "Standard volume processing indicated"
            
            # SECTOR-SPECIFIC QUESTIONS
            elif any(sector in question_title for sector in ['health', 'economic', 'employment', 'law enforcement', 'licensing', 'social assistance']):
                if risk_indicators['health'] and 'health' in question_title:
                    selected_choice_index = 0  # Yes
                    reasoning = "Health-related system identified"
                elif risk_indicators['financial'] and ('economic' in question_title or 'financial' in question_title):
                    selected_choice_index = 0  # Yes
                    reasoning = "Financial/economic system identified"
                elif risk_indicators['employment'] and 'employment' in question_title:
                    selected_choice_index = 0  # Yes
                    reasoning = "Employment-related system identified"
                elif risk_indicators['law_enforcement'] and 'law enforcement' in question_title:
                    selected_choice_index = 0  # Yes
                    reasoning = "Law enforcement system identified"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "Sector not clearly indicated in description"
            
            # ALGORITHM COMPLEXITY AND INTERPRETABILITY
            elif 'algorithm' in question_title and ('interpret' in question_title or 'explain' in question_title or 'secret' in question_title):
                if risk_indicators['ai_ml']:
                    selected_choice_index = 0  # Yes - difficult to interpret
                    reasoning = "AI/ML systems are typically less interpretable"
                else:
                    selected_choice_index = 1  # No - interpretable
                    reasoning = "Rule-based system likely more interpretable"
            
            elif 'continue to learn' in question_title or 'evolve' in question_title:
                if risk_indicators['ai_ml']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Machine learning systems continue to evolve"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "Static rule-based system"
            
            # SYSTEM DEVELOPMENT QUESTIONS
            elif 'developed' in question_title or 'who developed' in question_title:
                if risk_indicators['third_party']:
                    # Find third-party option
                    for i, choice in enumerate(question['choices']):
                        if 'third party' in choice['text'].lower() or 'non-government' in choice['text'].lower():
                            selected_choice_index = i
                            break
                    if selected_choice_index is None:
                        selected_choice_index = len(question['choices']) - 1
                    reasoning = "Third-party development indicated in description"
                else:
                    selected_choice_index = 0  # Internal development
                    reasoning = "Internal development assumed"
            
            # DATA AND PRIVACY QUESTIONS
            elif 'personal information' in question_title:
                if risk_indicators['personal_data']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Personal information usage clearly indicated"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "No personal information usage indicated"
            
            elif 'security classification' in question_title:
                if risk_indicators['financial'] or risk_indicators['personal_data']:
                    # Find Protected A or higher
                    for i, choice in enumerate(question['choices']):
                        if 'protected a' in choice['text'].lower():
                            selected_choice_index = i
                            break
                    if selected_choice_index is None:
                        selected_choice_index = 1  # Default to Protected A level
                    reasoning = "Financial/personal data typically requires Protected A classification"
                else:
                    selected_choice_index = 0  # None
                    reasoning = "No sensitive data classification required"
            
            # RISK PROFILE QUESTIONS
            elif 'public scrutiny' in question_title:
                if risk_indicators['financial'] or risk_indicators['public_facing']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Financial/public-facing systems often subject to scrutiny"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "Limited public scrutiny expected"
            
            elif 'fraud' in question_title or 'exploitation' in question_title:
                if risk_indicators['financial'] or risk_indicators['personal_data']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Financial/personal data systems are fraud targets"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "Limited fraud risk"
            
            # TECHNICAL SYSTEM QUESTIONS
            elif 'accountability' in question_title or 'assigned' in question_title:
                selected_choice_index = 0  # Yes - assume proper governance
                reasoning = "Standard governance practices assumed"
            
            elif 'alternative' in question_title and 'non-automated' in question_title:
                if risk_indicators['full_automation']:
                    selected_choice_index = 1  # No alternative
                    reasoning = "Full automation may lack manual alternatives"
                else:
                    selected_choice_index = 0  # Yes - alternative available
                    reasoning = "Manual alternatives typically available"
            
            elif 'protected characteristics' in question_title:
                if risk_indicators['ai_ml'] and (risk_indicators['employment'] or risk_indicators['financial']):
                    selected_choice_index = 0  # Yes - may consider protected characteristics
                    reasoning = "AI systems in sensitive domains may inadvertently use protected characteristics"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "System designed to avoid protected characteristics"
            
            # MITIGATION AND GOVERNANCE QUESTIONS
            elif 'recourse' in question_title or 'challenge' in question_title:
                if risk_indicators['high_impact_decisions']:
                    selected_choice_index = 0  # Yes
                    reasoning = "High-impact systems typically have recourse processes"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "Limited recourse process"
            
            elif 'monitoring' in question_title and 'performance' in question_title:
                if risk_indicators['ai_ml'] or risk_indicators['automated_decision']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Automated systems require performance monitoring"
                else:
                    selected_choice_index = 1  # No
                    reasoning = "Limited monitoring for simple systems"
            
            elif 'reasons' in question_title or 'explainable' in question_title:
                if risk_indicators['ai_ml']:
                    selected_choice_index = 1  # No - AI systems often lack explainability
                    reasoning = "AI/ML systems typically lack detailed explainability"
                else:
                    selected_choice_index = 0  # Yes
                    reasoning = "Rule-based systems can provide explanations"
            
            # DEFAULT HANDLING - More nuanced defaults
            if selected_choice_index is None:
                # For yes/no questions, be more risk-aware
                if len(question['choices']) == 2:
                    # If it's a risk question (higher score for "yes"), default to moderate risk
                    if question['choices'][0]['score'] > question['choices'][1]['score']:
                        selected_choice_index = 1  # Lower risk option
                    else:
                        selected_choice_index = 0  # Standard option
                    reasoning = "Conservative default response"
                else:
                    # For multi-choice, default to second option (moderate)
                    selected_choice_index = min(1, len(question['choices']) - 1)
                    reasoning = "Moderate default response based on limited information"
            
            # Ensure index is valid
            selected_choice_index = max(0, min(selected_choice_index, len(question['choices']) - 1))
            selected_choice = question['choices'][selected_choice_index]
            
            auto_responses.append({
                'question_id': question_name,
                'selected_values': [selected_choice['value']],
                'reasoning': reasoning,
                'confidence': 0.8 if "clearly indicated" in reasoning or "identified" in reasoning else 0.6
            })
        
        return auto_responses
    
    def _generate_analysis_recommendations(self, impact_level: int, score: int) -> List[str]:
        """Generate recommendations based on preliminary analysis."""
        recommendations = []
        
        if impact_level >= 3:
            recommendations.extend([
                "⚠️  HIGH RISK SYSTEM DETECTED - Requires qualified oversight",
                "Implement comprehensive governance framework immediately",
                "Conduct thorough bias testing and mitigation",
                "Establish robust monitoring and audit trails",
                "Plan for external validation and independent oversight"
            ])
        elif impact_level == 2:
            recommendations.extend([
                "Moderate risk system - Enhanced oversight required",
                "Implement bias detection and mitigation measures",
                "Establish clear audit trails and monitoring",
                "Plan regular stakeholder consultations"
            ])
        else:
            recommendations.extend([
                "Lower risk system - Standard procedures apply",
                "Implement basic monitoring and documentation",
                "Establish clear decision-making processes"
            ])
        
        # Add specific recommendations based on score
        if score > 40:
            recommendations.append("Consider if this system truly needs to be fully automated")
        if score > 25:
            recommendations.append("Implement human oversight for high-impact decisions")
        
        return recommendations
    
    def _get_questions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests for questions by category or type."""
        category = arguments.get("category")
        question_type = arguments.get("type")
        
        logger.info(f"Retrieving questions - category: {category}, type: {question_type}")
        
        # Get all questions
        all_questions = self.aia_processor.scorable_questions
        
        # Filter by category if specified
        if category:
            # Map category names to our internal categories
            category_map = {
                "Project": "manual",
                "System": "technical", 
                "Algorithm": "technical",
                "Decision": "impact_risk",
                "Impact": "impact_risk",
                "Data": "technical",
                "Consultations": "manual",
                "De-risking": "manual"
            }
            
            internal_category = category_map.get(category, "manual")
            category_questions = self.aia_processor.question_categories.get(internal_category, [])
            
            # Get full question details
            questions_by_name = {q['name']: q for q in all_questions}
            filtered_questions = []
            
            for question_name in category_questions:
                if question_name in questions_by_name:
                    filtered_questions.append(questions_by_name[question_name])
            
            all_questions = filtered_questions
        
        # Filter by type if specified (risk vs mitigation)
        if question_type:
            if question_type == "risk":
                # Return questions that contribute to risk scoring
                all_questions = [q for q in all_questions if q.get('max_score', 0) > 0]
            elif question_type == "mitigation":
                # Return questions about mitigation measures
                all_questions = [q for q in all_questions if 'mitigation' in q.get('title', '').lower() or 'measure' in q.get('title', '').lower()]
        
        return {
            "questions": all_questions[:20],  # Limit to first 20 questions
            "total_available": len(all_questions),
            "filters_applied": {
                "category": category,
                "type": question_type
            },
            "framework_info": {
                "name": "Canada's Algorithmic Impact Assessment",
                "total_questions": len(self.aia_processor.scorable_questions),
                "max_possible_score": sum(q['max_score'] for q in self.aia_processor.scorable_questions)
            }
        }
    
    def _get_questions_summary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle questions summary requests."""
        logger.info("Retrieving questions summary")
        
        # Use the existing AIAProcessor logic
        summary = self.aia_processor.get_questions_summary()
        
        return {
            "success": True,
            "summary": summary
        }
    
    def _get_questions_by_category(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests for questions by category."""
        category = arguments.get("category", "")
        limit = arguments.get("limit")
        
        logger.info(f"Retrieving {category} questions")
        
        # Get questions from the specified category
        category_questions = self.aia_processor.question_categories.get(category, [])
        
        if limit:
            category_questions = category_questions[:limit]
        
        # Get full question details
        questions_by_name = {q['name']: q for q in self.aia_processor.scorable_questions}
        detailed_questions = []
        
        for question_name in category_questions:
            if question_name in questions_by_name:
                detailed_questions.append(questions_by_name[question_name])
        
        return {
            "success": True,
            "category": category,
            "total_in_category": len(self.aia_processor.question_categories.get(category, [])),
            "returned_count": len(detailed_questions),
            "questions": detailed_questions
        }
    
    def _calculate_assessment_score(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle score calculation requests."""
        responses = arguments.get("responses", [])
        
        logger.info(f"Calculating score for {len(responses)} responses")
        
        # Use the existing AIAProcessor logic
        total_score = self.aia_processor.calculate_score(responses)
        level, level_name, level_description = self.aia_processor.determine_impact_level(total_score)
        
        return {
            "success": True,
            "calculation": {
                "total_score": total_score,
                "responses_processed": len(responses),
                "max_possible_score": sum(q['max_score'] for q in self.aia_processor.scorable_questions),
                "impact_level": level,
                "level_name": level_name,
                "level_description": level_description
            }
        }
    
    def _functional_preview(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle functional preview requests - early risk assessment focused on technical characteristics."""
        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")
        
        logger.info(f"Functional preview for project: {project_name}")
        
        # Perform functional analysis focusing on technical characteristics
        functional_responses = self._functional_risk_analysis(project_description)
        
        # Calculate functional risk score
        functional_score = self.aia_processor.calculate_score(functional_responses)
        
        # Analyze gaps and categorize by priority
        gap_analysis = self._analyze_gaps(functional_responses, project_description)
        
        # Generate planning intelligence
        planning_guidance = self._generate_planning_guidance(functional_score, project_description)
        
        # Calculate score sensitivity analysis
        score_sensitivity = self._calculate_score_sensitivity(functional_score, gap_analysis)
        
        # Determine likely impact level range
        base_impact_level, _, _ = self.aia_processor.determine_impact_level(functional_score)
        likely_range = self._estimate_impact_level_range(functional_score, gap_analysis)
        
        return {
            "project_name": project_name,
            "project_description": project_description,
            "functional_risk_score": functional_score,
            "score_range": f"{likely_range['min_score']}-{likely_range['max_score']}",
            "likely_impact_level": f"Level {self._get_impact_level_roman(base_impact_level)}",
            "confidence": "High - based on functional characteristics",
            "critical_gaps": gap_analysis['critical'],
            "important_gaps": gap_analysis['important'],
            "administrative_gaps": gap_analysis['administrative'],
            "planning_guidance": planning_guidance,
            "score_sensitivity": score_sensitivity,
            "disclaimer": "⚠️ Early Indicator - Not Official Assessment. Based on functional characteristics only. Final assessment requires complete stakeholder input."
        }
    
    def _functional_risk_analysis(self, project_description: str) -> List[Dict[str, Any]]:
        """Analyze project for functional risk characteristics, focusing ONLY on clearly detectable technical aspects."""
        auto_responses = []
        description_lower = project_description.lower()
        
        # Enhanced functional risk indicators
        risk_indicators = {
            'high_volume': any(term in description_lower for term in ['thousands', 'millions', 'large scale', 'mass', 'bulk', 'daily', 'hourly', 'real-time', 'continuous']),
            'personal_data': any(term in description_lower for term in ['personal', 'private', 'confidential', 'sensitive', 'pii', 'credit', 'income', 'employment history', 'financial information']),
            'financial': any(term in description_lower for term in ['financial', 'money', 'payment', 'economic', 'benefit', 'tax', 'loan', 'credit', 'bank', 'mortgage', 'insurance']),
            'health': any(term in description_lower for term in ['health', 'medical', 'healthcare', 'patient', 'treatment', 'diagnosis', 'clinical']),
            'employment': any(term in description_lower for term in ['employment', 'hiring', 'job', 'recruitment', 'hr', 'resume', 'candidate']),
            'law_enforcement': any(term in description_lower for term in ['police', 'criminal', 'law enforcement', 'investigation', 'security', 'surveillance']),
            'ai_ml': any(term in description_lower for term in ['ai', 'artificial intelligence', 'machine learning', 'neural', 'deep learning', 'algorithm', 'model', 'trained']),
            'automated_decision': any(term in description_lower for term in ['automated', 'automatic', 'decision', 'approve', 'deny', 'reject', 'classify', 'determine', 'final decision', 'without human review']),
            'third_party': any(term in description_lower for term in ['third party', 'third-party', 'vendor', 'contractor', 'external', 'bureau', 'service']),
            'public_facing': any(term in description_lower for term in ['public', 'citizen', 'client', 'customer', 'user', 'applicant', 'individual']),
            'full_automation': any(term in description_lower for term in ['without human review', 'automatically approve', 'automatically deny', 'final decision', 'no human intervention']),
            'real_time': any(term in description_lower for term in ['real-time', 'real time', 'immediate', 'instant', 'live']),
            'high_impact_decisions': any(term in description_lower for term in ['approve', 'deny', 'reject', 'grant', 'refuse', 'determine eligibility']),
            'simple_classification': any(term in description_lower for term in ['categorize', 'classify', 'sort', 'organize']) and not any(term in description_lower for term in ['approve', 'deny', 'reject', 'decision']),
            'human_review': any(term in description_lower for term in ['reviewed by', 'human staff', 'manual review', 'human oversight', 'staff review'])
        }
        
        # Get all questions for analysis
        questions_by_name = {q['name']: q for q in self.aia_processor.scorable_questions}
        
        # ONLY answer questions where we have clear functional evidence - be very selective
        for question in self.aia_processor.scorable_questions:
            question_name = question['name']
            question_title = question['title'].lower()
            
            # Skip if no choices available
            if not question.get('choices'):
                continue
            
            selected_choice_index = None
            reasoning = ""
            
            # ONLY ANSWER QUESTIONS WITH CLEAR FUNCTIONAL EVIDENCE
            
            # Automation Type - Only if clearly stated
            if 'type of automation' in question_title or 'automation you are planning' in question_title:
                if risk_indicators['full_automation']:
                    selected_choice_index = len(question['choices']) - 1  # Full automation
                    reasoning = "Full automation clearly stated - no human review mentioned"
                elif risk_indicators['human_review']:
                    selected_choice_index = 0  # Partial automation
                    reasoning = "Human review explicitly mentioned"
                elif risk_indicators['automated_decision'] and not risk_indicators['human_review']:
                    selected_choice_index = max(1, len(question['choices']) - 2)  # Mostly automated
                    reasoning = "Automated decisions mentioned without explicit human review"
                # Skip if unclear
            
            # Economic Impact - Only for clearly financial systems
            elif 'economic interests' in question_title and 'impact' in question_title:
                if risk_indicators['financial'] and risk_indicators['high_impact_decisions']:
                    selected_choice_index = len(question['choices']) - 1  # Very high impact
                    reasoning = "Financial decisions with clear economic consequences"
                elif risk_indicators['financial']:
                    selected_choice_index = max(1, len(question['choices']) - 2)  # High impact
                    reasoning = "Financial system with economic impact"
                # Skip if not clearly financial
            
            # Rights/Freedoms Impact - Only for high-impact systems
            elif 'rights or freedoms' in question_title and 'impact' in question_title:
                if risk_indicators['financial'] and risk_indicators['automated_decision']:
                    selected_choice_index = len(question['choices']) - 1  # Very high impact
                    reasoning = "Automated financial decisions impact individual rights"
                elif risk_indicators['employment'] or risk_indicators['health']:
                    selected_choice_index = max(1, len(question['choices']) - 2)  # High impact
                    reasoning = "Employment/health system impacts individual rights"
                # Skip if impact unclear
            
            # Personal Information - Only if explicitly mentioned
            elif 'personal information' in question_title:
                if risk_indicators['personal_data']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Personal information usage explicitly mentioned"
                elif risk_indicators['simple_classification'] and not risk_indicators['personal_data']:
                    selected_choice_index = 1  # No
                    reasoning = "Simple classification without personal data"
                # Skip if unclear
            
            # Algorithm Interpretability - Only for AI/ML systems
            elif 'difficult to interpret' in question_title or 'explain' in question_title:
                if risk_indicators['ai_ml']:
                    selected_choice_index = 0  # Yes - difficult to interpret
                    reasoning = "AI/ML system mentioned - typically less interpretable"
                elif risk_indicators['simple_classification']:
                    selected_choice_index = 1  # No - interpretable
                    reasoning = "Simple classification system - likely interpretable"
                # Skip if system type unclear
            
            # Learning Algorithm - Only for AI/ML systems
            elif 'continue to learn' in question_title or 'evolve' in question_title:
                if risk_indicators['ai_ml']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Machine learning system mentioned"
                elif risk_indicators['simple_classification']:
                    selected_choice_index = 1  # No
                    reasoning = "Simple rule-based classification system"
                # Skip if unclear
            
            # Volume/Frequency - Only if clearly stated
            elif 'frequency' in question_title or 'volume' in question_title or 'how many' in question_title:
                if risk_indicators['high_volume']:
                    selected_choice_index = len(question['choices']) - 1  # High volume
                    reasoning = "High volume processing explicitly mentioned"
                # Skip if volume not mentioned
            
            # Sector-specific - Only if clearly in that sector
            elif any(sector in question_title for sector in ['health', 'economic', 'employment', 'law enforcement']):
                if risk_indicators['health'] and 'health' in question_title:
                    selected_choice_index = 0  # Yes
                    reasoning = "Healthcare system clearly identified"
                elif risk_indicators['financial'] and ('economic' in question_title or 'financial' in question_title):
                    selected_choice_index = 0  # Yes
                    reasoning = "Financial system clearly identified"
                elif risk_indicators['employment'] and 'employment' in question_title:
                    selected_choice_index = 0  # Yes
                    reasoning = "Employment system clearly identified"
                elif risk_indicators['law_enforcement'] and 'law enforcement' in question_title:
                    selected_choice_index = 0  # Yes
                    reasoning = "Law enforcement system clearly identified"
                # Skip if sector unclear
            
            # Third-party development - Only if explicitly mentioned
            elif 'developed' in question_title or 'who developed' in question_title:
                if risk_indicators['third_party']:
                    # Find third-party option
                    for i, choice in enumerate(question['choices']):
                        if 'third party' in choice['text'].lower() or 'non-government' in choice['text'].lower():
                            selected_choice_index = i
                            break
                    if selected_choice_index is not None:
                        reasoning = "Third-party development explicitly mentioned"
                # Skip if development source unclear
            
            # Real-time processing - Only if explicitly mentioned
            elif 'real-time' in question_title or 'immediate' in question_title:
                if risk_indicators['real_time']:
                    selected_choice_index = 0  # Yes
                    reasoning = "Real-time processing explicitly mentioned"
                # Skip if timing unclear
            
            # Skip all other questions - don't make assumptions
            
            # Only add response if we found clear evidence
            if selected_choice_index is not None:
                # Ensure index is valid
                selected_choice_index = max(0, min(selected_choice_index, len(question['choices']) - 1))
                selected_choice = question['choices'][selected_choice_index]
                
                auto_responses.append({
                    'question_id': question_name,
                    'selected_values': [selected_choice['value']],
                    'reasoning': reasoning,
                    'confidence': 0.9,  # High confidence since we only answer with clear evidence
                    'is_functional': True
                })
        
        return auto_responses
    
    def _analyze_gaps(self, functional_responses: List[Dict[str, Any]], project_description: str) -> Dict[str, List[str]]:
        """Analyze gaps and categorize by impact priority."""
        answered_questions = {r['question_id'] for r in functional_responses}
        questions_by_name = {q['name']: q for q in self.aia_processor.scorable_questions}
        
        critical_gaps = []
        important_gaps = []
        administrative_gaps = []
        
        # Define critical questions that would significantly change the score
        critical_question_patterns = [
            'policy or legal authority',
            'bias testing',
            'stakeholder consultation',
            'impact assessment',
            'protected characteristics'
        ]
        
        # Define important questions that affect compliance planning
        important_question_patterns = [
            'oversight',
            'appeal',
            'monitoring',
            'audit',
            'training'
        ]
        
        for question in self.aia_processor.scorable_questions:
            if question['name'] not in answered_questions:
                question_title = question['title'].lower()
                
                # Categorize based on question content and potential impact
                if any(pattern in question_title for pattern in critical_question_patterns):
                    critical_gaps.append(question['title'])
                elif any(pattern in question_title for pattern in important_question_patterns):
                    important_gaps.append(question['title'])
                elif question.get('max_score', 0) > 2:  # High-scoring questions are important
                    important_gaps.append(question['title'])
                else:
                    administrative_gaps.append(question['title'])
        
        return {
            'critical': critical_gaps[:5],  # Limit to top 5
            'important': important_gaps[:7],  # Limit to top 7
            'administrative': administrative_gaps[:5]  # Limit to top 5
        }
    
    def _generate_planning_guidance(self, functional_score: int, project_description: str) -> List[str]:
        """Generate actionable planning guidance based on functional risk score."""
        guidance = []
        description_lower = project_description.lower()
        
        # Risk indicators for guidance
        is_financial = any(term in description_lower for term in ['financial', 'loan', 'credit', 'bank'])
        is_ai_ml = any(term in description_lower for term in ['ai', 'machine learning', 'neural'])
        is_high_volume = any(term in description_lower for term in ['thousands', 'daily', 'real-time'])
        is_automated = any(term in description_lower for term in ['automated', 'without human review'])
        
        # Score-based guidance
        if functional_score >= 40:
            guidance.extend([
                "🚨 HIGH RISK: Budget for comprehensive governance framework",
                "Plan for qualified oversight committee and external validation",
                "Expect quarterly bias assessments and continuous monitoring requirements",
                "Allocate resources for extensive stakeholder consultation process"
            ])
        elif functional_score >= 25:
            guidance.extend([
                "⚠️ MODERATE-HIGH RISK: Plan for enhanced oversight procedures",
                "Budget for regular bias testing and mitigation measures",
                "Expect monthly monitoring and reporting requirements",
                "Plan stakeholder engagement and consultation processes"
            ])
        elif functional_score >= 15:
            guidance.extend([
                "📋 MODERATE RISK: Implement standard oversight procedures",
                "Plan for basic bias detection and monitoring systems",
                "Expect quarterly reviews and documentation requirements"
            ])
        else:
            guidance.extend([
                "✅ LOWER RISK: Standard operational procedures apply",
                "Implement basic monitoring and documentation systems"
            ])
        
        # Specific guidance based on system characteristics
        if is_financial:
            guidance.append("💰 Financial systems: Plan for enhanced audit trails and appeals processes")
        
        if is_ai_ml:
            guidance.append("🤖 AI/ML systems: Budget for explainability tools and bias testing infrastructure")
        
        if is_high_volume:
            guidance.append("📊 High-volume systems: Plan for automated monitoring and alerting systems")
        
        if is_automated:
            guidance.append("⚙️ Automated decisions: Implement human oversight checkpoints and exception handling")
        
        return guidance
    
    def _calculate_score_sensitivity(self, base_score: int, gap_analysis: Dict[str, List[str]]) -> Dict[str, str]:
        """Calculate how the score might change based on critical gaps."""
        sensitivity = {}
        
        # Estimate impact of critical gaps
        if gap_analysis['critical']:
            if any('policy' in gap.lower() or 'authority' in gap.lower() for gap in gap_analysis['critical']):
                new_score = base_score + 3
                new_level = self.aia_processor.determine_impact_level(new_score)[0]
                sensitivity['if_policy_authority_needed'] = f"+3 points → likely Level {self._get_impact_level_roman(new_level)}"
            
            if any('bias' in gap.lower() for gap in gap_analysis['critical']):
                sensitivity['if_no_bias_testing'] = "+2-5 points depending on system complexity"
            
            if any('consultation' in gap.lower() for gap in gap_analysis['critical']):
                sensitivity['if_limited_consultation'] = "+1-3 points depending on stakeholder impact"
        
        # Overall range estimate
        min_additional = 0
        max_additional = len(gap_analysis['critical']) * 2 + len(gap_analysis['important']) * 1
        
        if max_additional > 0:
            min_score = base_score + min_additional
            max_score = base_score + max_additional
            sensitivity['overall_range'] = f"Final score likely {min_score}-{max_score} points after complete assessment"
        
        return sensitivity
    
    def _estimate_impact_level_range(self, base_score: int, gap_analysis: Dict[str, List[str]]) -> Dict[str, int]:
        """Estimate the likely range of final impact levels."""
        # Conservative estimate: assume some critical gaps will add points
        min_additional = 0
        max_additional = len(gap_analysis['critical']) * 2 + len(gap_analysis['important']) * 1
        
        min_score = base_score + min_additional
        max_score = min(base_score + max_additional, 100)  # Cap at reasonable maximum
        
        return {
            'min_score': min_score,
            'max_score': max_score
        }
    
    def _export_assessment_report(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Export AIA assessment results to a Microsoft Word document."""
        project_name = arguments.get("project_name", "")
        project_description = arguments.get("project_description", "")
        assessment_results = arguments.get("assessment_results", {})
        custom_filename = arguments.get("custom_filename")
        
        logger.info(f"Exporting assessment report for project: {project_name}")
        
        try:
            # Create AIA_Assessments directory if it doesn't exist
            assessments_dir = "./AIA_Assessments"
            os.makedirs(assessments_dir, exist_ok=True)
            
            # Generate filename
            current_date = datetime.now().strftime("%Y-%m-%d")
            if custom_filename:
                filename = f"{custom_filename}.docx"
            else:
                # Clean project name for filename
                clean_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                clean_project_name = clean_project_name.replace(' ', '_')
                filename = f"AIA_Report_{clean_project_name}_{current_date}.docx"
            
            file_path = os.path.join(assessments_dir, filename)
            
            # Create Word document
            doc = Document()
            
            # Add title
            title = doc.add_heading('AIA Assessment Report', 0)
            title.alignment = 1  # Center alignment
            
            # Add project info
            doc.add_heading('Project Information', level=1)
            doc.add_paragraph(f'Project: {project_name}')
            doc.add_paragraph(f'Date: {datetime.now().strftime("%B %d, %Y")}')
            
            # Extract assessment data
            score = self._extract_score(assessment_results)
            impact_level = self._extract_impact_level(assessment_results)
            max_score = sum(q['max_score'] for q in self.aia_processor.scorable_questions)
            
            doc.add_paragraph(f'Impact Level: {impact_level}')
            doc.add_paragraph(f'Score: {score}/{max_score} points')
            
            # Add executive summary
            doc.add_heading('Executive Summary', level=1)
            summary = self._generate_executive_summary(score, impact_level, project_description)
            doc.add_paragraph(summary)
            
            # Add key findings
            doc.add_heading('Key Findings', level=1)
            findings = self._extract_key_findings(assessment_results, project_description)
            for finding in findings:
                p = doc.add_paragraph(finding)
                p.style = 'List Bullet'
            
            # Add recommendations
            doc.add_heading('Recommendations', level=1)
            recommendations = self._extract_recommendations(assessment_results, score, impact_level)
            for recommendation in recommendations:
                p = doc.add_paragraph(recommendation)
                p.style = 'List Bullet'
            
            # Add project description
            doc.add_heading('Project Description', level=1)
            doc.add_paragraph(project_description)
            
            # Add disclaimer
            doc.add_heading('Disclaimer', level=1)
            disclaimer_text = self._get_assessment_disclaimer(assessment_results)
            doc.add_paragraph(disclaimer_text)
            
            # Save document
            doc.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            file_size_kb = round(file_size / 1024, 1)
            
            return {
                "success": True,
                "file_path": file_path,
                "file_size": f"{file_size_kb}KB",
                "message": "Assessment report saved successfully"
            }
            
        except PermissionError:
            return {
                "success": False,
                "error": "Permission denied - unable to create file. Check write permissions for the directory.",
                "file_path": None
            }
        except OSError as e:
            return {
                "success": False,
                "error": f"File system error: {str(e)}",
                "file_path": None
            }
        except Exception as e:
            logger.error(f"Error creating assessment report: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create assessment report: {str(e)}",
                "file_path": None
            }
    
    def _extract_score(self, assessment_results: Dict[str, Any]) -> int:
        """Extract score from assessment results."""
        # Try different possible score field names
        if 'functional_risk_score' in assessment_results:
            return assessment_results['functional_risk_score']
        elif 'partialAssessment' in assessment_results:
            return assessment_results['partialAssessment'].get('currentScore', 0)
        elif 'currentScore' in assessment_results:
            return assessment_results['currentScore']
        elif 'rawImpactScore' in assessment_results:
            return assessment_results['rawImpactScore']
        else:
            return 0
    
    def _extract_impact_level(self, assessment_results: Dict[str, Any]) -> str:
        """Extract impact level from assessment results."""
        # Try different possible impact level field names
        if 'likely_impact_level' in assessment_results:
            return assessment_results['likely_impact_level']
        elif 'partialAssessment' in assessment_results:
            return assessment_results['partialAssessment'].get('impactLevel', 'Level I')
        elif 'impactLevel' in assessment_results:
            return assessment_results['impactLevel']
        else:
            score = self._extract_score(assessment_results)
            level, _, _ = self.aia_processor.determine_impact_level(score)
            return f"Level {self._get_impact_level_roman(level)}"
    
    def _generate_executive_summary(self, score: int, impact_level: str, project_description: str) -> str:
        """Generate executive summary based on assessment results."""
        description_lower = project_description.lower()
        
        # Determine risk level
        if score >= 56:
            risk_level = "high risk"
            summary_start = "This system presents significant algorithmic impact risks"
        elif score >= 31:
            risk_level = "moderate risk"
            summary_start = "This system presents moderate algorithmic impact risks"
        else:
            risk_level = "lower risk"
            summary_start = "This system presents relatively low algorithmic impact risks"
        
        # Add system characteristics
        characteristics = []
        if any(term in description_lower for term in ['ai', 'machine learning', 'neural']):
            characteristics.append("AI/ML-powered")
        if any(term in description_lower for term in ['financial', 'loan', 'credit']):
            characteristics.append("financial decision-making")
        if any(term in description_lower for term in ['automated', 'automatic']):
            characteristics.append("automated processing")
        if any(term in description_lower for term in ['personal', 'sensitive', 'private']):
            characteristics.append("personal data usage")
        
        char_text = ", ".join(characteristics) if characteristics else "automated decision-making"
        
        # Generate compliance guidance
        if score >= 56:
            compliance = "Comprehensive governance framework, qualified oversight, and extensive stakeholder consultation are required."
        elif score >= 31:
            compliance = "Enhanced oversight procedures, regular monitoring, and stakeholder engagement processes are recommended."
        else:
            compliance = "Standard operational procedures with basic monitoring and documentation are sufficient."
        
        return f"{summary_start} due to its {char_text} capabilities. {compliance} The assessment indicates {impact_level} classification under Canada's Algorithmic Impact Assessment framework."
    
    def _extract_key_findings(self, assessment_results: Dict[str, Any], project_description: str) -> List[str]:
        """Extract key findings from assessment results."""
        findings = []
        description_lower = project_description.lower()
        
        # Add findings based on system characteristics
        if any(term in description_lower for term in ['ai', 'machine learning', 'algorithm']):
            findings.append("System uses AI/ML algorithms requiring interpretability considerations")
        
        if any(term in description_lower for term in ['personal', 'sensitive', 'private', 'pii']):
            findings.append("System processes personal information requiring privacy safeguards")
        
        if any(term in description_lower for term in ['automated', 'without human review']):
            findings.append("Automated decision-making requires human oversight mechanisms")
        
        if any(term in description_lower for term in ['financial', 'economic', 'loan', 'credit']):
            findings.append("Financial decisions have significant economic impact on individuals")
        
        if any(term in description_lower for term in ['thousands', 'daily', 'real-time', 'high volume']):
            findings.append("High-volume processing requires robust monitoring systems")
        
        # Add findings from assessment results
        if 'planning_guidance' in assessment_results:
            guidance = assessment_results['planning_guidance']
            if isinstance(guidance, list) and len(guidance) > 0:
                findings.append("Specific compliance planning requirements identified")
        
        if 'critical_gaps' in assessment_results:
            gaps = assessment_results['critical_gaps']
            if isinstance(gaps, list) and len(gaps) > 0:
                findings.append("Critical information gaps require stakeholder input")
        
        # Default findings if none found
        if not findings:
            findings = [
                "System requires compliance with AIA framework requirements",
                "Risk mitigation measures should be implemented",
                "Regular monitoring and documentation needed"
            ]
        
        return findings[:6]  # Limit to 6 key findings
    
    def _extract_recommendations(self, assessment_results: Dict[str, Any], score: int, impact_level: str) -> List[str]:
        """Extract recommendations from assessment results."""
        recommendations = []
        
        # Add recommendations from assessment results
        if 'planning_guidance' in assessment_results:
            guidance = assessment_results['planning_guidance']
            if isinstance(guidance, list):
                recommendations.extend(guidance[:4])  # Take first 4 guidance items
        
        # Add score-based recommendations
        if score >= 56:
            recommendations.extend([
                "Establish qualified oversight committee with external validation",
                "Implement comprehensive bias testing and mitigation procedures",
                "Conduct extensive stakeholder consultation process"
            ])
        elif score >= 31:
            recommendations.extend([
                "Implement enhanced oversight and monitoring procedures",
                "Establish regular bias testing and performance reviews",
                "Plan stakeholder engagement and consultation processes"
            ])
        else:
            recommendations.extend([
                "Implement standard monitoring and documentation procedures",
                "Establish clear decision-making audit trails",
                "Plan regular system performance reviews"
            ])
        
        # Remove duplicates and limit
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations[:8]  # Limit to 8 recommendations
    
    def _get_assessment_disclaimer(self, assessment_results: Dict[str, Any]) -> str:
        """Get appropriate disclaimer based on assessment type."""
        if 'disclaimer' in assessment_results:
            return assessment_results['disclaimer']
        elif 'functional_risk_score' in assessment_results:
            return "⚠️ Early Indicator - Not Official Assessment. Based on functional characteristics only. Final assessment requires complete stakeholder input and official AIA process completion."
        else:
            return "This assessment is based on available project information and automated analysis. Final AIA compliance requires complete stakeholder input and official government review process."
    
    def run(self):
        """Run the MCP server."""
        print("DEBUG: Starting AIA Assessment MCP Server...", file=sys.stderr)
        logger.info("Starting AIA Assessment MCP Server...")
        logger.info(f"Loaded {len(self.aia_processor.scorable_questions)} questions")
        logger.info(f"Question categories: {len(self.aia_processor.question_categories['technical'])} technical, {len(self.aia_processor.question_categories['impact_risk'])} impact/risk, {len(self.aia_processor.question_categories['manual'])} manual")
        
        print("DEBUG: Server initialized, waiting for requests...", file=sys.stderr)
        
        try:
            while True:
                # Read JSON-RPC request from stdin
                print("DEBUG: Waiting for input...", file=sys.stderr)
                line = sys.stdin.readline()
                if not line:
                    print("DEBUG: No input received, breaking", file=sys.stderr)
                    break
                
                print(f"DEBUG: Received line: {line.strip()}", file=sys.stderr)
                
                try:
                    request = json.loads(line.strip())
                    print(f"DEBUG: Parsed request: {request}", file=sys.stderr)
                    response = self.handle_request(request)
                    print(f"DEBUG: Generated response: {response}", file=sys.stderr)
                    
                    # Only send response if it's not None (notifications return None)
                    if response is not None:
                        print(json.dumps(response), flush=True)
                        print("DEBUG: Response sent", file=sys.stderr)
                    else:
                        print("DEBUG: No response needed (notification)", file=sys.stderr)
                    print("DEBUG: Continuing to wait for next request...", file=sys.stderr)
                    
                except json.JSONDecodeError as e:
                    print(f"DEBUG: JSON decode error: {e}", file=sys.stderr)
                    logger.error(f"Invalid JSON received: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    print(json.dumps(error_response), flush=True)
                    
        except KeyboardInterrupt:
            print("DEBUG: KeyboardInterrupt received", file=sys.stderr)
            logger.info("Server shutdown requested")
        except Exception as e:
            print(f"DEBUG: Server error: {str(e)}", file=sys.stderr)
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}", file=sys.stderr)
            logger.error(f"Server error: {str(e)}")
            sys.exit(1)

def main():
    """Main function to run the MCP server."""
    server = MCPServer()
    server.run()

if __name__ == "__main__":
    main()
