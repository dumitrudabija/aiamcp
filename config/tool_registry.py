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
                "description": (
                    "Get an introduction to the available regulatory assessment frameworks "
                    "(Canada's AIA and OSFI E-23) with step-by-step workflow guidance. "
                    "Call this at the start of an assessment conversation to understand "
                    "which tools to use and in what order. Automatically detects whether "
                    "the user needs AIA (government automated decisions) or OSFI E-23 "
                    "(financial institution model risk) based on context."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_context": {
                            "type": "string",
                            "description": "The user's message or project context to detect which framework applies."
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Optional session ID from an existing workflow."
                        }
                    }
                }
            },
            {
                "name": "validate_project_description",
                "description": (
                    "Validate that a project description contains enough information to run "
                    "an AIA or OSFI E-23 assessment. Checks coverage across 6 content areas "
                    "(system/technology, business purpose, data sources, impact scope, "
                    "decision process, technical architecture). Call this before starting "
                    "any framework assessment. Returns pass/fail with specific feedback on "
                    "what information is missing."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the project being validated."
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "Full project description to validate."
                        }
                    },
                    "required": ["projectName", "projectDescription"]
                }
            },
            {
                "name": "create_workflow",
                "description": (
                    "Create a managed assessment workflow session for AIA or OSFI E-23. "
                    "Returns a session ID used to track progress through the multi-step "
                    "assessment. Assessment type is auto-detected from the description if "
                    "not specified."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the project."
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "Project description."
                        },
                        "assessmentType": {
                            "type": "string",
                            "description": "Type of assessment: aia_full, aia_preview, osfi_e23, or combined.",
                            "enum": ["aia_full", "aia_preview", "osfi_e23", "combined"]
                        }
                    },
                    "required": ["projectName", "projectDescription"]
                }
            },
            {
                "name": "execute_workflow_step",
                "description": (
                    "Execute a specific step within an active workflow session. "
                    "Handles state tracking and dependency validation automatically."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sessionId": {
                            "type": "string",
                            "description": "Workflow session ID from create_workflow."
                        },
                        "toolName": {
                            "type": "string",
                            "description": "Name of the tool to execute."
                        },
                        "toolArguments": {
                            "type": "object",
                            "description": "Arguments for the tool."
                        }
                    },
                    "required": ["sessionId", "toolName", "toolArguments"]
                }
            },
            {
                "name": "get_workflow_status",
                "description": "Get the current progress and next recommended steps for an active workflow session.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sessionId": {
                            "type": "string",
                            "description": "Workflow session ID."
                        }
                    },
                    "required": ["sessionId"]
                }
            },
            {
                "name": "auto_execute_workflow",
                "description": "Automatically execute the next available steps in a workflow session, up to a specified number of steps.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "sessionId": {
                            "type": "string",
                            "description": "Workflow session ID."
                        },
                        "stepsToExecute": {
                            "type": "number",
                            "description": "Number of steps to auto-execute (default: 1, max: 5).",
                            "minimum": 1,
                            "maximum": 5
                        }
                    },
                    "required": ["sessionId"]
                }
            },
            {
                "name": "assess_project",
                "description": (
                    "Calculate the official AIA (Algorithmic Impact Assessment) risk score "
                    "from actual user responses to AIA questionnaire questions. Returns a "
                    "risk level (I–IV) and score out of 224. Requires the user to have "
                    "answered the AIA questions — do not fabricate responses."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the project."
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "Project description."
                        },
                        "responses": {
                            "type": "array",
                            "description": "Array of question responses with questionId and selectedOption (numeric index).",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "questionId": {"type": "string"},
                                    "selectedOption": {"type": "number"}
                                },
                                "required": ["questionId", "selectedOption"]
                            }
                        }
                    },
                    "required": ["projectName", "projectDescription"]
                }
            },
            {
                "name": "analyze_project_description",
                "description": (
                    "Analyze a project description against Canada's AIA framework questions. "
                    "Automatically answers questions where the description provides enough "
                    "information and flags questions that require manual input from the user."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the project."
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "Detailed project description."
                        }
                    },
                    "required": ["projectName", "projectDescription"]
                }
            },
            {
                "name": "get_questions",
                "description": (
                    "Get Canada's official AIA questionnaire questions. "
                    "Optionally filter by category or type (risk/mitigation)."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Filter by category.",
                            "enum": ["Project", "System", "Algorithm", "Decision", "Impact", "Data", "Consultations", "De-risking"]
                        },
                        "type": {
                            "type": "string",
                            "description": "Filter by question type.",
                            "enum": ["risk", "mitigation"]
                        }
                    }
                }
            },
            {
                "name": "functional_preview",
                "description": (
                    "Run a quick AIA functional risk preview from the project description alone, "
                    "without requiring answers to the full questionnaire. Useful for early-stage "
                    "planning and compliance scoping."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the project."
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "Detailed description of the AI system."
                        }
                    },
                    "required": ["projectName", "projectDescription"]
                }
            },
            {
                "name": "export_assessment_report",
                "description": "Export AIA assessment results as a Microsoft Word document (.docx) saved to the local filesystem.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Name of the project."
                        },
                        "project_description": {
                            "type": "string",
                            "description": "Project description."
                        },
                        "assessment_results": {
                            "type": "object",
                            "description": "Assessment results from functional_preview, analyze_project_description, or assess_project."
                        },
                        "custom_filename": {
                            "type": "string",
                            "description": "Optional custom filename without extension."
                        }
                    },
                    "required": ["project_name", "project_description", "assessment_results"]
                }
            },
            {
                "name": "assess_model_risk",
                "description": (
                    "Run an OSFI E-23 model risk assessment using 8 Risk Dimensions and 47 factors. "
                    "Two-phase workflow: the first call (without extracted_factors) returns an "
                    "extraction prompt; the second call (with extracted_factors) performs "
                    "deterministic scoring and returns the risk rating. "
                    "Requires projectName, projectDescription, and currentStage."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "projectName": {
                            "type": "string",
                            "description": "Name of the model being assessed."
                        },
                        "projectDescription": {
                            "type": "string",
                            "description": "Detailed description including technical architecture, data sources, business use case, and decision process."
                        },
                        "currentStage": {
                            "type": "string",
                            "description": "Current model lifecycle stage.",
                            "enum": ["design", "review", "deployment", "monitoring", "decommission"]
                        },
                        "extracted_factors": {
                            "type": "object",
                            "description": "Phase 2 only: extracted risk factor values from the first call's extraction prompt."
                        }
                    },
                    "required": ["projectName", "projectDescription", "currentStage"]
                }
            },
            {
                "name": "export_e23_report",
                "description": (
                    "Generate an OSFI E-23 compliance report as a Microsoft Word document. "
                    "Assessment data is retrieved automatically from the session — do not "
                    "pass assessment_results. Requires project_name, project_description, "
                    "and current_stage."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {
                            "type": "string",
                            "description": "Name of the model."
                        },
                        "project_description": {
                            "type": "string",
                            "description": "Description of the model and its business application."
                        },
                        "current_stage": {
                            "type": "string",
                            "description": "Current lifecycle stage.",
                            "enum": ["design", "review", "deployment", "monitoring", "decommission"]
                        },
                        "custom_filename": {
                            "type": "string",
                            "description": "Optional custom filename without extension."
                        },
                        "include_methodology_explanation": {
                            "type": "boolean",
                            "description": "Include the fixed 'How to Interpret This Assessment' educational section explaining how AI risk fits into existing ERM (default true)."
                        }
                    },
                    "required": ["project_name", "project_description"]
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
