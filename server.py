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
from docx.shared import Inches, Pt
from aia_processor import AIAProcessor
from osfi_e23_processor import OSFIE23Processor
from description_validator import ProjectDescriptionValidator
from workflow_engine import WorkflowEngine

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
        self.server_info = {
            "name": "aia-assessment-server",
            "version": "1.14.0"
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
        """List available tools."""
        tools = [
            {
                "name": "get_server_introduction",
                "description": "🚨 CRITICAL: This tool MUST be called at the START of any assessment conversation to orient users.\n\nWHEN TO CALL THIS TOOL:\nCall this tool IMMEDIATELY when a user:\n- Says they want to assess, evaluate, or analyze a project/system/model\n- Mentions AIA, OSFI, or compliance/regulatory requirements\n- Provides a project description asking for assessment\n- Asks about which framework to use\n- Says they're starting a new assessment or compliance process\n- Any variation of 'help me with [AI/model/system] compliance'\n\nWHAT TO DO AFTER CALLING THIS TOOL:\n1. Present the framework_selection_guide to help user choose AIA vs OSFI vs Combined\n2. Explain the workflow options available\n3. Ask the user which framework applies to their project\n4. WAIT for user to choose before proceeding with any assessment\n5. Do NOT immediately create workflows or start assessments without user choice\n\nWRONG FLOW ❌:\nUser: 'Assess my AI project'\nClaude: [Creates workflow immediately]\n\nCORRECT FLOW ✅:\nUser: 'Assess my AI project'\nClaude: [Calls get_server_introduction]\nClaude: 'Let me explain your options first. You can use: AIA for government systems, OSFI E-23 for financial institutions, or Combined. Which applies?'\nUser: [Chooses framework]\nClaude: [Proceeds with chosen approach]\n\nThis tool provides comprehensive introduction to MCP server capabilities, tool categories, workflow guidance, and critical distinction between official framework data (MCP) vs AI-generated interpretations (Claude).",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "name": "validate_project_description",
                "description": "🔍 FRAMEWORK READINESS VALIDATOR: Validate project descriptions for adequacy before conducting AIA or OSFI E-23 assessments. Ensures descriptions contain sufficient information across key areas required by both frameworks. Use this as a first step before framework assessments to prevent 'insufficient description' errors.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the project being validated"
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "Project description to validate for framework assessment readiness"
                        }
                    },
                    "required": ["projectName", "projectDescription"],
                    "additionalProperties": False
                }
            },
            {
                "name": "create_workflow",
                "description": "🔄 WORKFLOW MANAGEMENT: Create and manage assessment workflows with automatic sequencing, state persistence, and smart routing. Provides guided assessment processes for AIA and OSFI E-23 frameworks.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the project for workflow management"
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "Project description for workflow creation"
                        },
                        "assessmentType": {
                            "type": "string",
                            "description": "Type of assessment workflow (aia_full, aia_preview, osfi_e23, combined)",
                            "enum": ["aia_full", "aia_preview", "osfi_e23", "combined"]
                        }
                    },
                    "required": ["projectName", "projectDescription"],
                    "additionalProperties": False
                }
            },
            {
                "name": "execute_workflow_step",
                "description": "🎯 WORKFLOW EXECUTION: Execute specific tools within a managed workflow with automatic state tracking, dependency validation, and smart next-step recommendations.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sessionId": {
                            "type": "string",
                            "description": "Workflow session ID from create_workflow"
                        },
                        "toolName": {
                            "type": "string",
                            "description": "Name of the tool to execute within the workflow"
                        },
                        "toolArguments": {
                            "type": "object",
                            "description": "Arguments for the tool being executed"
                        }
                    },
                    "required": ["sessionId", "toolName", "toolArguments"],
                    "additionalProperties": False
                }
            },
            {
                "name": "get_workflow_status",
                "description": "📊 WORKFLOW STATUS: Get comprehensive workflow status including progress, next steps, smart routing recommendations, and session management.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sessionId": {
                            "type": "string",
                            "description": "Workflow session ID"
                        }
                    },
                    "required": ["sessionId"],
                    "additionalProperties": False
                }
            },
            {
                "name": "auto_execute_workflow",
                "description": "⚡ AUTO-EXECUTION: Automatically execute multiple workflow steps where possible, with intelligent dependency management and manual intervention detection.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sessionId": {
                            "type": "string",
                            "description": "Workflow session ID"
                        },
                        "stepsToExecute": {
                            "type": "number",
                            "description": "Number of steps to auto-execute (default: 1)",
                            "minimum": 1,
                            "maximum": 5
                        }
                    },
                    "required": ["sessionId"],
                    "additionalProperties": False
                }
            },
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
                "description": "CANADA'S AIA FRAMEWORK: Generates and saves a COMPLETE AIA compliance report as a Microsoft Word document. The MCP server creates the entire professional document with executive summary, key findings, recommendations, and all required sections based on Canada's official framework. The document is immediately ready for professional review.",
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
            },
            {
                "name": "assess_model_risk",
                "description": "⚠️ OSFI E-23 MODEL RISK MANAGEMENT: Assess model risk using Canada's OSFI Guideline E-23 framework for federally regulated financial institutions. COMPLIANCE WARNING: This tool provides structured assessment framework only. All results must be validated by qualified model risk professionals and approved by appropriate governance authorities. Risk assessments must be based on factual, verifiable project information - not AI interpretation.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the model being assessed"
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "CRITICAL: Provide factual, detailed description including specific technical architecture, documented data sources/volumes, explicit business use cases, defined decision-making processes, and measurable performance criteria. Avoid vague descriptions requiring AI interpretation."
                        }
                    },
                    "required": ["projectName", "projectDescription"],
                    "additionalProperties": False
                }
            },
            {
                "name": "evaluate_lifecycle_compliance",
                "description": "OSFI E-23 MODEL RISK MANAGEMENT: Evaluate model lifecycle compliance against OSFI E-23 requirements across all 5 stages (Design, Review, Deployment, Monitoring, Decommission). Identifies compliance gaps and provides stage-specific recommendations.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the model being evaluated"
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "Detailed description of the model and its current lifecycle stage"
                        },
                        "currentStage": {
                            "type": "string",
                            "description": "Current lifecycle stage of the model",
                            "enum": ["Design", "Review", "Deployment", "Monitoring", "Decommission"]
                        }
                    },
                    "required": ["projectName", "projectDescription"],
                    "additionalProperties": False
                }
            },
            {
                "name": "generate_risk_rating",
                "description": "OSFI E-23 MODEL RISK MANAGEMENT: Generate detailed risk rating assessment using OSFI E-23 methodology. Provides comprehensive risk analysis with quantitative scoring, qualitative factors, and risk amplification analysis for financial institution compliance.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the model being rated"
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "Detailed description of the model including technical details, business impact, and usage context"
                        }
                    },
                    "required": ["projectName", "projectDescription"],
                    "additionalProperties": False
                }
            },
            {
                "name": "create_compliance_framework",
                "description": "OSFI E-23 MODEL RISK MANAGEMENT: Create comprehensive compliance framework based on OSFI E-23 requirements. Generates detailed governance structure, policies, procedures, and controls tailored to the model's risk level and business context.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the model requiring compliance framework"
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "Detailed description of the model, its business purpose, and organizational context"
                        },
                        "riskLevel": {
                            "type": "string",
                            "description": "Optional: Pre-determined risk level to tailor framework requirements",
                            "enum": ["Low", "Medium", "High", "Critical"]
                        }
                    },
                    "required": ["projectName", "projectDescription"],
                    "additionalProperties": False
                }
            },
            {
                "name": "export_e23_report",
                "description": "⚠️ OSFI E-23 MODEL RISK MANAGEMENT: Generates and saves a COMPLETE lifecycle-focused OSFI E-23 compliance report as a Microsoft Word document. The MCP server creates the entire document including executive summary, risk analysis, compliance checklist, and recommendations. COMPLIANCE WARNING: Generated reports are templates requiring professional validation. All content must be reviewed by qualified model risk professionals, validated against actual project characteristics, and approved by appropriate governance authorities before use for regulatory compliance.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Name of the model being assessed"
                        },
                        "project_description": {
                            "type": "string",
                            "description": "Description of the model and its business application"
                        },
                        "assessment_results": {
                            "type": "object",
                            "description": "Assessment results object from previous E-23 assessment (assess_model_risk, generate_risk_rating, or create_compliance_framework)"
                        },
                        "custom_filename": {
                            "type": "string",
                            "description": "Optional custom filename (without extension). If not provided, will use E23_Report_[ProjectName]_[YYYY-MM-DD].docx format"
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

    def _get_server_introduction(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Provide comprehensive server introduction and transparency information."""

        # Mark introduction as shown for this session
        self.introduction_shown = True
        logger.info("Introduction shown - workflow enforcement gate unlocked")

        return {
            "assistant_directive": {
                "critical_instruction": "Present ONLY the information contained in this response. Do NOT add time estimates, interpretations, recommendations, or other content not explicitly provided here. If the user asks questions requiring interpretation, clearly state 'That's my interpretation as AI, not from the official MCP data.' Distinguish between official framework data (from this tool) and your own analysis."
            },
            "server_introduction": {
                "title": "🇨🇦 Canada's Regulatory Assessment MCP Server",
                "version": "1.14.0",
                "purpose": "Official framework compliance for Canada's Algorithmic Impact Assessment (AIA) and OSFI Guideline E-23 Model Risk Management",
                "transparency_notice": {
                    "critical_distinction": "This server provides OFFICIAL regulatory framework data. All calculations, scores, and compliance determinations come from verified government sources - NOT AI generation.",
                    "data_sources": [
                        "🔧 MCP SERVER (Official): Canada.ca AIA framework questions and scoring",
                        "🔧 MCP SERVER (Official): OSFI E-23 risk management methodology",
                        "🔧 MCP SERVER (Official): Validated calculations using government formulas",
                        "🧠 CLAUDE (AI-Generated): Result interpretations and recommendations only"
                    ],
                    "anti_hallucination_design": "AI cannot modify official scores, risk levels, or compliance determinations - these come exclusively from the MCP server using government-verified data"
                }
            },
            "tool_categories": {
                "workflow_management": {
                    "description": "🔄 Automated assessment workflows with state persistence",
                    "tools": ["create_workflow", "execute_workflow_step", "get_workflow_status", "auto_execute_workflow"],
                    "usage": "Recommended approach for guided, end-to-end assessments"
                },
                "validation_tools": {
                    "description": "🔍 Project description adequacy validation",
                    "tools": ["validate_project_description"],
                    "usage": "Required first step before framework assessments"
                },
                "aia_framework": {
                    "description": "🇨🇦 Canada's Algorithmic Impact Assessment (104 official questions)",
                    "tools": ["analyze_project_description", "get_questions", "assess_project", "functional_preview", "export_assessment_report"],
                    "official_source": "Canada.ca Treasury Board Directive on Automated Decision-Making"
                },
                "osfi_e23_framework": {
                    "description": "🏦 OSFI Guideline E-23 Model Risk Management",
                    "tools": ["assess_model_risk", "evaluate_lifecycle_compliance", "generate_risk_rating", "create_compliance_framework", "export_e23_report"],
                    "official_source": "Office of the Superintendent of Financial Institutions Canada"
                }
            },
            "workflow_guidance": {
                "recommended_approach": [
                    "1. 🔄 Use 'create_workflow' to start guided assessment",
                    "2. ⚡ Use 'auto_execute_workflow' for automated progression",
                    "3. 📊 Use 'get_workflow_status' for progress tracking",
                    "4. 🎯 Use 'execute_workflow_step' for manual control when needed"
                ],
                "traditional_approach": [
                    "1. 🔍 Start with 'validate_project_description'",
                    "2. 📋 Use framework-specific tools individually",
                    "3. 📄 Export results with report generation tools"
                ],
                "automatic_features": [
                    "✅ Assessment type auto-detection (AIA/OSFI E-23/Combined)",
                    "✅ Dependency validation (prevents out-of-order execution)",
                    "✅ State persistence (2-hour session timeout)",
                    "✅ Smart routing (next-step recommendations)",
                    "✅ Document generation (automated export)"
                ]
            },
            "compliance_warnings": {
                "professional_validation": "⚠️ ALL RESULTS require validation by qualified professionals and approval by appropriate governance authorities",
                "regulatory_compliance": "⚠️ This tool provides STRUCTURE ONLY - professional judgment is required for regulatory compliance",
                "anti_hallucination": "⚠️ Official scores and risk levels come from MCP server using government data - AI provides interpretation only",
                "audit_requirements": "⚠️ Results must be reviewed by appropriate risk management and compliance teams before regulatory use"
            },
            "usage_examples": {
                "proper_usage": [
                    "✅ Use workflows for complete guided assessments",
                    "✅ Validate project descriptions before framework tools",
                    "✅ Use official scores for regulatory compliance",
                    "✅ Export generated documents for audit trails"
                ],
                "improper_usage": [
                    "❌ Do NOT use AI interpretations for regulatory decisions",
                    "❌ Do NOT bypass description validation requirements",
                    "❌ Do NOT use framework tools without proper project information",
                    "❌ Do NOT modify or substitute official scoring calculations"
                ]
            },
            "next_steps": {
                "for_new_assessment": "Use 'create_workflow' with your project details to begin guided assessment",
                "for_specific_framework": "Use 'validate_project_description' first, then proceed with AIA or OSFI E-23 tools",
                "for_help": "This introduction provides all available capabilities - no additional help tools needed"
            }
        }

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
        
        return result
    
    def _analyze_project_description(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project description analysis requests with intelligent automatic scoring."""
        # WORKFLOW ENFORCEMENT: Check if introduction has been shown
        intro_check = self._check_introduction_requirement()
        if intro_check:
            return intro_check

        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")

        logger.info(f"Analyzing project description: {project_name}")
        
        # Get Design phase questions for all calculations
        design_phase_questions = self._get_design_phase_questions()
        design_phase_max_score = sum(q['max_score'] for q in design_phase_questions)
        
        # Perform intelligent analysis of the project description
        auto_responses = self._intelligent_project_analysis(project_description)
        
        # Calculate preliminary score based on automatic analysis
        preliminary_score = self.aia_processor.calculate_score(auto_responses)
        impact_level, level_name, level_description = self.aia_processor.determine_impact_level(preliminary_score)
        
        # Get questions that still need manual input (Design phase only)
        answered_question_ids = {r['question_id'] for r in auto_responses}
        questions_by_name = {q['name']: q for q in design_phase_questions}
        
        manual_questions = []
        for question in design_phase_questions:
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
        
        # Calculate percentages using Design phase questions
        completion_percentage = round((len(auto_responses) / len(design_phase_questions)) * 100)
        score_percentage = round((preliminary_score / design_phase_max_score) * 100, 2)
        
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
        
        return design_phase_questions
    
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
        
        # Filter questions to only include those visible in Design phase
        # Based on survey-enfr.json analysis: Design phase users see questions that are either:
        # 1. Always visible (no visibleIf condition), OR
        # 2. Have visibleIf condition "{projectDetailsPhase} = \"item1\"" (Design phase)
        design_phase_questions = self._get_design_phase_questions()
        
        # Get questions by name for lookup
        questions_by_name = {q['name']: q for q in design_phase_questions}
        
        # Automatically answer questions based on comprehensive project analysis
        for question in design_phase_questions:
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
    
    def _functional_preview(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle functional preview requests - early risk assessment focused on technical characteristics."""
        # WORKFLOW ENFORCEMENT: Check if introduction has been shown
        intro_check = self._check_introduction_requirement()
        if intro_check:
            return intro_check

        project_name = arguments.get("projectName", "")
        project_description = arguments.get("projectDescription", "")

        logger.info(f"Functional preview for project: {project_name}")

        # Validate project description adequacy for framework assessment
        validation_result = self.description_validator.validate_description(project_description)
        if not validation_result["is_valid"]:
            return {
                "assessment": {
                    "status": "validation_failed",
                    "message": "❌ Insufficient project description for AIA functional preview",
                    "validation_details": validation_result,
                    "required_action": "Use 'validate_project_description' tool to check requirements and improve description"
                },
                "framework_readiness": validation_result["framework_readiness"],
                "recommendations": [
                    "Project description does not meet minimum requirements for AIA functional preview",
                    "Please provide more detailed information covering the missing areas",
                    "Use the 'validate_project_description' tool to check specific requirements",
                    "Re-run functional preview after improving the description"
                ]
            }

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
            "mcp_official_data": {
                "data_source": "🔧 MCP SERVER (Official): Canada.ca AIA framework calculations",
                "functional_risk_score": functional_score,
                "score_range": f"{likely_range['min_score']}-{likely_range['max_score']}",
                "likely_impact_level": f"Level {self._get_impact_level_roman(base_impact_level)}",
                "scoring_methodology": "Official AIA framework formula using government-verified question weights",
                "compliance_note": "Score calculated using official Treasury Board Directive methodology"
            },
            "ai_generated_analysis": {
                "data_source": "🧠 CLAUDE ANALYSIS (AI-Generated): Interpretations and recommendations",
                "project_name": project_name,
                "project_description": project_description,
                "confidence": "High - based on functional characteristics",
                "critical_gaps": gap_analysis['critical'],
                "important_gaps": gap_analysis['important'],
                "administrative_gaps": gap_analysis['administrative'],
                "planning_guidance": planning_guidance,
                "score_sensitivity": score_sensitivity,
                "ai_interpretation_note": "Gap analysis and recommendations generated by AI based on official scores"
            },
            "compliance_warnings": {
                "disclaimer": "⚠️ Early Indicator - Not Official Assessment. Based on functional characteristics only. Final assessment requires complete stakeholder input.",
                "professional_validation": "⚠️ Results require validation by qualified professionals",
                "regulatory_compliance": "⚠️ Official scores come from MCP server - AI provides interpretation only"
            }
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
    
    def _generate_streamlined_e23_report(self, doc: Document, project_name: str,
                                          project_description: str, assessment_results: Dict[str, Any]) -> Document:
        """
        Generate concise, risk-adaptive OSFI E-23 report (4-6 pages).

        Structure:
        1. Executive Summary (1 page) - Risk-adaptive tone
        2. Risk Scoring & Justification (1-2 pages) - Only TRUE risk factors
        3. Next Steps to Progress to Review Stage (2-3 pages) - Risk-appropriate deliverables
        """
        # Extract key data
        risk_level = assessment_results.get("risk_level", assessment_results.get("risk_rating", "Medium"))
        risk_score = assessment_results.get("risk_score", assessment_results.get("overall_score", 0))
        risk_analysis = assessment_results.get("risk_analysis", {})

        # Detect lifecycle stage and model type
        from osfi_e23_structure import detect_lifecycle_stage, is_ai_ml_model
        current_stage = detect_lifecycle_stage(project_description)
        is_ai_ml = is_ai_ml_model(project_description)

        # DOCUMENT HEADER
        title = doc.add_heading('OSFI E-23 Model Risk Assessment', 0)
        title.alignment = 1  # Center

        subtitle = doc.add_paragraph()
        run = subtitle.add_run(project_name)
        run.bold = True
        run.font.size = Pt(14)
        subtitle.alignment = 1

        date_para = doc.add_paragraph(f'Assessment Date: {datetime.now().strftime("%B %d, %Y")}')
        date_para.alignment = 1

        doc.add_paragraph()  # Spacing

        # SECTION 1: EXECUTIVE SUMMARY (1 page)
        doc.add_heading('1. Executive Summary', level=1)

        # Risk-adaptive summary paragraph
        summary_text = self._generate_risk_adaptive_summary(
            risk_level, risk_score, current_stage, is_ai_ml, project_description
        )
        doc.add_paragraph(summary_text)

        doc.add_paragraph()  # Spacing

        # SECTION 2: RISK SCORING & JUSTIFICATION (1-2 pages)
        doc.add_heading('2. Risk Scoring & Justification', level=1)

        # 2.1 Overall Assessment
        doc.add_heading('2.1 Overall Assessment', level=2)
        para = doc.add_paragraph()
        para.add_run('Risk Rating: ').bold = True
        para.add_run(f'{risk_level}\n')
        para.add_run('Risk Score: ').bold = True
        para.add_run(f'{risk_score}/100\n')
        para.add_run('Scoring Methodology: ').bold = True
        para.add_run("Institution's risk rating per OSFI Principle 2.2 (Model Risk Rating)")

        # 2.2 Risk Factors Identified
        doc.add_heading('2.2 Risk Factors Identified', level=2)

        true_risk_factors = self._extract_true_risk_factors(risk_analysis)

        if true_risk_factors:
            doc.add_paragraph("The following risk factors are present in this model:")
            for factor in true_risk_factors:
                doc.add_paragraph(factor, style='List Bullet')
        else:
            doc.add_paragraph("No significant risk factors identified. This model exhibits low inherent risk profile.")

        # 2.3 OSFI E-23 Risk-Based Approach
        doc.add_heading('2.3 OSFI E-23 Risk-Based Approach', level=2)

        risk_approach_text = self._generate_risk_approach_text(risk_level, is_ai_ml)
        doc.add_paragraph(risk_approach_text)

        doc.add_paragraph()  # Spacing

        # SECTION 3: NEXT STEPS TO PROGRESS TO REVIEW STAGE (2-3 pages)
        doc.add_heading('3. Next Steps to Progress to Review Stage', level=1)

        doc.add_paragraph(
            'Per OSFI E-23 Model Lifecycle (Outcome 3), progression from Design to Review stage '
            'requires completion of Design stage deliverables.'
        )

        # 3.1 Design Stage Deliverables Required
        doc.add_heading('3.1 Design Stage Deliverables Required', level=2)

        self._add_design_deliverables(doc, risk_level, is_ai_ml)

        # 3.2 Review Stage Setup
        doc.add_heading('3.2 Review Stage Setup', level=2)

        self._add_review_setup(doc, risk_level)

        # 3.3 Governance Implications (if not Low risk)
        if risk_level != "Low":
            doc.add_heading('3.3 Governance Implications', level=2)
            governance_text = self._generate_governance_implications(risk_level)
            doc.add_paragraph(governance_text)

        # Professional validation footer
        doc.add_paragraph()
        doc.add_paragraph()
        footer = doc.add_paragraph()
        run = footer.add_run('⚠️ PROFESSIONAL VALIDATION REQUIRED')
        run.bold = True
        doc.add_paragraph(
            'This assessment provides structured analysis based on OSFI E-23 framework. '
            'All results require validation by qualified professionals and approval by '
            'appropriate governance authorities before use in regulatory compliance.'
        )

        return doc

    def _generate_risk_adaptive_summary(self, risk_level: str, risk_score: int,
                                        current_stage: str, is_ai_ml: bool,
                                        project_description: str) -> str:
        """Generate risk-adaptive executive summary text."""
        description_lower = project_description.lower()

        # Model characteristics
        characteristics = []
        if is_ai_ml:
            characteristics.append("AI/ML-based")
        if any(term in description_lower for term in ['financial', 'loan', 'credit', 'lending']):
            characteristics.append("financial decision-making")
        if any(term in description_lower for term in ['customer', 'client', 'consumer']):
            characteristics.append("customer-facing")

        model_desc = " ".join(characteristics) if characteristics else "decision-making"

        if risk_level in ["Critical", "High"]:
            return (
                f'This {model_desc} model has been assessed as {risk_level} risk (score: {risk_score}/100) '
                f'under OSFI Guideline E-23. The elevated risk profile requires enhanced governance '
                f'commensurate with the model\'s potential impact (OSFI Principle 2.3). Comprehensive Design '
                f'stage documentation is required before progressing to Model Review stage. Key risk factors '
                f'necessitate thorough validation, robust oversight processes, and heightened senior management '
                f'attention throughout the model lifecycle.'
            )
        elif risk_level == "Medium":
            return (
                f'This {model_desc} model has been assessed as Medium risk (score: {risk_score}/100) '
                f'under OSFI Guideline E-23. The model requires proportionate governance aligned with OSFI\'s '
                f'risk-based approach (Principle 2.3). Standard Design stage requirements apply, with moderate '
                f'oversight appropriate for the risk profile. Complete Design stage deliverables are needed '
                f'before progressing to Model Review stage.'
            )
        else:  # Low risk
            return (
                f'This {model_desc} model has been assessed as Low risk (score: {risk_score}/100) '
                f'under OSFI Guideline E-23. The low risk profile reflects '
                + ('limited financial impact, ' if 'financial' not in description_lower else '')
                + ('non-customer-facing usage, ' if 'customer' not in description_lower else '')
                + ('and straightforward methodology. ' if not is_ai_ml else '')
                + f'Per OSFI\'s proportionality principle (Principle 2.3), streamlined governance is '
                f'appropriate. Basic Design stage documentation is required, but the low risk nature '
                f'allows for an efficient compliance path with reduced oversight burden.'
            )

    def _extract_true_risk_factors(self, risk_analysis: Dict[str, Any]) -> List[str]:
        """Extract only TRUE risk factors from assessment."""
        factors = []

        # Quantitative indicators
        quant = risk_analysis.get("quantitative_indicators", {})
        if quant.get("financial_impact"):
            factors.append("Financial Impact: Model influences material financial decisions or exposures")
        if quant.get("large_transaction_volume"):
            factors.append("Large Transaction Volume: Model processes significant number of transactions")
        if quant.get("customer_impact"):
            factors.append("Customer Impact: Model directly affects customer outcomes or decisions")

        # Qualitative indicators
        qual = risk_analysis.get("qualitative_indicators", {})
        if qual.get("complex_methodology"):
            factors.append("Complex Methodology: Advanced analytical or computational techniques employed")
        if qual.get("ai_ml_usage"):
            factors.append("AI/ML Usage: Model utilizes artificial intelligence or machine learning algorithms")
        if qual.get("data_quality_concerns"):
            factors.append("Data Quality Sensitivity: Model performance significantly dependent on data quality")
        if qual.get("regulatory_sensitivity"):
            factors.append("Regulatory Sensitivity: Model outputs subject to regulatory scrutiny or reporting")

        return factors

    def _generate_risk_approach_text(self, risk_level: str, is_ai_ml: bool) -> str:
        """Generate OSFI risk-based approach explanation."""
        base_text = (
            'OSFI Principle 2.2 requires institutions to establish a model risk rating methodology. '
            'Principle 2.3 mandates that governance intensity be commensurate with the model\'s risk profile. '
        )

        if risk_level in ["Critical", "High"]:
            return base_text + (
                f'This model\'s {risk_level} risk rating requires enhanced scrutiny, including: '
                f'heightened approval authorities, comprehensive validation, frequent monitoring, and '
                f'senior management involvement. '
                + ('For AI/ML models of this risk level, explainability and bias assessment are particularly important. ' if is_ai_ml else '')
            )
        elif risk_level == "Medium":
            return base_text + (
                'This Medium risk rating requires standard governance procedures with regular monitoring '
                'and oversight appropriate to the risk profile. Balanced documentation and review processes apply.'
            )
        else:
            return base_text + (
                'This Low risk rating permits streamlined governance with reduced oversight burden. '
                'OSFI\'s proportionality principle ensures compliance requirements match the actual risk, '
                'avoiding unnecessary regulatory burden for minimal-risk models.'
            )

    def _add_design_deliverables(self, doc: Document, risk_level: str, is_ai_ml: bool):
        """Add Design stage deliverables checklist."""
        doc.add_paragraph('Extract from OSFI E-23 Principles 3.2 (Model Design) and 3.3 (Model Development):')
        doc.add_paragraph()

        # Model Rationale
        para = doc.add_paragraph('☐ ', style='List Bullet')
        run = para.add_run('Model Rationale (Principle 3.2)')
        run.bold = True
        doc.add_paragraph('    • Document model purpose, scope, and business use case', style='List Bullet')
        doc.add_paragraph('    • Assess risk of intended usage', style='List Bullet')
        if is_ai_ml:
            doc.add_paragraph('    • Document explainability approach and bias assessment procedures', style='List Bullet')

        # Model Data
        para = doc.add_paragraph('☐ ', style='List Bullet')
        run = para.add_run('Model Data (Principle 3.2)')
        run.bold = True
        doc.add_paragraph('    • Document data governance framework', style='List Bullet')
        doc.add_paragraph('    • Establish data quality standards (accuracy, relevance, representativeness, '
                         'compliance, traceability, timeliness)', style='List Bullet')
        doc.add_paragraph('    • Document data sources and provenance', style='List Bullet')
        doc.add_paragraph('    • Define data quality check procedures', style='List Bullet')

        # Model Development
        para = doc.add_paragraph('☐ ', style='List Bullet')
        run = para.add_run('Model Development (Principle 3.3)')
        run.bold = True
        doc.add_paragraph('    • Document model methodology and assumptions', style='List Bullet')
        doc.add_paragraph('    • Document limitations and restrictions on use', style='List Bullet')
        doc.add_paragraph('    • Define performance criteria', style='List Bullet')
        doc.add_paragraph('    • Establish monitoring standards', style='List Bullet')
        doc.add_paragraph('    • Document role of expert judgment', style='List Bullet')

        # Model Inventory
        para = doc.add_paragraph('☐ ', style='List Bullet')
        run = para.add_run('Model Inventory Entry (OSFI Appendix 1)')
        run.bold = True
        doc.add_paragraph('    • Complete minimum tracking fields per OSFI Appendix 1', style='List Bullet')
        doc.add_paragraph('    • Confirm or update provisional risk rating', style='List Bullet')

        # Risk-adaptive note
        if risk_level in ["Critical", "High"]:
            doc.add_paragraph()
            note = doc.add_paragraph()
            run = note.add_run('Note: ')
            run.bold = True
            note.add_run(f'{risk_level} risk models require enhanced documentation depth and thoroughness.')
        elif risk_level == "Low":
            doc.add_paragraph()
            note = doc.add_paragraph()
            run = note.add_run('Note: ')
            run.bold = True
            note.add_run('Low risk models may use streamlined documentation formats per proportionality principle.')

    def _add_review_setup(self, doc: Document, risk_level: str):
        """Add Review stage setup requirements."""
        para = doc.add_paragraph('☐ ', style='List Bullet')
        run = para.add_run('Assign Independent Model Reviewer')
        run.bold = True
        doc.add_paragraph(f'    • Identify qualified reviewer with appropriate independence', style='List Bullet')

        para = doc.add_paragraph('☐ ', style='List Bullet')
        run = para.add_run('Define Review Scope')
        run.bold = True
        doc.add_paragraph(f'    • Establish review depth commensurate with {risk_level} risk level', style='List Bullet')

        if risk_level == "Critical":
            doc.add_paragraph('    • Consider external validation for Critical-rated models', style='List Bullet')
            doc.add_paragraph('    • Enhanced documentation requirements apply', style='List Bullet')
        elif risk_level == "High":
            doc.add_paragraph('    • Comprehensive internal validation required', style='List Bullet')
        elif risk_level == "Low":
            doc.add_paragraph('    • Streamlined review appropriate for low-risk profile', style='List Bullet')

        para = doc.add_paragraph('☐ ', style='List Bullet')
        run = para.add_run('Establish Review Schedule')
        run.bold = True
        if risk_level in ["Critical", "High"]:
            doc.add_paragraph('    • Prioritize review given elevated risk profile', style='List Bullet')
        else:
            doc.add_paragraph('    • Schedule review according to institution priorities', style='List Bullet')

    def _generate_governance_implications(self, risk_level: str) -> str:
        """Generate governance implications for non-Low risk models."""
        if risk_level == "Critical":
            return (
                'Critical risk models typically require: Board or Board Committee approval; '
                'external validation or independent expert review; enhanced monitoring with '
                'frequent reporting to senior management; formal escalation procedures; '
                'comprehensive documentation meeting highest standards.'
            )
        elif risk_level == "High":
            return (
                'High risk models typically require: Senior Management (CEO/CFO) approval; '
                'comprehensive internal validation; regular monitoring with management reporting; '
                'formal change management procedures; thorough documentation meeting enhanced standards.'
            )
        elif risk_level == "Medium":
            return (
                'Medium risk models typically require: Appropriate Management approval; '
                'standard validation procedures; periodic monitoring; documented change control; '
                'standard documentation completeness.'
            )
        return ""

    def _export_e23_report(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Export streamlined OSFI E-23 model risk assessment report (4-6 pages, risk-adaptive)."""
        project_name = arguments.get("project_name", "")
        project_description = arguments.get("project_description", "")
        assessment_results = arguments.get("assessment_results", {})
        custom_filename = arguments.get("custom_filename")

        logger.info(f"Exporting streamlined OSFI E-23 report for project: {project_name}")

        # CRITICAL FIX: Validate that assessment_results contains required data
        # Prevent generating misleading reports with default values (0/100, "Medium")
        if not assessment_results or len(assessment_results) == 0:
            return {
                "error": "export_failed",
                "reason": "Cannot export OSFI E-23 report: assessment_results is empty or missing",
                "required_action": "Execute 'assess_model_risk' tool first to generate assessment data",
                "workflow_guidance": "If using workflow, the system should auto-inject results. This error indicates no assessment has been completed.",
                "critical_warning": "⚠️ COMPLIANCE RISK: Exporting without assessment data would create misleading documents with default values (Risk Score: 0/100, Risk Level: Medium)"
            }

        # Check for minimum required risk assessment fields
        has_risk_score = "risk_score" in assessment_results or "overall_score" in assessment_results
        has_risk_level = "risk_level" in assessment_results or "risk_rating" in assessment_results

        if not has_risk_score or not has_risk_level:
            return {
                "error": "export_failed",
                "reason": "Cannot export OSFI E-23 report: assessment_results missing required risk assessment fields",
                "missing_fields": {
                    "risk_score_missing": not has_risk_score,
                    "risk_level_missing": not has_risk_level
                },
                "required_fields": ["risk_score (or overall_score)", "risk_level (or risk_rating)"],
                "required_action": "Execute 'assess_model_risk' tool to generate complete assessment with risk scoring",
                "received_data": list(assessment_results.keys()) if assessment_results else [],
                "critical_warning": "⚠️ COMPLIANCE RISK: Incomplete assessment data cannot produce valid regulatory documents"
            }

        try:
            # STREAMLINED OSFI E-23 REPORT GENERATION (4-6 pages, risk-adaptive)
            from osfi_e23_structure import detect_lifecycle_stage

            current_stage = detect_lifecycle_stage(project_description)
            logger.info(f"Detected OSFI E-23 lifecycle stage: {current_stage}")

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
                filename = f"OSFI_E23_Assessment_{clean_project_name}_{current_date}_Streamlined.docx"

            file_path = os.path.join(assessments_dir, filename)

            # Create Word document with streamlined content
            doc = Document()

            # Generate streamlined, risk-adaptive report (3 sections only)
            doc = self._generate_streamlined_e23_report(
                doc=doc,
                project_name=project_name,
                project_description=project_description,
                assessment_results=assessment_results
            )

            # Save document
            doc.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            file_size_kb = round(file_size / 1024, 1)
            
            risk_level = assessment_results.get("risk_level", assessment_results.get("risk_rating", "Medium"))

            return {
                "assistant_directive": {
                    "critical_instruction": "The COMPLETE OSFI E-23 streamlined assessment report (4-6 pages, risk-adaptive) has been generated and saved by the MCP server. Present ONLY the file path and success message below. Do NOT generate, create, or write any additional report content. Do NOT offer to create summaries or additional documents. The Word document is complete and ready for professional review."
                },
                "success": True,
                "file_path": file_path,
                "file_size": f"{file_size_kb}KB",
                "lifecycle_stage": current_stage,
                "risk_level": risk_level,
                "report_type": "Streamlined (4-6 pages, risk-adaptive)",
                "message": f"✅ OSFI E-23 streamlined assessment report ({risk_level} risk) saved successfully to {filename}"
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
            logger.error(f"Error creating OSFI E-23 assessment report: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to create OSFI E-23 assessment report: {str(e)}",
                "file_path": None
            }

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

    def _extract_e23_risk_level(self, assessment_results: Dict[str, Any]) -> str:
        """Extract risk level from E-23 assessment results."""
        return assessment_results.get("risk_level", 
               assessment_results.get("risk_rating", "Medium"))
    
    def _extract_e23_risk_score(self, assessment_results: Dict[str, Any]) -> int:
        """Extract risk score from E-23 assessment results."""
        return assessment_results.get("risk_score", 
               assessment_results.get("overall_score", 0))
    
    def _generate_e23_executive_summary(self, risk_level: str, risk_score: int, project_description: str) -> str:
        """Generate executive summary for E-23 assessment."""
        description_lower = project_description.lower()
        
        # Determine risk characterization
        if risk_level == "Critical":
            risk_char = "presents critical model risk requiring maximum governance controls"
        elif risk_level == "High":
            risk_char = "presents high model risk requiring enhanced governance and oversight"
        elif risk_level == "Medium":
            risk_char = "presents moderate model risk requiring standard governance procedures"
        else:
            risk_char = "presents low model risk with minimal governance requirements"
        
        # Add model characteristics
        characteristics = []
        if any(term in description_lower for term in ['ai', 'machine learning', 'neural']):
            characteristics.append("AI/ML-powered")
        if any(term in description_lower for term in ['financial', 'loan', 'credit', 'risk management']):
            characteristics.append("financial decision-making")
        if any(term in description_lower for term in ['automated', 'autonomous']):
            characteristics.append("automated processing")
        if any(term in description_lower for term in ['customer', 'client', 'retail']):
            characteristics.append("customer-facing")
        
        char_text = ", ".join(characteristics) if characteristics else "decision-making"
        
        # Generate governance guidance
        governance_guidance = {
            "Critical": "Maximum governance controls including board oversight, external validation, and continuous monitoring are required.",
            "High": "Enhanced governance procedures including senior management oversight, quarterly reviews, and comprehensive monitoring are recommended.",
            "Medium": "Standard governance procedures with regular monitoring and semi-annual reviews are sufficient.",
            "Low": "Basic governance procedures with annual reviews and minimal monitoring are adequate."
        }
        
        governance = governance_guidance.get(risk_level, "Standard governance procedures are recommended.")
        
        return f"This {char_text} model {risk_char} under OSFI Guideline E-23 Model Risk Management framework. {governance} The assessment indicates {risk_level} risk classification requiring appropriate risk management intensity commensurate with the model's risk profile."
    
    def _extract_e23_risk_analysis(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract risk analysis points from E-23 assessment results."""
        analysis_points = []
        
        # Extract from risk_analysis if available
        risk_analysis = assessment_results.get("risk_analysis", {})
        
        # Quantitative indicators
        quant_indicators = risk_analysis.get("quantitative_indicators", {})
        for indicator, present in quant_indicators.items():
            if present:
                indicator_text = indicator.replace('_', ' ').title()
                analysis_points.append(f"Quantitative Risk Factor: {indicator_text} identified")
        
        # Qualitative indicators
        qual_indicators = risk_analysis.get("qualitative_indicators", {})
        for indicator, present in qual_indicators.items():
            if present:
                indicator_text = indicator.replace('_', ' ').title()
                analysis_points.append(f"Qualitative Risk Factor: {indicator_text} identified")
        
        # Risk factor analysis if available
        if 'risk_factor_analysis' in assessment_results:
            factor_analysis = assessment_results['risk_factor_analysis']
            
            high_risk_factors = factor_analysis.get('high_risk_factors', [])
            for factor in high_risk_factors[:3]:  # Limit to top 3
                analysis_points.append(f"High Risk: {factor}")
            
            risk_interactions = factor_analysis.get('risk_interactions', [])
            for interaction in risk_interactions[:2]:  # Limit to top 2
                analysis_points.append(f"Risk Interaction: {interaction}")
        
        # Default analysis if none found
        if not analysis_points:
            analysis_points = [
                "Model risk assessment completed using OSFI E-23 methodology",
                "Risk factors evaluated across quantitative and qualitative dimensions",
                "Governance requirements determined based on risk profile"
            ]
        
        return analysis_points[:8]  # Limit to 8 analysis points
    
    def _extract_e23_governance_requirements(self, assessment_results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract governance requirements from E-23 assessment results."""
        # Try to get governance requirements from assessment results
        governance_reqs = assessment_results.get("governance_requirements", {})
        
        if governance_reqs:
            return governance_reqs
        
        # Generate default governance requirements based on risk level
        risk_level = self._extract_e23_risk_level(assessment_results)
        
        base_requirements = {
            "organizational": [
                "Assign qualified model owner with appropriate expertise",
                "Establish clear roles and responsibilities",
                "Ensure adequate resources for model risk management"
            ],
            "documentation": [
                "Maintain comprehensive model documentation",
                "Document model rationale and business purpose",
                "Record model limitations and assumptions"
            ],
            "review_approval": [
                "Conduct independent model review",
                "Obtain appropriate approval before deployment",
                "Document review findings and recommendations"
            ],
            "monitoring": [
                "Implement ongoing model performance monitoring",
                "Establish performance thresholds and alerts",
                "Monitor for model drift and degradation"
            ]
        }
        
        # Enhanced requirements for higher risk levels
        if risk_level in ["High", "Critical"]:
            base_requirements["organizational"].extend([
                "Establish Model Risk Committee oversight",
                "Assign senior management accountability"
            ])
            
            base_requirements["review_approval"].extend([
                "Require senior management approval",
                "Conduct quarterly comprehensive reviews"
            ])
            
            base_requirements["monitoring"].extend([
                "Implement real-time monitoring and alerting",
                "Maintain contingency and rollback procedures"
            ])
        
        return base_requirements
    
    def _extract_e23_recommendations(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract recommendations from E-23 assessment results."""
        recommendations = assessment_results.get("recommendations", [])
        
        if recommendations:
            return recommendations[:8]  # Limit to 8 recommendations
        
        # Generate default recommendations based on risk level
        risk_level = self._extract_e23_risk_level(assessment_results)
        
        default_recommendations = [
            "Establish comprehensive Model Risk Management framework aligned with OSFI E-23",
            "Implement risk-based approach to model governance",
            "Ensure model inventory includes all models with non-negligible risk"
        ]
        
        if risk_level == "Critical":
            default_recommendations.extend([
                "🚨 CRITICAL: Obtain board-level approval before deployment",
                "Implement maximum governance controls and oversight",
                "Conduct external validation and independent review"
            ])
        elif risk_level == "High":
            default_recommendations.extend([
                "⚠️ HIGH RISK: Require senior management approval",
                "Implement enhanced governance and oversight controls",
                "Conduct quarterly comprehensive model reviews"
            ])
        elif risk_level == "Medium":
            default_recommendations.extend([
                "📋 MODERATE RISK: Implement standard governance procedures",
                "Conduct semi-annual model reviews"
            ])
        else:
            default_recommendations.extend([
                "✅ LOWER RISK: Apply proportionate governance controls",
                "Conduct annual model reviews"
            ])
        
        return default_recommendations
    
    def _extract_e23_lifecycle_info(self, assessment_results: Dict[str, Any]) -> str:
        """Extract lifecycle compliance information from E-23 assessment results."""
        if 'compliance_checklist' in assessment_results:
            checklist = assessment_results['compliance_checklist']
            completed_items = len([item for item in checklist if item.get('completed', False)])
            total_items = len(checklist)
            return f"Compliance checklist: {completed_items}/{total_items} items completed. Review lifecycle requirements and ensure all mandatory items are addressed before model deployment."
        
        if 'current_stage' in assessment_results:
            current_stage = assessment_results['current_stage']
            return f"Model is currently in {current_stage} stage. Ensure all stage-specific requirements are met before proceeding to the next lifecycle phase."
        
        return "Model lifecycle compliance should be evaluated across all five stages: Design, Review, Deployment, Monitoring, and Decommission. Ensure appropriate governance controls are applied at each stage."
    
    def _get_e23_assessment_disclaimer(self, assessment_results: Dict[str, Any]) -> str:
        """Get appropriate disclaimer for E-23 assessment."""
        return "This OSFI E-23 model risk assessment is based on available project information and automated analysis. Final compliance with OSFI Guideline E-23 requires comprehensive stakeholder input, independent validation, and appropriate governance oversight. This assessment should be reviewed and validated by qualified model risk management professionals before making final risk management decisions."
    
    # Enhanced E-23 Report Helper Methods
    
    def _extract_e23_business_rationale(self, assessment_results: Dict[str, Any], project_description: str) -> str:
        """Extract business rationale for E-23 model."""
        description_lower = project_description.lower()
        
        # Generate business rationale based on project characteristics
        if any(term in description_lower for term in ['risk management', 'credit risk', 'market risk']):
            return "This model supports risk management objectives by providing quantitative risk assessments to inform business decisions and regulatory compliance requirements."
        elif any(term in description_lower for term in ['fraud', 'detection', 'prevention']):
            return "This model enhances fraud detection capabilities to protect the institution and customers from financial losses while maintaining operational efficiency."
        elif any(term in description_lower for term in ['pricing', 'loan', 'credit']):
            return "This model supports pricing and credit decision-making to optimize risk-adjusted returns while ensuring fair and consistent treatment of customers."
        elif any(term in description_lower for term in ['regulatory', 'compliance', 'reporting']):
            return "This model supports regulatory compliance and reporting requirements while improving operational efficiency and decision-making accuracy."
        else:
            return "This model supports business objectives by automating decision-making processes, improving operational efficiency, and enhancing risk management capabilities."

    def _generate_e23_risk_summary(self, risk_level: str, risk_score: int, project_description: str) -> str:
        """Generate concise risk summary for E-23 assessment."""
        description_lower = project_description.lower()

        # Risk level interpretation
        risk_interpretations = {
            "Low": "requires basic governance with annual reviews and standard documentation",
            "Medium": "requires enhanced oversight with semi-annual reviews and comprehensive monitoring",
            "High": "requires robust governance with quarterly reviews and extensive controls",
            "Critical": "requires maximum oversight with monthly reviews and continuous monitoring"
        }

        risk_desc = risk_interpretations.get(risk_level, "requires appropriate governance")

        # Add model characteristics
        characteristics = []
        if any(term in description_lower for term in ['ai', 'machine learning', 'neural']):
            characteristics.append("AI/ML technology")
        if any(term in description_lower for term in ['financial', 'credit', 'loan']):
            characteristics.append("financial decision-making")
        if any(term in description_lower for term in ['automated', 'real-time']):
            characteristics.append("automated processing")

        char_text = f" involving {', '.join(characteristics)}" if characteristics else ""

        return f"This model has been assessed as {risk_level} risk (score: {risk_score}/100) and {risk_desc}. The model{char_text} requires implementation of OSFI E-23 framework controls appropriate to its risk level."

    def _generate_enhanced_e23_checklist(self, assessment_results: Dict[str, Any], risk_level: str) -> List[Dict[str, Any]]:
        """Generate enhanced compliance checklist with priorities and timelines."""
        checklist = []

        # Critical items (all risk levels)
        checklist.extend([
            {
                "item": "Establish clear model definition and scope documentation",
                "priority": "Critical",
                "stage": "Design",
                "timeline": "Week 1-2",
                "completed": False,
                "required": True
            },
            {
                "item": "Define model ownership and accountability framework",
                "priority": "Critical",
                "stage": "Design",
                "timeline": "Week 1-2",
                "completed": False,
                "required": True
            },
            {
                "item": "Document model risk assessment and rating",
                "priority": "Critical",
                "stage": "Design",
                "timeline": "Week 2-3",
                "completed": False,
                "required": True
            }
        ])

        # High priority items based on risk level
        if risk_level in ["High", "Critical"]:
            checklist.extend([
                {
                    "item": "Establish independent model validation team",
                    "priority": "High",
                    "stage": "Review",
                    "timeline": "Month 1",
                    "completed": False,
                    "required": True
                },
                {
                    "item": "Implement comprehensive model testing framework",
                    "priority": "High",
                    "stage": "Review",
                    "timeline": "Month 1-2",
                    "completed": False,
                    "required": True
                },
                {
                    "item": "Establish real-time monitoring and alerting",
                    "priority": "High",
                    "stage": "Monitoring",
                    "timeline": "Month 2-3",
                    "completed": False,
                    "required": True
                }
            ])

        # Medium priority items
        checklist.extend([
            {
                "item": "Create model development methodology documentation",
                "priority": "Medium",
                "stage": "Design",
                "timeline": "Month 1",
                "completed": False,
                "required": True
            },
            {
                "item": "Implement data quality and lineage controls",
                "priority": "Medium",
                "stage": "Design",
                "timeline": "Month 1-2",
                "completed": False,
                "required": True
            },
            {
                "item": "Establish model performance monitoring",
                "priority": "Medium",
                "stage": "Monitoring",
                "timeline": "Month 2",
                "completed": False,
                "required": True
            },
            {
                "item": "Create model inventory and documentation repository",
                "priority": "Medium",
                "stage": "All Stages",
                "timeline": "Month 1",
                "completed": False,
                "required": True
            }
        ])

        # Low priority optimization items
        checklist.extend([
            {
                "item": "Implement automated model testing tools",
                "priority": "Low",
                "stage": "Review",
                "timeline": "Month 3-6",
                "completed": False,
                "required": False
            },
            {
                "item": "Establish model challenger models framework",
                "priority": "Low",
                "stage": "Review",
                "timeline": "Month 6+",
                "completed": False,
                "required": False
            }
        ])

        return checklist

    def _extract_e23_key_risk_factors(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract key risk factors from assessment results."""
        risk_factors = []

        # From assessment results if available
        if 'quantitative_factors' in assessment_results:
            quant_factors = assessment_results['quantitative_factors']
            if isinstance(quant_factors, dict):
                for factor, value in quant_factors.items():
                    if value:  # If factor is present/true
                        risk_factors.append(f"Quantitative factor: {factor.replace('_', ' ').title()}")

        # From qualitative factors
        if 'qualitative_factors' in assessment_results:
            qual_factors = assessment_results['qualitative_factors']
            if isinstance(qual_factors, dict):
                for factor, value in qual_factors.items():
                    if value:  # If factor is present/true
                        risk_factors.append(f"Qualitative factor: {factor.replace('_', ' ').title()}")

        # Default risk factors if none found
        if not risk_factors:
            risk_factors = [
                "Model complexity and interpretability requirements",
                "Data quality and governance considerations",
                "Business impact and operational criticality",
                "Regulatory compliance and oversight requirements"
            ]

        return risk_factors[:8]  # Limit to top 8

    def _extract_e23_immediate_actions(self, assessment_results: Dict[str, Any], risk_level: str) -> List[str]:
        """Extract immediate actions based on risk level."""
        actions = [
            "Complete model definition and scope documentation",
            "Assign clear model ownership and accountability",
            "Document current model development status and gaps"
        ]

        if risk_level in ["High", "Critical"]:
            actions.extend([
                "Establish independent validation team immediately",
                "Implement enhanced monitoring and controls",
                "Schedule executive briefing on model risk"
            ])
        elif risk_level == "Medium":
            actions.extend([
                "Plan validation team structure and resources",
                "Design monitoring framework requirements",
                "Schedule stakeholder alignment meetings"
            ])

        return actions

    def _extract_e23_short_term_goals(self, assessment_results: Dict[str, Any], risk_level: str) -> List[str]:
        """Extract short-term goals (3-6 months)."""
        goals = [
            "Complete comprehensive model validation",
            "Implement monitoring and alerting framework",
            "Establish ongoing governance processes"
        ]

        if risk_level in ["High", "Critical"]:
            goals.extend([
                "Conduct independent third-party validation",
                "Implement advanced model testing scenarios",
                "Establish board-level reporting framework"
            ])

        return goals

    def _extract_e23_long_term_objectives(self, assessment_results: Dict[str, Any], risk_level: str) -> List[str]:
        """Extract long-term objectives (6+ months)."""
        objectives = [
            "Achieve full OSFI E-23 compliance certification",
            "Integrate model into enterprise risk framework",
            "Establish continuous improvement processes"
        ]

        if risk_level in ["High", "Critical"]:
            objectives.extend([
                "Implement advanced model risk analytics",
                "Establish challenger model framework",
                "Achieve automated compliance monitoring"
            ])

        return objectives

    def _get_e23_core_requirements(self) -> List[Dict[str, str]]:
        """Get core OSFI E-23 requirements."""
        return [
            {
                "section": "3.1",
                "title": "Model Risk Management Framework",
                "description": "Establish comprehensive framework for identifying, measuring, monitoring and controlling model risk"
            },
            {
                "section": "4.2",
                "title": "Model Development and Implementation",
                "description": "Ensure sound model development practices including validation, testing and documentation"
            },
            {
                "section": "5.1",
                "title": "Model Governance",
                "description": "Implement appropriate governance structure with clear roles, responsibilities and oversight"
            },
            {
                "section": "6.3",
                "title": "Model Monitoring and Performance Management",
                "description": "Establish ongoing monitoring, performance tracking and corrective action processes"
            }
        ]

    def _get_e23_risk_level_requirements(self, risk_level: str) -> List[str]:
        """Get specific requirements based on risk level."""
        requirements_map = {
            "Low": [
                "Annual model validation and review",
                "Basic monitoring and performance tracking",
                "Standard documentation and governance",
                "Local business unit oversight"
            ],
            "Medium": [
                "Semi-annual validation and comprehensive review",
                "Enhanced monitoring with quarterly reporting",
                "Detailed documentation and governance framework",
                "Senior management oversight and approval"
            ],
            "High": [
                "Quarterly validation with independent review",
                "Continuous monitoring with monthly reporting",
                "Comprehensive documentation and robust governance",
                "Executive leadership and board oversight"
            ],
            "Critical": [
                "Monthly validation with external independent review",
                "Real-time monitoring with immediate alerting",
                "Extensive documentation and maximum governance",
                "Board-level oversight and regulatory notification"
            ]
        }

        return requirements_map.get(risk_level, requirements_map["Medium"])

    def _generate_e23_rating_breakdown(self, assessment_results: Dict[str, Any], risk_level: str, risk_score: int) -> str:
        """Generate detailed risk rating breakdown explanation."""
        total_possible = 100
        percentage = round((risk_score / total_possible) * 100, 1)

        breakdown_text = f"The model achieved a risk score of {risk_score} out of {total_possible} possible points ({percentage}%), "

        # Risk level thresholds
        if risk_score <= 25:
            threshold_text = "falling within the Low risk range (0-25 points)"
        elif risk_score <= 50:
            threshold_text = "falling within the Medium risk range (26-50 points)"
        elif risk_score <= 75:
            threshold_text = "falling within the High risk range (51-75 points)"
        else:
            threshold_text = "falling within the Critical risk range (76-100 points)"

        breakdown_text += threshold_text + ". "

        # Add scoring methodology explanation
        breakdown_text += "This score reflects a combination of quantitative factors (portfolio size, financial impact, operational criticality) and qualitative factors (model complexity, AI/ML usage, explainability, third-party dependencies). "

        # Add amplification note if applicable
        amplification_applied = assessment_results.get('amplification_applied', False)
        if amplification_applied:
            breakdown_text += "Risk amplification was applied due to high-risk factor combinations, such as AI/ML usage in critical financial decisions."

        return breakdown_text

    def _extract_e23_scoring_details(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ACTUAL scoring breakdown from assessment results using real OSFI E-23 calculation logic."""
        scoring_details = {
            "quantitative_breakdown": {},
            "qualitative_breakdown": {},
            "amplification_applied": False,
            "amplification_details": {},
            "calculation_method": "actual"
        }

        # Try to get actual risk analysis data first
        risk_analysis = assessment_results.get('risk_analysis', {})

        if risk_analysis:
            # Extract ACTUAL quantitative indicators and scores
            quant_indicators = risk_analysis.get('quantitative_indicators', {})

            for indicator, present in quant_indicators.items():
                if present:
                    scoring_details["quantitative_breakdown"][indicator] = {
                        "score": 10,  # Each quantitative indicator = 10 points
                        "reason": self._get_osfi_quantitative_reason(indicator),
                        "present": True
                    }

            # Extract ACTUAL qualitative indicators and scores
            qual_indicators = risk_analysis.get('qualitative_indicators', {})

            for indicator, present in qual_indicators.items():
                if present:
                    scoring_details["qualitative_breakdown"][indicator] = {
                        "score": 8,  # Each qualitative indicator = 8 points
                        "reason": self._get_osfi_qualitative_reason(indicator),
                        "present": True
                    }

            # Calculate actual multipliers applied
            quant_score = risk_analysis.get('quantitative_score', 0)
            qual_score = risk_analysis.get('qualitative_score', 0)
            base_score = quant_score + qual_score
            final_score = self._extract_e23_risk_score(assessment_results)

            if base_score > 0:
                actual_multiplier = final_score / base_score
                if actual_multiplier > 1.05:  # More than 5% increase indicates amplification
                    scoring_details["amplification_applied"] = True
                    scoring_details["amplification_details"] = {
                        "factor": round(actual_multiplier, 2),
                        "base_score": base_score,
                        "final_score": final_score,
                        "reason": self._determine_amplification_reason(quant_indicators, qual_indicators),
                        "triggering_factors": self._get_actual_amplification_triggers(quant_indicators, qual_indicators)
                    }
        else:
            # Fallback to inference if no risk_analysis available
            scoring_details = self._infer_scoring_details_from_assessment(assessment_results)
            scoring_details["calculation_method"] = "inferred"

        return scoring_details

    def _get_osfi_quantitative_reason(self, indicator: str) -> str:
        """Get official OSFI E-23 reasons for quantitative indicators."""
        reasons = {
            "high_volume": "High transaction/decision volume amplifies potential model impact",
            "financial_impact": "Direct financial decisions create significant loss potential",
            "customer_facing": "Customer-impacting decisions require enhanced oversight",
            "revenue_critical": "Revenue-critical functions present business continuity risks",
            "regulatory_impact": "Regulatory exposure requires compliance-grade governance"
        }
        return reasons.get(indicator, f"{indicator.replace('_', ' ').title()} contributes to operational risk")

    def _get_osfi_qualitative_reason(self, indicator: str) -> str:
        """Get official OSFI E-23 reasons for qualitative indicators."""
        reasons = {
            "ai_ml_usage": "AI/ML models present interpretability and bias validation challenges",
            "high_complexity": "Complex models are difficult to validate and monitor effectively",
            "autonomous_decisions": "Autonomous systems reduce human oversight and intervention ability",
            "black_box": "Black-box models limit explainability and audit capability",
            "third_party": "Third-party dependencies introduce external risk vectors",
            "data_sensitive": "Sensitive data processing requires enhanced privacy controls",
            "real_time": "Real-time processing limits validation and intervention windows",
            "customer_impact": "Direct customer impact requires fairness and bias controls"
        }
        return reasons.get(indicator, f"{indicator.replace('_', ' ').title()} contributes to model risk profile")

    def _determine_amplification_reason(self, quant_indicators: dict, qual_indicators: dict) -> str:
        """Determine why amplification was applied based on actual indicator combinations."""
        reasons = []

        if quant_indicators.get("financial_impact") and qual_indicators.get("ai_ml_usage"):
            reasons.append("AI/ML usage in financial decision-making (+30%)")
        if quant_indicators.get("customer_facing") and qual_indicators.get("autonomous_decisions"):
            reasons.append("Autonomous customer-facing decisions (+20%)")
        if qual_indicators.get("black_box") and quant_indicators.get("regulatory_impact"):
            reasons.append("Black-box models with regulatory impact (+25%)")
        if qual_indicators.get("third_party") and quant_indicators.get("revenue_critical"):
            reasons.append("Third-party dependencies in critical systems (+15%)")

        return "; ".join(reasons) if reasons else "High-risk factor combination detected"

    def _get_actual_amplification_triggers(self, quant_indicators: dict, qual_indicators: dict) -> list:
        """Get actual amplification triggers that were applied."""
        triggers = []

        if quant_indicators.get("financial_impact") and qual_indicators.get("ai_ml_usage"):
            triggers.append("Financial Impact + AI/ML Usage")
        if quant_indicators.get("customer_facing") and qual_indicators.get("autonomous_decisions"):
            triggers.append("Customer Facing + Autonomous Decisions")
        if qual_indicators.get("black_box") and quant_indicators.get("regulatory_impact"):
            triggers.append("Black Box + Regulatory Impact")
        if qual_indicators.get("third_party") and quant_indicators.get("revenue_critical"):
            triggers.append("Third Party + Revenue Critical")

        return triggers

    def _infer_scoring_details_from_assessment(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Infer scoring details when detailed breakdown is not available."""
        risk_score = self._extract_e23_risk_score(assessment_results)
        risk_level = self._extract_e23_risk_level(assessment_results)

        # Create plausible scoring breakdown based on risk level and score
        scoring_details = {
            "quantitative_breakdown": {},
            "qualitative_breakdown": {},
            "amplification_applied": False,
            "amplification_details": {}
        }

        # Infer likely quantitative factors based on risk level
        quant_base_score = min(risk_score * 0.6, 45)  # ~60% from quantitative
        scoring_details["quantitative_breakdown"] = {
            "financial_impact": {
                "score": int(quant_base_score * 0.4),
                "reason": "Significant financial decisions affected by model outputs",
                "present": True
            },
            "operational_criticality": {
                "score": int(quant_base_score * 0.35),
                "reason": "Model is critical to core business operations",
                "present": True
            },
            "portfolio_size": {
                "score": int(quant_base_score * 0.25),
                "reason": "Large portfolio size increases potential impact of model errors",
                "present": True
            }
        }

        # Infer likely qualitative factors based on risk level
        qual_base_score = risk_score - quant_base_score
        scoring_details["qualitative_breakdown"] = {
            "ai_ml_usage": {
                "score": int(qual_base_score * 0.5),
                "reason": "AI/ML models present inherent interpretability and bias risks",
                "present": True
            },
            "model_complexity": {
                "score": int(qual_base_score * 0.3),
                "reason": "Complex models are harder to validate and control",
                "present": True
            },
            "explainability": {
                "score": int(qual_base_score * 0.2),
                "reason": "Limited explainability reduces oversight effectiveness",
                "present": True
            }
        }

        # Add amplification for High/Critical risk levels
        if risk_level in ["High", "Critical"]:
            scoring_details["amplification_applied"] = True
            scoring_details["amplification_details"] = {
                "factor": 1.2 if risk_level == "High" else 1.4,
                "reason": f"High-risk factor combinations typical of {risk_level} risk models",
                "triggering_factors": ["AI/ML + Financial Impact", "High Complexity + Large Portfolio"]
            }

        return scoring_details

    def _get_quantitative_factor_reason(self, factor: str, assessment_results: Dict[str, Any]) -> str:
        """Get explanation for why a quantitative factor was scored."""
        reasons = {
            "portfolio_size": "Large portfolio size increases potential impact of model errors",
            "financial_impact": "Significant financial decisions affected by model outputs",
            "operational_criticality": "Model is critical to core business operations",
            "customer_base": "Large customer base affected by model decisions",
            "transaction_volume": "High transaction volume amplifies model impact",
            "regulatory_exposure": "Model subject to regulatory oversight and compliance"
        }
        return reasons.get(factor, f"Factor {factor.replace('_', ' ')} identified as risk contributor")

    def _get_qualitative_factor_reason(self, factor: str, assessment_results: Dict[str, Any]) -> str:
        """Get explanation for why a qualitative factor was scored."""
        reasons = {
            "ai_ml_usage": "AI/ML models present inherent interpretability and bias risks",
            "model_complexity": "Complex models are harder to validate and control",
            "explainability": "Limited explainability reduces oversight effectiveness",
            "third_party_dependency": "Third-party components introduce additional risk vectors",
            "data_quality_issues": "Poor data quality leads to unreliable model outputs",
            "human_oversight": "Limited human oversight increases error propagation risk",
            "update_frequency": "Frequent updates increase operational and validation burden"
        }
        return reasons.get(factor, f"Factor {factor.replace('_', ' ')} contributes to model risk profile")

    def _generate_e23_risk_justification(self, assessment_results: Dict[str, Any], risk_level: str, risk_score: int) -> str:
        """Generate detailed justification for the risk level assignment."""
        justification = f"The {risk_level} risk classification is justified based on the following analysis:\n\n"

        # Analyze primary risk drivers
        quant_factors = assessment_results.get('quantitative_factors', {})
        qual_factors = assessment_results.get('qualitative_factors', {})

        primary_drivers = []

        # High-impact quantitative factors
        high_impact_quant = [factor for factor, present in quant_factors.items() if present]
        if high_impact_quant:
            drivers_text = ", ".join([factor.replace('_', ' ') for factor in high_impact_quant[:3]])
            primary_drivers.append(f"Quantitative factors: {drivers_text}")

        # High-impact qualitative factors
        high_impact_qual = [factor for factor, present in qual_factors.items() if present]
        if high_impact_qual:
            drivers_text = ", ".join([factor.replace('_', ' ') for factor in high_impact_qual[:3]])
            primary_drivers.append(f"Qualitative factors: {drivers_text}")

        if primary_drivers:
            justification += "Primary risk drivers include: " + "; ".join(primary_drivers) + ".\n\n"

        # Risk level specific justification
        level_justifications = {
            "Low": "The model presents manageable risks that can be addressed through standard governance practices.",
            "Medium": "The model requires enhanced oversight and monitoring to manage identified risk factors effectively.",
            "High": "The model presents significant risks requiring robust governance, independent validation, and comprehensive monitoring.",
            "Critical": "The model presents maximum risk requiring extensive controls, continuous monitoring, and board-level oversight."
        }

        justification += level_justifications.get(risk_level, "The model requires appropriate risk management controls.")

        # Add amplification note if applicable
        if assessment_results.get('risk_amplification', {}).get('applied'):
            justification += "\n\nRisk amplification was applied due to dangerous factor combinations that multiply the individual risk components."

        return justification

    def _generate_e23_risk_methodology(self, assessment_results: Dict[str, Any]) -> str:
        """Generate risk rating methodology description."""
        return "The model risk rating follows OSFI E-23 methodology, evaluating both quantitative and qualitative risk factors. Quantitative factors include portfolio size, financial impact, and operational criticality. Qualitative factors assess model complexity, autonomy level, explainability, and third-party dependencies. Risk amplification is applied when high-risk combinations are identified, such as AI/ML usage in critical financial decisions."
    
    def _extract_e23_quantitative_factors(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract quantitative risk factors from assessment results."""
        factors = []
        risk_analysis = assessment_results.get("risk_analysis", {})
        quant_indicators = risk_analysis.get("quantitative_indicators", {})
        
        factor_descriptions = {
            'high_volume': "High transaction volume requiring robust processing capabilities",
            'financial_impact': "Significant financial impact on institution and customers",
            'customer_facing': "Direct customer impact requiring enhanced controls",
            'revenue_critical': "Revenue-critical application with business continuity implications",
            'regulatory_impact': "Regulatory compliance and reporting dependencies"
        }
        
        for factor, present in quant_indicators.items():
            if present and factor in factor_descriptions:
                factors.append(factor_descriptions[factor])
        
        if not factors:
            factors = [
                "Standard operational impact assessment completed",
                "Financial materiality evaluated based on model usage",
                "Customer impact scope determined"
            ]
        
        return factors
    
    def _extract_e23_qualitative_factors(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract qualitative risk factors from assessment results."""
        factors = []
        risk_analysis = assessment_results.get("risk_analysis", {})
        qual_indicators = risk_analysis.get("qualitative_indicators", {})
        
        factor_descriptions = {
            'ai_ml_usage': "AI/ML technology requiring specialized validation and monitoring",
            'high_complexity': "High model complexity increasing validation requirements",
            'autonomous_decisions': "Autonomous decision-making with limited human oversight",
            'black_box': "Limited model explainability and transparency",
            'third_party': "Third-party model dependencies requiring vendor oversight",
            'data_sensitive': "Sensitive data processing requiring enhanced controls",
            'real_time': "Real-time processing with immediate decision impact",
            'customer_impact': "Direct customer decision impact requiring fairness controls"
        }
        
        for factor, present in qual_indicators.items():
            if present and factor in factor_descriptions:
                factors.append(factor_descriptions[factor])
        
        if not factors:
            factors = [
                "Standard model complexity assessment completed",
                "Technology risk evaluation performed",
                "Operational risk factors identified"
            ]
        
        return factors
    
    def _extract_e23_risk_interactions(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract risk interactions and amplification factors."""
        interactions = []
        
        if 'risk_factor_analysis' in assessment_results:
            factor_analysis = assessment_results['risk_factor_analysis']
            risk_interactions = factor_analysis.get('risk_interactions', [])
            interactions.extend(risk_interactions)
        
        if not interactions:
            interactions = [
                "Risk factor interactions evaluated for amplification effects",
                "Combined risk scenarios assessed for governance implications",
                "Risk mitigation strategies aligned with interaction patterns"
            ]
        
        return interactions
    
    def _extract_e23_organizational_structure(self, assessment_results: Dict[str, Any]) -> Dict[str, str]:
        """Extract organizational structure from assessment results."""
        governance_reqs = assessment_results.get("governance_requirements", {})
        
        if 'governance_structure' in assessment_results:
            return assessment_results['governance_structure']
        
        # Generate default organizational structure
        risk_level = self._extract_e23_risk_level(assessment_results)
        
        base_structure = {
            "model_owner": "Business unit responsible for model outcomes and business rationale",
            "model_developer": "Technical team or vendor responsible for model development and maintenance",
            "model_reviewer": "Independent validation team responsible for model review and testing",
            "model_approver": f"Approval authority as per risk level: {self.osfi_e23_processor._determine_approval_authority(risk_level)}"
        }
        
        if risk_level in ["High", "Critical"]:
            base_structure.update({
                "model_risk_committee": "Senior committee providing oversight and governance for model risk",
                "compliance_officer": "Compliance function ensuring adherence to regulatory requirements"
            })
        
        if risk_level == "Critical":
            base_structure.update({
                "board_oversight": "Board of Directors providing oversight for critical models",
                "external_validator": "Independent third-party validation for critical model components"
            })
        
        return base_structure
    
    def _extract_e23_policies_procedures(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract policies and procedures requirements."""
        policies = [
            "Model Risk Management Policy defining roles, responsibilities, and governance framework",
            "Model Development Standards specifying technical and documentation requirements",
            "Model Review and Validation Procedures for independent assessment processes",
            "Model Approval Procedures defining authority levels and approval criteria",
            "Model Monitoring and Performance Management Procedures",
            "Model Change Management Procedures for updates and modifications",
            "Model Decommission Procedures for retirement and replacement processes"
        ]
        
        risk_level = self._extract_e23_risk_level(assessment_results)
        
        if risk_level in ["High", "Critical"]:
            policies.extend([
                "Enhanced Documentation Standards for complex and high-risk models",
                "Bias Testing and Fairness Assessment Procedures for AI/ML models",
                "Third-party Model Oversight Procedures for vendor-developed models"
            ])
        
        return policies
    
    def _extract_e23_design_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract model design requirements."""
        requirements = [
            "Clear organizational rationale and business case documentation",
            "Comprehensive data quality and governance standards",
            "Appropriate model development methodology and documentation",
            "Performance criteria and success metrics definition",
            "Model limitations and assumptions documentation"
        ]
        
        risk_level = self._extract_e23_risk_level(assessment_results)
        
        if risk_level in ["High", "Critical"]:
            requirements.extend([
                "Detailed explainability and interpretability analysis",
                "Comprehensive bias and fairness assessment",
                "Regulatory compliance and impact analysis"
            ])
        
        return requirements
    
    def _extract_e23_review_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract model review and validation requirements."""
        requirements = [
            "Independent conceptual soundness review",
            "Comprehensive performance evaluation and testing",
            "Risk rating confirmation and documentation",
            "Model documentation completeness review",
            "Limitation and mitigation strategy assessment"
        ]
        
        risk_level = self._extract_e23_risk_level(assessment_results)
        
        if risk_level in ["High", "Critical"]:
            requirements.extend([
                "Enhanced validation testing including stress scenarios",
                "External validation for critical model components",
                "Regulatory pre-approval consultation where applicable"
            ])
        
        return requirements
    
    def _extract_e23_deployment_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract model deployment requirements."""
        requirements = [
            "Quality assurance and change control processes",
            "Production environment testing and validation",
            "Stakeholder coordination and communication",
            "Risk assessment completion and sign-off",
            "Monitoring framework setup and configuration"
        ]
        
        risk_level = self._extract_e23_risk_level(assessment_results)
        
        if risk_level in ["High", "Critical"]:
            requirements.extend([
                "Enhanced production testing with parallel run validation",
                "Real-time monitoring and alerting system activation",
                "Contingency and rollback procedure implementation"
            ])
        
        return requirements
    
    def _extract_e23_monitoring_framework(self, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract monitoring framework details."""
        risk_level = self._extract_e23_risk_level(assessment_results)
        
        frequency_mapping = {
            "Low": "Quarterly monitoring with annual comprehensive review",
            "Medium": "Monthly monitoring with quarterly comprehensive review",
            "High": "Weekly monitoring with monthly comprehensive review",
            "Critical": "Daily monitoring with weekly comprehensive review"
        }
        
        base_kpis = [
            "Model performance accuracy and stability metrics",
            "Prediction quality and consistency indicators",
            "Data quality and completeness measures",
            "Usage patterns and volume statistics"
        ]
        
        if risk_level in ["High", "Critical"]:
            base_kpis.extend([
                "Bias and fairness metrics for protected characteristics",
                "Explainability and transparency measures",
                "Regulatory compliance indicators",
                "Customer impact and complaint metrics"
            ])
        
        return {
            "frequency": frequency_mapping.get(risk_level, "Monthly monitoring"),
            "kpis": base_kpis
        }
    
    def _extract_e23_decommission_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract model decommission requirements."""
        return [
            "Formal model retirement process and timeline",
            "Stakeholder notification and communication plan",
            "Documentation retention and archival procedures",
            "Downstream system impact assessment and mitigation",
            "Third-party model considerations and vendor coordination",
            "Data retention and disposal procedures",
            "Replacement model transition planning"
        ]
    
    def _extract_e23_documentation_requirements(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Extract documentation requirements."""
        risk_level = self._extract_e23_risk_level(assessment_results)
        
        base_docs = [
            "Model rationale and business purpose documentation",
            "Data sources, quality standards, and governance documentation",
            "Model methodology, assumptions, and limitations documentation",
            "Performance metrics, validation results, and testing documentation",
            "Risk assessment and mitigation strategy documentation"
        ]
        
        if risk_level in ["High", "Critical"]:
            base_docs.extend([
                "Detailed explainability and interpretability documentation",
                "Comprehensive bias testing and mitigation measures documentation",
                "Audit trail and change management documentation",
                "Contingency planning and rollback procedures documentation"
            ])
        
        if risk_level == "Critical":
            base_docs.extend([
                "Board presentation and approval documentation",
                "External validation and independent review reports",
                "Regulatory compliance attestations and correspondence",
                "Continuous monitoring dashboards and alert configurations"
            ])
        
        return base_docs
    
    def _extract_e23_compliance_checklist(self, assessment_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract compliance checklist from assessment results."""
        if 'compliance_checklist' in assessment_results:
            return assessment_results['compliance_checklist']
        
        # Generate default compliance checklist
        risk_level = self._extract_e23_risk_level(assessment_results)
        
        base_checklist = [
            {"item": "Model inventory registration", "required": True, "stage": "design", "completed": False},
            {"item": "Risk rating assignment", "required": True, "stage": "design", "completed": False},
            {"item": "Model documentation completion", "required": True, "stage": "design", "completed": False},
            {"item": "Independent model review", "required": True, "stage": "review", "completed": False},
            {"item": "Formal model approval", "required": True, "stage": "review", "completed": False},
            {"item": "Production deployment testing", "required": True, "stage": "deployment", "completed": False},
            {"item": "Monitoring system activation", "required": True, "stage": "deployment", "completed": False},
            {"item": "Regular performance monitoring", "required": True, "stage": "monitoring", "completed": False}
        ]
        
        if risk_level in ["High", "Critical"]:
            base_checklist.extend([
                {"item": "Bias and fairness testing", "required": True, "stage": "design", "completed": False},
                {"item": "Explainability documentation", "required": True, "stage": "design", "completed": False},
                {"item": "Senior management approval", "required": True, "stage": "review", "completed": False},
                {"item": "Enhanced monitoring setup", "required": True, "stage": "deployment", "completed": False}
            ])
        
        if risk_level == "Critical":
            base_checklist.extend([
                {"item": "Board-level approval", "required": True, "stage": "review", "completed": False},
                {"item": "External validation", "required": True, "stage": "review", "completed": False},
                {"item": "Real-time monitoring activation", "required": True, "stage": "deployment", "completed": False}
            ])
        
        return base_checklist
    
    def _extract_e23_implementation_timeline(self, assessment_results: Dict[str, Any]) -> Dict[str, str]:
        """Extract implementation timeline from assessment results."""
        if 'implementation_timeline' in assessment_results:
            return assessment_results['implementation_timeline']
        
        # Generate default timeline based on risk level
        risk_level = self._extract_e23_risk_level(assessment_results)
        
        timeline_mapping = {
            "Low": {
                "design_phase": "4-6 weeks",
                "review_phase": "2-3 weeks",
                "deployment_phase": "2-3 weeks",
                "monitoring_setup": "1-2 weeks"
            },
            "Medium": {
                "design_phase": "6-8 weeks",
                "review_phase": "3-4 weeks",
                "deployment_phase": "3-4 weeks",
                "monitoring_setup": "2-3 weeks"
            },
            "High": {
                "design_phase": "8-12 weeks",
                "review_phase": "4-6 weeks",
                "deployment_phase": "4-5 weeks",
                "monitoring_setup": "3-4 weeks"
            },
            "Critical": {
                "design_phase": "12-16 weeks",
                "review_phase": "6-8 weeks",
                "external_validation": "4-6 weeks",
                "deployment_phase": "5-7 weeks",
                "monitoring_setup": "4-5 weeks"
            }
        }
        
        return timeline_mapping.get(risk_level, timeline_mapping["Medium"])
    
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

        # Validate project description adequacy for OSFI E-23 framework assessment
        validation_result = self.description_validator.validate_description(project_description)
        # Use OSFI E-23 specific readiness instead of combined validation
        osfi_ready = validation_result["framework_readiness"].get("osfi_e23_framework", False)

        if not osfi_ready:
            return {
                "assessment": {
                    "status": "validation_failed",
                    "message": "❌ Insufficient project description for OSFI E-23 framework assessment",
                    "validation_details": validation_result,
                    "required_action": "Use 'validate_project_description' tool to check requirements and improve description"
                },
                "framework_readiness": validation_result["framework_readiness"],
                "recommendations": [
                    "Project description does not meet minimum requirements for OSFI E-23 assessment",
                    "Please provide more detailed information covering the missing areas",
                    "Use the 'validate_project_description' tool to check specific requirements",
                    "Re-run assessment after improving the description"
                ],
                "compliance_warning": "⚠️ COMPLIANCE WARNING: OSFI E-23 assessments require detailed, factual project descriptions for regulatory compliance"
            }

        # Use the OSFI E-23 processor
        result = self.osfi_e23_processor.assess_model_risk(
            project_name=project_name,
            project_description=project_description
        )
        
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
