#!/usr/bin/env python3
"""
AIA Assessment MCP Server
A Model Context Protocol server for Canada's Algorithmic Impact Assessment
"""

import json
import logging
import sys
import os
from typing import Dict, Any, List, Optional
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
                "description": "FINAL STEP: Calculate official AIA risk score using actual question responses. CRITICAL: Only use this tool with actual user responses to specific AIA questions. Do NOT make assumptions or interpretations about risk levels - only the calculated score from actual responses is valid. This tool should only be used after collecting specific question responses.",
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
                "description": "Intelligently analyze a project description to automatically answer AIA questions where possible and identify questions requiring manual input",
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
                "description": "Get AIA questions by category or type",
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
        """Handle project description analysis requests."""
        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")
        
        logger.info(f"Analyzing project description: {project_name}")
        
        # Get questions summary and categorization
        summary = self.aia_processor.get_questions_summary()
        
        # Get technical questions that could be auto-answered
        technical_questions = []
        questions_by_name = {q['name']: q for q in self.aia_processor.scorable_questions}
        
        for question_name in self.aia_processor.question_categories['technical'][:10]:  # Limit to first 10
            if question_name in questions_by_name:
                technical_questions.append(questions_by_name[question_name])
        
        # Get manual questions that need human input
        manual_questions = []
        for question_name in self.aia_processor.question_categories['manual'][:5]:  # Limit to first 5
            if question_name in questions_by_name:
                manual_questions.append(questions_by_name[question_name])
        
        return {
            "project_name": project_name,
            "project_description": project_description,
            "analysis": {
                "framework_summary": summary,
                "auto_answerable_questions": technical_questions,
                "manual_input_required": manual_questions,
                "total_questions": summary['total_questions'],
                "categorization": {
                    "technical": len(self.aia_processor.question_categories['technical']),
                    "impact_risk": len(self.aia_processor.question_categories['impact_risk']),
                    "manual": len(self.aia_processor.question_categories['manual'])
                }
            },
            "next_steps": [
                "Review auto-answerable technical questions",
                "Provide input for manual questions requiring human judgment",
                "Complete full assessment with all responses"
            ]
        }
    
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
