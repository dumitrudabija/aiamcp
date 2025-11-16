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
from docx.shared import Inches, Pt, RGBColor
from aia_processor import AIAProcessor
from osfi_e23_processor import OSFIE23Processor
from description_validator import ProjectDescriptionValidator
from workflow_engine import WorkflowEngine
from utils.framework_detection import FrameworkDetector
from config.tool_registry import ToolRegistry
from utils.data_extractors import AIADataExtractor, OSFIE23DataExtractor
from aia_analysis import AIAAnalyzer
from introduction_builder import IntroductionBuilder

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
        self.osfi_e23_processor = OSFIE23Processor()
        self.description_validator = ProjectDescriptionValidator()
        self.workflow_engine = WorkflowEngine()
        self.framework_detector = FrameworkDetector(self.workflow_engine)
        self.aia_data_extractor = AIADataExtractor(self.aia_processor)
        self.osfi_data_extractor = OSFIE23DataExtractor(self.osfi_e23_processor)
        self.aia_analyzer = AIAAnalyzer(self.aia_processor)
        self.introduction_builder = IntroductionBuilder(self.framework_detector)
        self.server_info = {
            "name": "aia-assessment-server",
            "version": "1.15.0"
        }

        # Session state for workflow enforcement
        self.introduction_shown = False  # Tracks if get_server_introduction has been called
        
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
        """
        List available tools.

        This method delegates to the ToolRegistry for tool definitions
        to maintain separation of concerns and reduce server complexity.
        """
        return ToolRegistry.format_list_tools_response(request_id)
    
    def _get_or_create_auto_session(self, project_name: str, assessment_type: str = "osfi_e23") -> str:
        """
        Get or create an automatic session for direct tool calls.
        This enables session state management without explicit workflow creation.
        """
        # Create a session ID based on project name and type
        session_id = f"auto-{assessment_type}-{project_name.replace(' ', '_')[:50]}"

        # Check if session exists
        existing_session = self.workflow_engine.get_session(session_id)
        if existing_session:
            logger.info(f"Retrieved existing auto-session: {session_id}")
            return session_id

        # Create new session manually with our desired session_id
        from workflow_engine import AssessmentType, WorkflowState

        workflow_type = AssessmentType.OSFI_E23 if assessment_type == "osfi_e23" else AssessmentType.AIA_FULL

        session = {
            "session_id": session_id,
            "project_name": project_name,
            "project_description": "",  # Will be filled by first tool call
            "assessment_type": workflow_type.value,
            "state": WorkflowState.CREATED.value,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "completed_tools": [],
            "tool_results": {},
            "current_step": 0,
            "workflow_sequence": self.workflow_engine.workflows.get(workflow_type, []),
            "is_auto_session": True  # Mark as auto-created
        }

        # Store in workflow engine's sessions
        self.workflow_engine.sessions[session_id] = session

        logger.info(f"Created auto-session for direct tool calls: {session_id}")
        return session_id

    def _store_tool_result_in_session(self, session_id: str, tool_name: str, tool_result: Dict[str, Any]):
        """Store tool result in session for later retrieval."""
        session = self.workflow_engine.get_session(session_id)
        if session:
            session["tool_results"][tool_name] = {
                "result": tool_result,
                "executed_at": datetime.now().isoformat(),
                "success": True
            }
            if tool_name not in session["completed_tools"]:
                session["completed_tools"].append(tool_name)
            logger.info(f"Stored {tool_name} result in session {session_id}")

    def _get_assessment_results_for_export_from_session(self, session_id: str, framework_type: str) -> Optional[Dict[str, Any]]:
        """Extract assessment results from auto-session for export tools."""
        session = self.workflow_engine.get_session(session_id)
        if not session:
            return None

        return self._get_assessment_results_for_export(session, framework_type)

    def _call_tool(self, request_id: Any, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        # Auto-session management for OSFI E-23 tools
        osfi_tools = ["assess_model_risk", "evaluate_lifecycle_compliance", "generate_risk_rating",
                      "create_compliance_framework", "export_e23_report"]

        session_id = None
        if tool_name in osfi_tools:
            project_name = arguments.get("projectName") or arguments.get("project_name", "UnnamedProject")
            session_id = self._get_or_create_auto_session(project_name, "osfi_e23")
            logger.info(f"Using auto-session {session_id} for {tool_name}")

        try:
            if tool_name == "get_server_introduction":
                result = self._get_server_introduction(arguments)
            elif tool_name == "create_workflow":
                result = self._create_workflow(arguments)
            elif tool_name == "execute_workflow_step":
                result = self._execute_workflow_step(arguments)
            elif tool_name == "get_workflow_status":
                result = self._get_workflow_status(arguments)
            elif tool_name == "auto_execute_workflow":
                result = self._auto_execute_workflow(arguments)
            elif tool_name == "validate_project_description":
                result = self._validate_project_description(arguments)
            elif tool_name == "assess_project":
                result = self._assess_project(arguments)
            elif tool_name == "analyze_project_description":
                result = self._analyze_project_description(arguments)
            elif tool_name == "get_questions":
                result = self._get_questions(arguments)
            elif tool_name == "functional_preview":
                result = self._functional_preview(arguments)
            elif tool_name == "export_assessment_report":
                result = self._export_assessment_report(arguments)
            elif tool_name == "assess_model_risk":
                result = self._assess_model_risk(arguments)
            elif tool_name == "evaluate_lifecycle_compliance":
                result = self._evaluate_lifecycle_compliance(arguments)
            elif tool_name == "generate_risk_rating":
                result = self._generate_risk_rating(arguments)
            elif tool_name == "create_compliance_framework":
                result = self._create_compliance_framework(arguments)
            elif tool_name == "export_e23_report":
                # Auto-inject assessment_results from session if not provided
                if session_id:
                    assessment_results = arguments.get("assessment_results", {})
                    if not assessment_results or len(assessment_results) == 0:
                        # Try to get from session
                        framework_results = self._get_assessment_results_for_export_from_session(session_id, "osfi_e23")
                        if framework_results:
                            arguments["assessment_results"] = framework_results
                            logger.info(f"Auto-injected assessment_results from session {session_id}")
                result = self._export_e23_report(arguments)
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                }

            # Store result in session for OSFI tools (except export which is terminal)
            if session_id and tool_name in osfi_tools and tool_name != "export_e23_report":
                self._store_tool_result_in_session(session_id, tool_name, result)

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

    def _detect_framework_context(self, user_context: str = "", session_id: str = None) -> str:
        """
        Detect which framework to emphasize based on user context and session state.

        This method delegates to the FrameworkDetector class for the actual detection logic.

        Args:
            user_context: User's statement or project context
            session_id: Optional session ID to check for existing workflow type

        Returns:
            'aia' | 'osfi_e23' | 'both'
        """
        return self.framework_detector.detect(user_context, session_id)

    # Introduction and Workflow Builder Methods (delegate to IntroductionBuilder)

    def _build_aia_workflow_section(self) -> Dict[str, Any]:
        """Build AIA workflow section - delegates to IntroductionBuilder."""
        return self.introduction_builder._build_aia_workflow_section()

    def _build_osfi_workflow_section(self) -> Dict[str, Any]:
        """Build OSFI workflow section - delegates to IntroductionBuilder."""
        return self.introduction_builder._build_osfi_workflow_section()

    def _build_both_workflows_section(self) -> Dict[str, Any]:
        """Build combined workflows section - delegates to IntroductionBuilder."""
        return self.introduction_builder._build_both_workflows_section()

    def _get_server_introduction(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get server introduction - delegates to IntroductionBuilder."""
        return self.introduction_builder._get_server_introduction(arguments)

    def _check_introduction_requirement(self) -> Optional[Dict[str, Any]]:
        """
        Check if get_server_introduction has been called before allowing assessment tools.

        Returns:
            None if introduction shown, error dict otherwise
        """
        if not self.introduction_shown:
            return {
                "error": "INTRODUCTION_REQUIRED",
                "message": "Must call get_server_introduction first to understand available frameworks and workflows",
                "correct_flow": [
                    "1. Call get_server_introduction",
                    "2. Review framework options (AIA, OSFI E-23, Combined)",
                    "3. Choose appropriate framework for your project",
                    "4. Proceed with chosen assessment approach"
                ],
                "required_tool": "get_server_introduction",
                "educational_note": "This workflow ensures you understand the available regulatory frameworks and select the appropriate assessment type before beginning. The introduction provides critical context about official data sources, compliance requirements, and anti-hallucination safeguards."
            }
        return None

    def _create_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow session."""
        # WORKFLOW ENFORCEMENT: Check if introduction has been shown
        intro_check = self._check_introduction_requirement()
        if intro_check:
            return intro_check

        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")
        assessment_type = arguments.get("assessmentType")

        try:
            session_id = self.workflow_engine.create_session(
                project_name=project_name,
                project_description=project_description,
                assessment_type=assessment_type
            )

            session = self.workflow_engine.get_session(session_id)
            if not session:
                return {"error": "Failed to create workflow session"}

            # Get detailed workflow visualization
            detailed_sequence = self.workflow_engine.get_detailed_workflow_sequence(session["assessment_type"])

            return {
                "workflow_created": {
                    "session_id": session_id,
                    "project_name": project_name,
                    "assessment_type": session["assessment_type"],
                    "total_steps": len(session["workflow_sequence"]),
                    "initial_state": session["state"]
                },
                "workflow_visualization": {
                    "title": f"📋 {session['assessment_type'].upper()} Assessment Workflow",
                    "description": f"Complete {len(detailed_sequence)}-step guided assessment process",
                    "detailed_steps": detailed_sequence
                },
                "instructions": {
                    "how_to_proceed": "Use 'execute_workflow_step' to run individual tools within this workflow",
                    "auto_execution": "Use 'auto_execute_workflow' to automatically run compatible steps",
                    "status_tracking": "Use 'get_workflow_status' to check progress and get recommendations"
                },
                "framework_guidance": {
                    "workflow_benefits": "Automatic state persistence, dependency validation, and smart routing",
                    "professional_note": "All results still require professional validation for regulatory compliance"
                }
            }

        except Exception as e:
            logger.error(f"Error creating workflow: {str(e)}")
            return {"error": f"Workflow creation failed: {str(e)}"}

    def _execute_workflow_step(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool within a workflow."""
        session_id = arguments.get("sessionId", "")
        tool_name = arguments.get("toolName", "")
        tool_arguments = arguments.get("toolArguments", {})

        try:
            # CRITICAL FIX: Auto-inject assessment results for export tools if missing
            # This prevents generating misleading reports with default values (0/100, "Medium")
            if tool_name in ["export_assessment_report", "export_e23_report"]:
                session = self.workflow_engine.get_session(session_id)
                if session:
                    assessment_results_arg = tool_arguments.get("assessment_results", {})

                    # Check if assessment_results is empty or missing required fields
                    is_empty = not assessment_results_arg or len(assessment_results_arg) == 0

                    # For OSFI E-23, check for required risk assessment fields
                    if tool_name == "export_e23_report":
                        has_risk_data = "risk_score" in assessment_results_arg or "risk_level" in assessment_results_arg
                        if is_empty or not has_risk_data:
                            # Attempt to auto-inject from workflow state
                            framework_results = self._get_assessment_results_for_export(session, "osfi_e23")
                            if framework_results:
                                # Unwrap 'assessment' wrapper if present
                                if "assessment" in framework_results and isinstance(framework_results["assessment"], dict):
                                    tool_arguments["assessment_results"] = framework_results["assessment"]
                                else:
                                    tool_arguments["assessment_results"] = framework_results
                                logger.info(f"Auto-injected OSFI E-23 assessment results from workflow state for {session_id}")

                    # For AIA, check for required assessment fields
                    elif tool_name == "export_assessment_report":
                        has_assessment_data = "score" in assessment_results_arg or "impact_level" in assessment_results_arg
                        if is_empty or not has_assessment_data:
                            # Attempt to auto-inject from workflow state
                            framework_results = self._get_assessment_results_for_export(session, "aia")
                            if framework_results:
                                # Unwrap 'assessment' wrapper if present
                                if "assessment" in framework_results and isinstance(framework_results["assessment"], dict):
                                    tool_arguments["assessment_results"] = framework_results["assessment"]
                                else:
                                    tool_arguments["assessment_results"] = framework_results
                                logger.info(f"Auto-injected AIA assessment results from workflow state for {session_id}")

            # Execute the actual tool
            if tool_name == "validate_project_description":
                tool_result = self._validate_project_description(tool_arguments)
            elif tool_name == "assess_project":
                tool_result = self._assess_project(tool_arguments)
            elif tool_name == "analyze_project_description":
                tool_result = self._analyze_project_description(tool_arguments)
            elif tool_name == "functional_preview":
                tool_result = self._functional_preview(tool_arguments)
            elif tool_name == "assess_model_risk":
                tool_result = self._assess_model_risk(tool_arguments)
            elif tool_name == "get_questions":
                tool_result = self._get_questions(tool_arguments)
            elif tool_name == "export_assessment_report":
                tool_result = self._export_assessment_report(tool_arguments)
            elif tool_name == "export_e23_report":
                tool_result = self._export_e23_report(tool_arguments)
            elif tool_name == "evaluate_lifecycle_compliance":
                tool_result = self._evaluate_lifecycle_compliance(tool_arguments)
            elif tool_name == "generate_risk_rating":
                tool_result = self._generate_risk_rating(tool_arguments)
            elif tool_name == "create_compliance_framework":
                tool_result = self._create_compliance_framework(tool_arguments)
            else:
                return {"error": f"Tool '{tool_name}' not supported in workflow execution"}

            # Update workflow state
            workflow_info = self.workflow_engine.execute_tool(session_id, tool_name, tool_result)

            # Combine tool result with workflow management
            return {
                "tool_result": tool_result,
                "workflow_management": workflow_info,
                "session_id": session_id,
                "executed_tool": tool_name,
                "execution_timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error executing workflow step: {str(e)}")
            return {"error": f"Workflow step execution failed: {str(e)}"}

    def _get_workflow_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive workflow status."""
        session_id = arguments.get("sessionId", "")

        try:
            workflow_summary = self.workflow_engine.get_workflow_summary(session_id)
            return {
                "workflow_status": workflow_summary,
                "management_options": {
                    "continue_workflow": "Use 'execute_workflow_step' for manual execution",
                    "auto_execute": "Use 'auto_execute_workflow' for automated execution",
                    "get_updates": "Call this tool again for latest status"
                }
            }

        except Exception as e:
            logger.error(f"Error getting workflow status: {str(e)}")
            return {"error": f"Failed to get workflow status: {str(e)}"}

    def _auto_execute_workflow(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Auto-execute workflow steps."""
        session_id = arguments.get("sessionId", "")
        steps_to_execute = arguments.get("stepsToExecute", 1)

        try:
            # Get auto-execution plan
            execution_plan = self.workflow_engine.auto_execute_workflow(session_id, steps_to_execute)

            if "error" in execution_plan:
                return execution_plan

            results = []
            for step in execution_plan["execution_plan"]:
                tool_name = step["tool_name"]

                # Get session for tool arguments
                session = self.workflow_engine.get_session(session_id)
                if not session:
                    break

                # Prepare tool arguments from session data
                tool_arguments = {
                    "projectName": session["project_name"],
                    "projectDescription": session["project_description"]
                }

                # Add special arguments for export tools
                if tool_name == "export_assessment_report":
                    # Get assessment results from previous tools
                    assessment_results = self._get_assessment_results_for_export(session, "aia")
                    if assessment_results:
                        tool_arguments.update({
                            "project_name": session["project_name"],
                            "project_description": session["project_description"],
                            "assessment_results": assessment_results
                        })
                    else:
                        # Return clear error instead of silent skip
                        results.append({
                            "tool_name": tool_name,
                            "step_number": step["step_number"],
                            "execution_result": {
                                "error": "Cannot execute export - no assessment results available",
                                "reason": "Missing assessment data from functional_preview or assess_project",
                                "required_action": "Execute functional_preview or assess_project first",
                                "workflow_guidance": "Use 'get_workflow_status' to see required dependencies"
                            },
                            "success": False
                        })
                        break

                elif tool_name == "export_e23_report":
                    # Get E-23 assessment results from previous tools
                    assessment_results = self._get_assessment_results_for_export(session, "osfi_e23")
                    if assessment_results:
                        tool_arguments.update({
                            "project_name": session["project_name"],
                            "project_description": session["project_description"],
                            "assessment_results": assessment_results
                        })
                    else:
                        # Return clear error instead of silent skip
                        results.append({
                            "tool_name": tool_name,
                            "step_number": step["step_number"],
                            "execution_result": {
                                "error": "Cannot execute export - no E-23 assessment results available",
                                "reason": "Missing assessment data from assess_model_risk or related tools",
                                "required_action": "Execute assess_model_risk first",
                                "workflow_guidance": "Use 'get_workflow_status' to see required dependencies"
                            },
                            "success": False
                        })
                        break

                # Execute the step
                step_result = self._execute_workflow_step({
                    "sessionId": session_id,
                    "toolName": tool_name,
                    "toolArguments": tool_arguments
                })

                results.append({
                    "tool_name": tool_name,
                    "step_number": step["step_number"],
                    "execution_result": step_result,
                    "success": "error" not in step_result
                })

                # Stop if execution failed
                if "error" in step_result:
                    break

            return {
                "auto_execution_results": results,
                "execution_summary": {
                    "steps_planned": len(execution_plan["execution_plan"]),
                    "steps_executed": len(results),
                    "all_successful": all(result["success"] for result in results),
                    "session_id": session_id
                },
                "next_actions": "Use 'get_workflow_status' to see updated workflow state"
            }

        except Exception as e:
            logger.error(f"Error in auto-execution: {str(e)}")
            return {"error": f"Auto-execution failed: {str(e)}"}

    def _get_assessment_results_for_export(self, session: Dict[str, Any], framework_type: str) -> Optional[Dict[str, Any]]:
        """Extract assessment results from session for export tools."""
        tool_results = session.get("tool_results", {})

        if framework_type == "aia":
            # Look for AIA assessment results
            if "assess_project" in tool_results:
                return tool_results["assess_project"]["result"]
            elif "functional_preview" in tool_results:
                return tool_results["functional_preview"]["result"]
            elif "analyze_project_description" in tool_results:
                return tool_results["analyze_project_description"]["result"]

        elif framework_type == "osfi_e23":
            # Look for OSFI E-23 assessment results
            if "assess_model_risk" in tool_results:
                return tool_results["assess_model_risk"]["result"]
            elif "generate_risk_rating" in tool_results:
                return tool_results["generate_risk_rating"]["result"]
            elif "create_compliance_framework" in tool_results:
                return tool_results["create_compliance_framework"]["result"]

        return None

    def _validate_project_description(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Validate project description for framework assessment readiness."""
        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")

        # Perform validation using the description validator
        validation_result = self.description_validator.validate_description(project_description)

        # Format the response
        response = {
            "validation": {
                "project_name": project_name,
                "is_valid": validation_result["is_valid"],
                "total_words": validation_result["total_words"],
                "areas_covered": validation_result["areas_covered"],
                "areas_missing": validation_result["areas_missing"],
                "framework_readiness": validation_result["framework_readiness"],
                "validation_message": validation_result["validation_message"],
                "recommendations": validation_result["recommendations"]
            },
            "coverage_analysis": {
                area_key: {
                    "area_name": details["name"],
                    "covered": details["covered"],
                    "keywords_found": details["keyword_matches"],
                    "relevant_word_count": details["relevant_word_count"],
                    "minimum_required": details["min_words_required"],
                    "status": "✅ Adequate" if details["covered"] else "❌ Insufficient"
                }
                for area_key, details in validation_result["coverage_details"].items()
            },
            "next_steps": self._get_next_steps(validation_result),
            "professional_guidance": {
                "framework_compliance": "Results are based on content analysis and require professional validation",
                "regulatory_note": "Both AIA and OSFI E-23 frameworks require qualified professional oversight",
                "validation_warning": "This tool provides structure only - professional judgment is required for regulatory compliance"
            }
        }

        # Add template if description is insufficient
        if not validation_result["is_valid"]:
            response["description_template"] = self.description_validator.get_description_template()

        return response

    def _get_next_steps(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate next steps based on validation results."""
        if validation_result["is_valid"]:
            return [
                "✅ Description is adequate for framework assessments",
                "• Use 'assess_project' for AIA framework assessment with actual question responses",
                "• Use 'assess_model_risk' for OSFI E-23 framework assessment",
                "• Use 'functional_preview' for early AIA risk assessment without full responses",
                "• Use 'analyze_project_description' for automated AIA question analysis"
            ]
        else:
            return [
                "❌ Description needs improvement before framework assessment",
                "• Review the missing content areas listed above",
                "• Add more detail to reach minimum word count requirements",
                "• Use the provided template as a guide",
                "• Re-run validation after improving the description",
                "• Once validation passes, proceed with framework assessment tools"
            ]

    def _assess_project(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project assessment requests."""
        # WORKFLOW ENFORCEMENT: Check if introduction has been shown
        intro_check = self._check_introduction_requirement()
        if intro_check:
            return intro_check

        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")
        responses = arguments.get("responses")

        logger.info(f"Assessing project: {project_name}")

        # Validate project description adequacy for framework assessment
        validation_result = self.description_validator.validate_description(project_description)
        if not validation_result["is_valid"]:
            return {
                "assessment": {
                    "status": "validation_failed",
                    "message": "❌ Insufficient project description for AIA framework assessment",
                    "validation_details": validation_result,
                    "required_action": "Use 'validate_project_description' tool to check requirements and improve description"
                },
                "framework_readiness": validation_result["framework_readiness"],
                "recommendations": [
                    "Project description does not meet minimum requirements for AIA assessment",
                    "Please provide more detailed information covering the missing areas",
                    "Use the 'validate_project_description' tool to check specific requirements",
                    "Re-run assessment after improving the description"
                ]
            }
        
        # Convert responses format if provided
        converted_responses = None
        if responses:
            converted_responses = []
            # Create a lookup dict for questions by name (Design phase only)
            design_phase_questions = self._get_design_phase_questions()
            questions_by_name = {q['name']: q for q in design_phase_questions}
            
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
        
    # AIA Analysis Methods (delegate to AIAAnalyzer)

    def _analyze_project_description(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project description - delegates to AIAAnalyzer."""
        return self.aia_analyzer._analyze_project_description(arguments)

    def _intelligent_project_analysis(self, project_description: str) -> List[Dict[str, Any]]:
        """Perform intelligent analysis - delegates to AIAAnalyzer."""
        return self.aia_analyzer._intelligent_project_analysis(project_description)

    def _generate_analysis_recommendations(self, impact_level: int, score: int) -> List[str]:
        """Generate recommendations - delegates to AIAAnalyzer."""
        return self.aia_analyzer._generate_analysis_recommendations(impact_level, score)

    def _functional_preview(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Functional preview - delegates to AIAAnalyzer."""
        return self.aia_analyzer._functional_preview(arguments)

    def _functional_risk_analysis(self, project_description: str) -> List[Dict[str, Any]]:
        """Perform functional risk analysis - delegates to AIAAnalyzer."""
        return self.aia_analyzer._functional_risk_analysis(project_description)

    def _analyze_gaps(self, functional_responses: List[Dict[str, Any]], project_description: str) -> Dict[str, List[str]]:
        """Analyze gaps - delegates to AIAAnalyzer."""
        return self.aia_analyzer._analyze_gaps(functional_responses, project_description)

    def _generate_planning_guidance(self, functional_score: int, project_description: str) -> List[str]:
        """Generate planning guidance - delegates to AIAAnalyzer."""
        return self.aia_analyzer._generate_planning_guidance(functional_score, project_description)

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
    
    def _get_design_phase_questions(self) -> List[Dict[str, Any]]:
        """Filter questions to only include those visible in Design phase.
        
        Based on survey-enfr.json analysis, Design phase users see questions that are either:
        1. Always visible (no visibleIf condition), OR
        2. Have visibleIf condition "{projectDetailsPhase} = \"item1\"" (Design phase)
        
        This excludes questions that are only visible in Implementation phase.
        """
        # Load the survey data to check visibility conditions
        try:
            with open('data/survey-enfr.json', 'r', encoding='utf-8') as f:
                survey_data = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load survey data for phase filtering: {e}")
            # Fallback to all questions if we can't load the survey data
            return self.aia_processor.scorable_questions
        
        # Find pages that are Implementation-only (have visibleIf with item2)
        implementation_only_pages = set()
        
        # Check each page for visibility conditions
        for page in survey_data.get('pages', []):
            page_name = page.get('name', '')
            page_visible_if = page.get('visibleIf', '')
            
            # Check if this page is only visible in Implementation phase
            if '{projectDetailsPhase} = "item2"' in page_visible_if:
                implementation_only_pages.add(page_name)
                logger.info(f"Found Implementation-only page: {page_name}")
        
        # Extract all question names, excluding those from Implementation-only pages
        design_phase_question_names = set()
        
        def extract_questions_from_page(page):
            page_name = page.get('name', '')
            
            # Skip Implementation-only pages
            if page_name in implementation_only_pages:
                return
            
            # Recursively extract questions from this page
            def extract_questions(element):
                if isinstance(element, dict):
                    # Check if this is a question element
                    if 'name' in element and 'type' in element:
                        question_name = element['name']
                        element_visible_if = element.get('visibleIf', '')
                        
                        # Skip questions that are specifically Implementation-only
                        if '{projectDetailsPhase} = "item2"' in element_visible_if and '{projectDetailsPhase} = "item1"' not in element_visible_if:
                            return
                        
                        design_phase_question_names.add(question_name)
                    
                    # Recursively process nested elements
                    for key, value in element.items():
                        if key in ['elements', 'choices']:
                            extract_questions(value)
                elif isinstance(element, list):
                    for item in element:
                        extract_questions(item)
            
            # Extract questions from this page
            extract_questions(page)
        
        # Process all pages
        for page in survey_data.get('pages', []):
            extract_questions_from_page(page)
        
        # Filter scorable questions to only include Design phase questions
        design_phase_questions = []
        for question in self.aia_processor.scorable_questions:
            if question['name'] in design_phase_question_names:
                design_phase_questions.append(question)
        
        logger.info(f"Filtered to {len(design_phase_questions)} Design phase questions out of {len(self.aia_processor.scorable_questions)} total questions")
        logger.info(f"Found {len(implementation_only_pages)} Implementation-only pages")
        
        
        
        return recommendations
    
    def _get_questions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle requests for questions by category or type."""
        category = arguments.get("category")
        question_type = arguments.get("type")
        
        logger.info(f"Retrieving questions - category: {category}, type: {question_type}")
        
        # Get Design phase questions only (not all 162 questions)
        all_questions = self._get_design_phase_questions()
        
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
                "name": "Canada's Algorithmic Impact Assessment (Design Phase)",
                "total_questions": len(self._get_design_phase_questions()),
                "max_possible_score": sum(q['max_score'] for q in self._get_design_phase_questions())
            }
        }
    
    def _get_questions_summary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle questions summary requests."""
        logger.info("Retrieving questions summary")
        
        # Use Design phase questions for summary calculation
        design_phase_questions = self._get_design_phase_questions()
        
        # Calculate summary based on Design phase questions only
        total_questions = len(design_phase_questions)
        max_possible_score = sum(q['max_score'] for q in design_phase_questions)
        
        # Count questions by type
        risk_questions = len([q for q in design_phase_questions if q.get('max_score', 0) > 0])
        mitigation_questions = total_questions - risk_questions
        
        summary = {
            "total_questions": total_questions,
            "risk_questions": risk_questions,
            "mitigation_questions": mitigation_questions,
            "max_possible_score": max_possible_score,
            "framework": "Canada's Algorithmic Impact Assessment (Design Phase)"
        }
        
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
        
        # Get full question details (Design phase only)
        design_phase_questions = self._get_design_phase_questions()
        questions_by_name = {q['name']: q for q in design_phase_questions}
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
        
        # Use Design phase questions for max score calculation
        design_phase_questions = self._get_design_phase_questions()
        max_possible_score = sum(q['max_score'] for q in design_phase_questions)
        
        return {
            "success": True,
            "calculation": {
                "total_score": total_score,
                "responses_processed": len(responses),
                "max_possible_score": max_possible_score,
                "impact_level": level,
                "level_name": level_name,
                "level_description": level_description
            }
        }

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

    # Report generation helper methods

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

    def _get_assessment_disclaimer(self, assessment_results: Dict[str, Any]) -> str:
        """Get appropriate disclaimer based on assessment type."""
        if 'disclaimer' in assessment_results:
            return assessment_results['disclaimer']
        elif 'functional_risk_score' in assessment_results:
            return "⚠️ Early Indicator - Not Official Assessment. Based on functional characteristics only. Final assessment requires complete stakeholder input and official AIA process completion."
        else:
            return "This assessment is based on available project information and automated analysis. Final AIA compliance requires complete stakeholder input and official government review process."

    def _strip_markdown_formatting(self, text: str) -> str:
        """Strip markdown formatting from text for Word documents."""
        import re
        if not isinstance(text, str):
            return str(text)

        # Remove markdown formatting
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'\1', text)  # Bold italic
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)      # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)          # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)            # Code
        text = re.sub(r'#{1,6}\s+', '', text)             # Headers
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Links

        return text.strip()

    def _export_assessment_report(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Export AIA assessment results to a Microsoft Word document."""
        project_name = arguments.get("project_name", "")
        project_description = arguments.get("project_description", "")
        assessment_results = arguments.get("assessment_results", {})
        custom_filename = arguments.get("custom_filename")

        logger.info(f"Exporting assessment report for project: {project_name}")

        # CRITICAL FIX: Validate that assessment_results contains required data
        # Prevent generating misleading reports with default/incomplete values
        if not assessment_results or len(assessment_results) == 0:
            return {
                "error": "export_failed",
                "reason": "Cannot export AIA report: assessment_results is empty or missing",
                "required_action": "Execute 'assess_project' or 'functional_preview' tool first to generate assessment data",
                "workflow_guidance": "If using workflow, the system should auto-inject results. This error indicates no assessment has been completed.",
                "critical_warning": "⚠️ COMPLIANCE RISK: Exporting without assessment data would create misleading documents with incomplete or default values"
            }

        # Check for minimum required assessment fields (score or impact_level)
        has_score = "score" in assessment_results or "functional_risk_score" in assessment_results
        has_impact_level = "impact_level" in assessment_results

        if not has_score and not has_impact_level:
            return {
                "error": "export_failed",
                "reason": "Cannot export AIA report: assessment_results missing required assessment fields",
                "missing_fields": {
                    "score_missing": not has_score,
                    "impact_level_missing": not has_impact_level
                },
                "required_fields": ["score (or functional_risk_score)", "impact_level"],
                "required_action": "Execute 'assess_project' or 'functional_preview' tool to generate complete assessment",
                "received_data": list(assessment_results.keys()) if assessment_results else [],
                "critical_warning": "⚠️ COMPLIANCE RISK: Incomplete assessment data cannot produce valid regulatory documents"
            }
        
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
            design_phase_questions = self._get_design_phase_questions()
            max_score = sum(q['max_score'] for q in design_phase_questions)
            
            doc.add_paragraph(f'Impact Level: {impact_level}')
            doc.add_paragraph(f'Score: {score}/{max_score} points')
            
            # Add executive summary
            doc.add_heading('Executive Summary', level=1)
            summary = self._generate_executive_summary(score, impact_level, project_description)
            doc.add_paragraph(self._strip_markdown_formatting(summary))

            # Add key findings
            doc.add_heading('Key Findings', level=1)
            findings = self._extract_key_findings(assessment_results, project_description)
            for finding in findings:
                p = doc.add_paragraph(self._strip_markdown_formatting(finding))
                p.style = 'List Bullet'

            # Add recommendations
            doc.add_heading('Recommendations', level=1)
            recommendations = self._extract_recommendations(assessment_results, score, impact_level)
            for recommendation in recommendations:
                p = doc.add_paragraph(self._strip_markdown_formatting(recommendation))
                p.style = 'List Bullet'

            # Add project description
            doc.add_heading('Project Description', level=1)
            doc.add_paragraph(self._strip_markdown_formatting(project_description))
            
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
                "assistant_directive": {
                    "critical_instruction": "The COMPLETE AIA compliance report has been generated and saved by the MCP server. Present ONLY the file path and success message below. Do NOT generate, create, or write any additional report content. Do NOT offer to create summaries or additional documents. The Word document is complete and ready for professional review."
                },
                "success": True,
                "file_path": file_path,
                "file_size": f"{file_size_kb}KB",
                "message": f"✅ Canada's AIA compliance report saved successfully to {filename}"
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
    
    # AIA Data Extraction Methods (delegate to AIADataExtractor)

    def _extract_score(self, assessment_results: Dict[str, Any]) -> int:
        """Extract score from assessment results."""
        return self.aia_data_extractor.extract_score(assessment_results)

    def _extract_impact_level(self, assessment_results: Dict[str, Any]) -> str:
        """Extract impact level from assessment results."""
        return self.aia_data_extractor.extract_impact_level(assessment_results)

    def _extract_key_findings(self, assessment_results: Dict[str, Any], project_description: str) -> List[str]:
        """Extract key findings from assessment results."""
        return self.aia_data_extractor.extract_key_findings(assessment_results, project_description)

    def _extract_recommendations(self, assessment_results: Dict[str, Any], score: int, impact_level: str) -> List[str]:
        """Extract recommendations from assessment results."""
        return self.aia_data_extractor.extract_recommendations(assessment_results, score, impact_level)

    def _extract_true_risk_factors(self, risk_analysis: Dict[str, Any]) -> List[str]:
        """Extract only TRUE risk factors from assessment."""
        return self.aia_data_extractor.extract_true_risk_factors(risk_analysis)

    # OSFI E-23 Data Extraction Methods (delegate to OSFIE23DataExtractor)

    def _extract_e23_risk_level(self, assessment_results: Dict[str, Any]) -> str:
        """Extract risk level from E-23 assessment results."""
        return self.osfi_data_extractor.extract_risk_level(assessment_results)

    def _extract_e23_risk_score(self, assessment_results: Dict[str, Any]) -> int:
        """Extract risk score from E-23 assessment results."""
        return self.osfi_data_extractor.extract_risk_score(assessment_results)

    def _extract_e23_risk_analysis(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract risk analysis points from E-23 assessment results."""
        return self.osfi_data_extractor.extract_risk_analysis(assessment_results)

    def _extract_e23_governance_requirements(self, assessment_results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract governance requirements from E-23 assessment results."""
        return self.osfi_data_extractor.extract_governance_requirements(assessment_results)

    def _extract_e23_recommendations(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract recommendations from E-23 assessment results."""
        return self.osfi_data_extractor.extract_recommendations(assessment_results)

    def _extract_e23_lifecycle_info(self, assessment_results: Dict[str, Any]) -> str:
        """Extract lifecycle compliance information from E-23 assessment results."""
        return self.osfi_data_extractor.extract_lifecycle_info(assessment_results)

    def _extract_e23_business_rationale(self, assessment_results: Dict[str, Any], project_description: str) -> str:
        """Extract business rationale for E-23 model."""
        return self.osfi_data_extractor.extract_business_rationale(assessment_results, project_description)

    def _extract_e23_key_risk_factors(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract key risk factors from assessment results."""
        return self.osfi_data_extractor.extract_key_risk_factors(assessment_results)

    def _extract_e23_immediate_actions(self, assessment_results: Dict[str, Any], risk_level: str) -> List[str]:
        """Extract immediate actions based on risk level."""
        return self.osfi_data_extractor.extract_immediate_actions(assessment_results, risk_level)

    def _extract_e23_short_term_goals(self, assessment_results: Dict[str, Any], risk_level: str) -> List[str]:
        """Extract short-term goals (3-6 months)."""
        return self.osfi_data_extractor.extract_short_term_goals(assessment_results, risk_level)

    def _extract_e23_long_term_objectives(self, assessment_results: Dict[str, Any], risk_level: str) -> List[str]:
        """Extract long-term objectives (6+ months)."""
        return self.osfi_data_extractor.extract_long_term_objectives(assessment_results, risk_level)

    def _extract_e23_scoring_details(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ACTUAL scoring breakdown from assessment results."""
        return self.osfi_data_extractor.extract_scoring_details(assessment_results)

    def _extract_e23_quantitative_factors(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract quantitative risk factors from assessment results."""
        return self.osfi_data_extractor.extract_quantitative_factors(assessment_results)

    def _extract_e23_qualitative_factors(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract qualitative risk factors from assessment results."""
        return self.osfi_data_extractor.extract_qualitative_factors(assessment_results)

    def _extract_e23_risk_interactions(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract risk interactions and amplification factors."""
        return self.osfi_data_extractor.extract_risk_interactions(assessment_results)

    def _extract_e23_organizational_structure(self, assessment_results: Dict[str, Any]) -> Dict[str, str]:
        """Extract organizational structure from assessment results."""
        return self.osfi_data_extractor.extract_organizational_structure(assessment_results)

    def _extract_e23_policies_procedures(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract policies and procedures requirements."""
        return self.osfi_data_extractor.extract_policies_procedures(assessment_results)

    def _extract_e23_design_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract model design requirements."""
        return self.osfi_data_extractor.extract_design_requirements(assessment_results)

    def _extract_e23_review_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract model review and validation requirements."""
        return self.osfi_data_extractor.extract_review_requirements(assessment_results)

    def _extract_e23_deployment_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract model deployment requirements."""
        return self.osfi_data_extractor.extract_deployment_requirements(assessment_results)

    def _extract_e23_monitoring_framework(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract monitoring framework details."""
        return self.osfi_data_extractor.extract_monitoring_framework(assessment_results)

    def _extract_e23_decommission_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract model decommission requirements."""
        return self.osfi_data_extractor.extract_decommission_requirements(assessment_results)

    def _extract_e23_documentation_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract documentation requirements."""
        return self.osfi_data_extractor.extract_documentation_requirements(assessment_results)

    def _extract_e23_compliance_checklist(self, assessment_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract compliance checklist from assessment results."""
        return self.osfi_data_extractor.extract_compliance_checklist(assessment_results)

    def _extract_e23_implementation_timeline(self, assessment_results: Dict[str, Any]) -> Dict[str, str]:
        """Extract implementation timeline from assessment results."""
        return self.osfi_data_extractor.extract_implementation_timeline(assessment_results)

    
    def _get_e23_core_principles(self) -> List[Dict[str, str]]:
        """Get OSFI E-23 core principles."""
        return self.osfi_e23_processor.framework_data.get("principles", [
            {
                "id": "1.1",
                "title": "Organizational Enablement",
                "description": "Effective reporting structures and proper resourcing should enable sound model governance"
            },
            {
                "id": "1.2",
                "title": "MRM Framework",
                "description": "The MRM framework should align risk-taking activities to strategic objectives and risk appetite"
            },
            {
                "id": "1.3",
                "title": "Use of Models",
                "description": "Models should be appropriate for their business purposes"
            },
            {
                "id": "2.1",
                "title": "Model Identification",
                "description": "Institutions should identify and track all models in use or recently decommissioned"
            },
            {
                "id": "2.2",
                "title": "Model Risk Rating",
                "description": "Institutions should establish a model risk rating approach that assesses key dimensions of model risk"
            },
            {
                "id": "2.3",
                "title": "Risk Management Intensity",
                "description": "The scope, scale, and intensity of MRM should be commensurate with the risk introduced by the model"
            },
            {
                "id": "3.1",
                "title": "Policies, Procedures, and Controls",
                "description": "MRM policies, procedures, and controls should be robust, flexible, and lead to effective requirements applied across the model lifecycle"
            }
        ])
    
    def _get_e23_risk_levels(self) -> List[Dict[str, Any]]:
        """Get OSFI E-23 risk rating levels."""
        return self.osfi_e23_processor.framework_data.get("risk_rating_levels", [
            {"level": "Low", "description": "Minimal governance requirements", "score_range": [0, 25]},
            {"level": "Medium", "description": "Standard governance requirements", "score_range": [26, 50]},
            {"level": "High", "description": "Enhanced governance requirements", "score_range": [51, 75]},
            {"level": "Critical", "description": "Maximum governance requirements", "score_range": [76, 100]}
        ])
    
    # OSFI E-23 Tool Handlers
    
    def _assess_model_risk(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OSFI E-23 model risk assessment requests."""
        # WORKFLOW ENFORCEMENT: Check if introduction has been shown
        intro_check = self._check_introduction_requirement()
        if intro_check:
            return intro_check

        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")

        logger.info(f"OSFI E-23 model risk assessment for: {project_name}")

        # Validate project description adequacy (NON-BLOCKING - results included as warnings)
        validation_result = self.description_validator.validate_description(project_description)
        osfi_ready = validation_result["framework_readiness"].get("osfi_e23_framework", False)

        # Use the OSFI E-23 processor to perform assessment
        result = self.osfi_e23_processor.assess_model_risk(
            project_name=project_name,
            project_description=project_description
        )

        # Add validation warnings if description has issues
        if not osfi_ready:
            # Add validation warnings to the result (non-blocking)
            result["description_validation"] = {
                "validation_status": "warning",
                "message": "⚠️ Project description may not meet all recommended requirements for OSFI E-23 framework",
                "total_words": validation_result["total_words"],
                "areas_covered": validation_result["areas_covered"],
                "areas_missing": validation_result["areas_missing"],
                "recommendation": "For more comprehensive results, consider using 'validate_project_description' tool to check detailed requirements and improve description coverage."
            }
            logger.warning(f"Description validation warning for {project_name}: {validation_result['areas_missing']} areas may need more detail")
        else:
            # Add confirmation that description is adequate
            result["description_validation"] = {
                "validation_status": "passed",
                "message": "✅ Project description meets OSFI E-23 framework requirements"
            }

        return result
    
    def _evaluate_lifecycle_compliance(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OSFI E-23 lifecycle compliance evaluation requests."""
        # WORKFLOW ENFORCEMENT: Check if introduction has been shown
        intro_check = self._check_introduction_requirement()
        if intro_check:
            return intro_check

        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")
        current_stage = arguments.get("currentStage")

        logger.info(f"OSFI E-23 lifecycle compliance evaluation for: {project_name}")
        
        # Use the OSFI E-23 processor
        result = self.osfi_e23_processor.evaluate_lifecycle_compliance(
            project_name=project_name,
            project_description=project_description,
            current_stage=current_stage
        )
        
        return result
    
    def _generate_risk_rating(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OSFI E-23 risk rating generation requests."""
        # WORKFLOW ENFORCEMENT: Check if introduction has been shown
        intro_check = self._check_introduction_requirement()
        if intro_check:
            return intro_check

        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")

        logger.info(f"OSFI E-23 risk rating generation for: {project_name}")
        
        # Use the OSFI E-23 processor
        result = self.osfi_e23_processor.generate_risk_rating(
            project_name=project_name,
            project_description=project_description
        )
        
        return result
    
    def _create_compliance_framework(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OSFI E-23 compliance framework creation requests."""
        # WORKFLOW ENFORCEMENT: Check if introduction has been shown
        intro_check = self._check_introduction_requirement()
        if intro_check:
            return intro_check

        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")
        risk_level = arguments.get("riskLevel")

        logger.info(f"OSFI E-23 compliance framework creation for: {project_name}")
        
        # If risk_level is provided, create a mock risk assessment
        risk_assessment = None
        if risk_level:
            risk_assessment = {
                "risk_level": risk_level,
                "risk_score": {"Low": 20, "Medium": 40, "High": 65, "Critical": 85}.get(risk_level, 40),
                "risk_analysis": {
                    "quantitative_indicators": {},
                    "qualitative_indicators": {}
                }
            }
        
        # Use the OSFI E-23 processor
        result = self.osfi_e23_processor.create_compliance_framework(
            project_name=project_name,
            project_description=project_description,
            risk_assessment=risk_assessment
        )
        
        return result
    
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
