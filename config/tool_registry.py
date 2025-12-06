"""
Tool Registry Module

Manages MCP tool definitions and registration.
Extracted from server.py to reduce complexity and improve maintainability.
"""

from typing import List, Dict, Any


class ToolRegistry:
    """
    Registry for MCP tool definitions.

    Centralizes tool metadata, descriptions, and input schemas
    for the Model Context Protocol server.
    """

    @staticmethod
    def get_tools() -> List[Dict[str, Any]]:
        """
        Get complete list of MCP tool definitions.

        Returns:
            List of tool definition dictionaries with name, description, and inputSchema
        """
        return [
            {
                "name": "get_server_introduction",
                "description": "🚨 CRITICAL FIRST CALL - CALL THIS ALONE: This tool MUST be called BY ITSELF at the START of any assessment conversation.\n\n⚠️ CALL THIS TOOL ALONE - Do NOT call other tools in the same response!\n\n✨ NEW: SMART FRAMEWORK DETECTION - This tool now automatically detects which framework the user needs based on context, showing only the relevant workflow to reduce confusion.\n\nWHEN TO CALL THIS TOOL:\nCall IMMEDIATELY when a user:\n- Says 'run through OSFI framework' or 'run through AIA'\n- Wants to assess, evaluate, or analyze a project/system/model\n- Mentions AIA, OSFI, or compliance/regulatory requirements\n- Provides a project description asking for assessment\n- Asks about which framework to use or available workflows\n- Says they're starting a new assessment or compliance process\n- Any variation of 'help me with [AI/model/system] compliance'\n\nHOW IT WORKS:\n- If user mentions 'OSFI', 'bank', 'financial institution' → Shows ONLY OSFI E-23 workflow\n- If user mentions 'AIA', 'government', 'federal' → Shows ONLY AIA workflow\n- If context is unclear → Shows BOTH workflows and asks user to choose\n- You can pass the user's message as 'user_context' for better detection\n\nWHAT THIS TOOL PROVIDES:\n- Framework-specific or combined introduction based on context\n- Complete workflow sequences (5 steps for OSFI E-23, 5 steps for AIA)\n- Framework selection guidance if context unclear\n- Critical data source distinctions (MCP official data vs AI interpretation)\n\nWHAT TO DO AFTER CALLING THIS TOOL:\n1. PRESENT the introduction (either AIA-only, OSFI-only, or both)\n2. If only one framework shown: Proceed with Step 1 unless user wants options\n3. If both frameworks shown: ASK which one applies and WAIT for response\n4. THEN follow the appropriate workflow sequence step-by-step\n\nEXAMPLES:\n\nScenario 1 - Clear OSFI Context:\nUser: 'Run through OSFI framework for my credit model'\nClaude: [Calls get_server_introduction with user_context='Run through OSFI framework for my credit model']\nClaude: [Shows ONLY OSFI E-23 5-step workflow]\nClaude: 'I'll guide you through OSFI E-23 compliance. Let's start with Step 1...'\n\nScenario 2 - Clear AIA Context:\nUser: 'I need an AIA for my benefits system'\nClaude: [Calls get_server_introduction with user_context='I need an AIA for my benefits system']\nClaude: [Shows ONLY AIA 5-step workflow]\nClaude: 'I'll help with the Algorithmic Impact Assessment. Let's start with Step 1...'\n\nScenario 3 - Unclear Context:\nUser: 'Help me assess my AI system'\nClaude: [Calls get_server_introduction with user_context='Help me assess my AI system']\nClaude: [Shows BOTH workflows]\nClaude: 'Which framework applies? OSFI E-23 for financial institutions, or AIA for government?'",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_context": {
                            "type": "string",
                            "description": "Optional: The user's message or project context for framework detection. Include this to enable smart framework detection (e.g., user mentions 'OSFI' → show only OSFI workflow, user mentions 'AIA' → show only AIA workflow). If omitted, shows both frameworks by default."
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Optional: Session ID for context detection from existing workflow"
                        }
                    },
                    "additionalProperties": False
                }
            },
            {
                "name": "validate_project_description",
                "description": "🔍 STEP 1 OF 3 - FRAMEWORK READINESS VALIDATOR: Validate project descriptions for adequacy before conducting AIA or OSFI E-23 assessments. OSFI E-23 WORKFLOW: (1) validate_project_description [YOU ARE HERE] → (2) assess_model_risk → (3) export_e23_report. Ensures descriptions contain sufficient information across key areas required by both frameworks.",
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
                "description": "🏦 OSFI E-23 STEP 2 OF 3 - MODEL RISK ASSESSMENT: Comprehensive model risk assessment using 6 Risk Dimensions (31 factors) under Canada's OSFI Guideline E-23 framework. TWO-PHASE WORKFLOW: (1) First call returns extraction prompt for Claude to analyze description and extract risk factor values; (2) Second call with extracted_factors performs deterministic scoring. User must confirm lifecycle stage before proceeding. COMPLETE OSFI WORKFLOW: (1) validate_project_description → (2) assess_model_risk [YOU ARE HERE] → (3) export_e23_report. ⚠️ COMPLIANCE WARNING: All results must be validated by qualified model risk professionals.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the model being assessed"
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "CRITICAL: Provide factual, detailed description including specific technical architecture, documented data sources/volumes, explicit business use cases, defined decision-making processes, and measurable performance criteria."
                        },
                        "currentStage": {
                            "type": "string",
                            "description": "Current lifecycle stage of the model. User should confirm this before proceeding.",
                            "enum": ["design", "review", "deployment", "monitoring", "decommission"]
                        },
                        "extracted_factors": {
                            "type": "object",
                            "description": "PHASE 2 ONLY: JSON object containing extracted risk factor values from Claude's analysis of the project description. Required structure: { 'dimensions': { 'dimension_id': { 'factor_id': { 'value': <number|string|NOT_STATED>, 'evidence': <string|null> } } } }. If not provided, returns extraction prompt for Phase 1."
                        }
                    },
                    "required": ["projectName", "projectDescription", "currentStage"],
                    "additionalProperties": False
                }
            },
            {
                "name": "export_e23_report",
                "description": "🏦 OSFI E-23 STEP 3 OF 3 - REPORT GENERATION: Generates a stage-specific OSFI E-23 compliance report as a Microsoft Word document. COMPLETE OSFI WORKFLOW: (1) validate_project_description → (2) assess_model_risk → (3) export_e23_report [YOU ARE HERE]. Report includes executive summary, 6 Risk Dimensions assessment, lifecycle requirements scaled by risk level, and OSFI principles annex. ⚠️ COMPLIANCE WARNING: Generated reports require professional validation before regulatory use.",
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
                            "description": "OPTIONAL: Assessment results from Step 2 (assess_model_risk). If not provided, will retrieve from session state."
                        },
                        "current_stage": {
                            "type": "string",
                            "description": "Current lifecycle stage (from Step 2). Required for generating stage-specific requirements.",
                            "enum": ["design", "review", "deployment", "monitoring", "decommission"]
                        },
                        "custom_filename": {
                            "type": "string",
                            "description": "Optional custom filename (without extension). Default: OSFI_E23_Report_[ProjectName]_[YYYY-MM-DD].docx"
                        }
                    },
                    "required": ["project_name", "project_description"],
                    "additionalProperties": False
                }
            }
        ]

    @staticmethod
    def format_list_tools_response(request_id: Any) -> Dict[str, Any]:
        """
        Format tools list as MCP list_tools response.

        Args:
            request_id: The JSON-RPC request ID

        Returns:
            Formatted JSON-RPC response with tools list
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": ToolRegistry.get_tools()
            }
        }
