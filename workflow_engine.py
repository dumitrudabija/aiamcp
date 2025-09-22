"""
Workflow Engine for AIA Assessment MCP Server

Manages assessment workflows, state persistence, dependency validation, and smart routing.
Provides automated tool sequencing and intelligent next-step recommendations.
"""

import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class WorkflowState(Enum):
    """Workflow execution states."""
    CREATED = "created"
    VALIDATING = "validating"
    ANALYZING = "analyzing"
    ASSESSING = "assessing"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"

class AssessmentType(Enum):
    """Types of assessments supported."""
    AIA_FULL = "aia_full"
    AIA_PREVIEW = "aia_preview"
    OSFI_E23 = "osfi_e23"
    COMBINED = "combined"

class WorkflowEngine:
    """
    Workflow engine for managing assessment sequences and state.
    """

    def __init__(self):
        """Initialize the workflow engine."""
        self.sessions = {}  # In-memory session storage
        self.session_timeout = timedelta(hours=2)  # Sessions expire after 2 hours

        # Define workflow sequences
        self.workflows = {
            AssessmentType.AIA_FULL: [
                "validate_project_description",
                "analyze_project_description",
                "get_questions",
                "assess_project",
                "export_assessment_report"
            ],
            AssessmentType.AIA_PREVIEW: [
                "validate_project_description",
                "functional_preview",
                "export_assessment_report",  # Can export after functional_preview
                "assess_project"  # Optional upgrade step
            ],
            AssessmentType.OSFI_E23: [
                "validate_project_description",
                "assess_model_risk",
                "evaluate_lifecycle_compliance",
                "generate_risk_rating",
                "create_compliance_framework",
                "export_e23_report"
            ],
            AssessmentType.COMBINED: [
                "validate_project_description",
                "functional_preview",  # AIA preview
                "assess_model_risk",   # OSFI E-23
                "assess_project",      # Full AIA if needed
                "export_assessment_report",
                "export_e23_report"
            ]
        }

        # Tool dependencies - Updated to support flexible export dependencies
        self.dependencies = {
            "assess_project": ["validate_project_description"],
            "assess_model_risk": ["validate_project_description"],
            "functional_preview": ["validate_project_description"],
            "export_assessment_report": [],  # Special handling - can export after functional_preview OR assess_project
            "export_e23_report": ["assess_model_risk"],
            "evaluate_lifecycle_compliance": ["assess_model_risk"],
            "generate_risk_rating": ["assess_model_risk"],
            "create_compliance_framework": ["assess_model_risk"]
        }

    def create_session(self, project_name: str, project_description: str,
                      assessment_type: Optional[str] = None) -> str:
        """
        Create a new workflow session.

        Args:
            project_name: Name of the project
            project_description: Project description
            assessment_type: Type of assessment (auto-detected if not provided)

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())

        # Auto-detect assessment type if not provided
        if not assessment_type:
            assessment_type = self._detect_assessment_type(project_description)

        session = {
            "session_id": session_id,
            "project_name": project_name,
            "project_description": project_description,
            "assessment_type": assessment_type,
            "state": WorkflowState.CREATED.value,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "completed_tools": [],
            "tool_results": {},
            "current_step": 0,
            "workflow_sequence": self.workflows.get(AssessmentType(assessment_type), []),
            "auto_execute": False,
            "validation_passed": False
        }

        self.sessions[session_id] = session
        logger.info(f"Created workflow session {session_id} for {project_name} ({assessment_type})")

        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID, checking for expiration."""
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        last_accessed = datetime.fromisoformat(session["last_accessed"])

        if datetime.now() - last_accessed > self.session_timeout:
            del self.sessions[session_id]
            return None

        # Update last accessed time
        session["last_accessed"] = datetime.now().isoformat()
        return session

    def execute_tool(self, session_id: str, tool_name: str, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool within a workflow session and manage state transitions.

        Args:
            session_id: Workflow session ID
            tool_name: Name of the executed tool
            tool_result: Result from tool execution

        Returns:
            Workflow management information
        """
        session = self.get_session(session_id)
        if not session:
            return {
                "workflow_error": "Session not found or expired",
                "action_required": "Create new session"
            }

        # Validate dependencies
        dependency_check = self._validate_dependencies(session, tool_name)
        if not dependency_check["valid"]:
            return {
                "workflow_error": f"Tool dependency validation failed: {dependency_check['reason']}",
                "missing_dependencies": dependency_check["missing_dependencies"],
                "recommended_action": dependency_check["recommended_action"]
            }

        # Store tool result
        session["tool_results"][tool_name] = {
            "result": tool_result,
            "executed_at": datetime.now().isoformat(),
            "success": "assessment" in tool_result or "validation" in tool_result
        }

        # Update completed tools
        if tool_name not in session["completed_tools"]:
            session["completed_tools"].append(tool_name)

        # Update workflow state
        self._update_workflow_state(session, tool_name, tool_result)

        # Get next recommended actions
        next_actions = self._get_next_actions(session)

        # Generate enhanced progress display
        progress_display = self._generate_progress_display(session)

        return {
            "workflow_status": {
                "session_id": session_id,
                "current_state": session["state"],
                "completed_tools": session["completed_tools"],
                "progress": f"{len(session['completed_tools'])}/{len(session['workflow_sequence'])}",
                "progress_percentage": round((len(session['completed_tools']) / len(session['workflow_sequence'])) * 100, 1),
                "assessment_type": session["assessment_type"]
            },
            "progress_display": progress_display,
            "next_actions": next_actions,
            "smart_routing": self._generate_smart_routing(session),
            "auto_execute_available": self._can_auto_execute(session)
        }

    def auto_execute_workflow(self, session_id: str, steps_to_execute: int = 1) -> Dict[str, Any]:
        """
        Auto-execute the next steps in the workflow.

        Args:
            session_id: Workflow session ID
            steps_to_execute: Number of steps to execute automatically

        Returns:
            Auto-execution results and next steps
        """
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found or expired"}

        if not self._can_auto_execute(session):
            return {
                "error": "Auto-execution not available",
                "reason": "Manual input required or dependencies not met"
            }

        execution_plan = []
        current_step = session["current_step"]
        workflow = session["workflow_sequence"]

        for i in range(steps_to_execute):
            if current_step + i >= len(workflow):
                break

            next_tool = workflow[current_step + i]

            # Check if tool can be auto-executed
            if self._requires_manual_input(next_tool):
                break

            execution_plan.append({
                "tool_name": next_tool,
                "step_number": current_step + i + 1,
                "can_auto_execute": True,
                "requires_data": self._get_required_data(next_tool, session)
            })

        return {
            "execution_plan": execution_plan,
            "auto_executable_steps": len(execution_plan),
            "manual_intervention_required": len(execution_plan) < steps_to_execute,
            "session_state": session["state"]
        }

    def get_workflow_summary(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow summary."""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found or expired"}

        return {
            "session_info": {
                "session_id": session_id,
                "project_name": session["project_name"],
                "assessment_type": session["assessment_type"],
                "state": session["state"],
                "created_at": session["created_at"],
                "last_accessed": session["last_accessed"]
            },
            "workflow_progress": {
                "completed_tools": session["completed_tools"],
                "total_tools": len(session["workflow_sequence"]),
                "current_step": session["current_step"],
                "progress_percentage": round((len(session["completed_tools"]) / len(session["workflow_sequence"])) * 100, 1),
                "workflow_sequence": session["workflow_sequence"]
            },
            "tool_results_summary": {
                tool_name: {
                    "executed_at": result["executed_at"],
                    "success": result["success"],
                    "has_data": bool(result["result"])
                }
                for tool_name, result in session["tool_results"].items()
            },
            "next_steps": self._get_next_actions(session),
            "smart_recommendations": self._generate_smart_routing(session)
        }

    def _detect_assessment_type(self, project_description: str) -> str:
        """Auto-detect assessment type based on project description."""
        description_lower = project_description.lower()

        # Look for OSFI E-23 indicators
        osfi_indicators = [
            'financial', 'bank', 'credit', 'loan', 'risk management',
            'model risk', 'basel', 'capital', 'regulatory', 'osfi'
        ]

        # Look for AIA indicators
        aia_indicators = [
            'government', 'federal', 'public service', 'citizen',
            'algorithmic impact', 'automated decision', 'aia'
        ]

        osfi_score = sum(1 for indicator in osfi_indicators if indicator in description_lower)
        aia_score = sum(1 for indicator in aia_indicators if indicator in description_lower)

        if osfi_score > aia_score and osfi_score >= 2:
            return AssessmentType.OSFI_E23.value
        elif aia_score >= 2:
            return AssessmentType.AIA_FULL.value
        elif osfi_score > 0 and aia_score > 0:
            return AssessmentType.COMBINED.value
        else:
            return AssessmentType.AIA_PREVIEW.value  # Default to AIA preview

    def _validate_dependencies(self, session: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
        """Validate tool dependencies with special handling for export tools."""
        required_deps = self.dependencies.get(tool_name, [])
        completed_tools = session["completed_tools"]

        # Special handling for export_assessment_report - needs either functional_preview OR assess_project
        if tool_name == "export_assessment_report":
            has_assessment = any(tool in completed_tools for tool in ["functional_preview", "assess_project"])
            if has_assessment:
                return {"valid": True}
            else:
                return {
                    "valid": False,
                    "reason": "Missing assessment results - need either functional_preview or assess_project",
                    "missing_dependencies": ["functional_preview OR assess_project"],
                    "recommended_action": "Execute functional_preview or assess_project first"
                }

        missing_deps = [dep for dep in required_deps if dep not in completed_tools]

        if not missing_deps:
            return {"valid": True}

        return {
            "valid": False,
            "reason": f"Missing required dependencies: {', '.join(missing_deps)}",
            "missing_dependencies": missing_deps,
            "recommended_action": f"Execute {missing_deps[0]} first"
        }

    def _update_workflow_state(self, session: Dict[str, Any], tool_name: str, tool_result: Dict[str, Any]):
        """Update workflow state based on tool execution."""
        # Update current step based on workflow sequence
        workflow = session["workflow_sequence"]
        if tool_name in workflow:
            tool_index = workflow.index(tool_name)
            session["current_step"] = tool_index + 1  # Next step index

        # Update workflow state
        if tool_name == "validate_project_description":
            if tool_result.get("validation", {}).get("is_valid"):
                session["validation_passed"] = True
                session["state"] = WorkflowState.VALIDATING.value
            else:
                session["state"] = WorkflowState.FAILED.value

        elif tool_name in ["analyze_project_description", "functional_preview"]:
            session["state"] = WorkflowState.ANALYZING.value

        elif tool_name in ["assess_project", "assess_model_risk"]:
            session["state"] = WorkflowState.ASSESSING.value

        elif tool_name in ["export_assessment_report", "export_e23_report"]:
            session["state"] = WorkflowState.REPORTING.value

            # Check if workflow is complete
            if len(session["completed_tools"]) >= len(session["workflow_sequence"]) - 1:
                session["state"] = WorkflowState.COMPLETED.value

    def _get_next_actions(self, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get recommended next actions."""
        completed_tools = session["completed_tools"]
        workflow = session["workflow_sequence"]

        next_actions = []

        for tool in workflow:
            if tool not in completed_tools:
                # Check dependencies
                deps_met = all(dep in completed_tools for dep in self.dependencies.get(tool, []))

                next_actions.append({
                    "tool_name": tool,
                    "priority": "high" if deps_met else "medium",
                    "dependencies_met": deps_met,
                    "required_dependencies": self.dependencies.get(tool, []),
                    "description": self._get_tool_description(tool),
                    "auto_executable": deps_met and not self._requires_manual_input(tool)
                })

                # Only show next 2-3 immediate actions
                if len(next_actions) >= 3:
                    break

        return next_actions

    def _generate_smart_routing(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Generate smart routing recommendations."""
        completed_tools = session["completed_tools"]
        state = session["state"]

        if state == WorkflowState.FAILED.value:
            return {
                "recommendation": "Fix validation issues before proceeding",
                "action": "improve_description",
                "priority": "critical"
            }

        if "validate_project_description" not in completed_tools:
            return {
                "recommendation": "Start with project description validation",
                "action": "validate_first",
                "priority": "high"
            }

        if session["assessment_type"] == AssessmentType.AIA_PREVIEW.value:
            if "functional_preview" not in completed_tools:
                return {
                    "recommendation": "Get early risk assessment with functional preview",
                    "action": "preview_first",
                    "priority": "high"
                }

        if session["assessment_type"] == AssessmentType.OSFI_E23.value:
            if "assess_model_risk" not in completed_tools:
                return {
                    "recommendation": "Conduct OSFI E-23 model risk assessment",
                    "action": "risk_assessment",
                    "priority": "high"
                }

        return {
            "recommendation": "Continue with next step in workflow",
            "action": "follow_sequence",
            "priority": "medium"
        }

    def _can_auto_execute(self, session: Dict[str, Any]) -> bool:
        """Check if auto-execution is possible."""
        # Allow auto-execution if not failed or completed
        # Validation will be handled automatically as the first step
        return session["state"] not in [WorkflowState.FAILED.value, WorkflowState.COMPLETED.value]

    def _requires_manual_input(self, tool_name: str) -> bool:
        """Check if tool requires manual input."""
        manual_input_tools = ["assess_project", "get_questions"]
        return tool_name in manual_input_tools

    def _get_required_data(self, tool_name: str, session: Dict[str, Any]) -> List[str]:
        """Get required data for tool execution."""
        data_requirements = {
            "validate_project_description": ["project_name", "project_description"],
            "analyze_project_description": ["project_name", "project_description"],
            "functional_preview": ["project_name", "project_description"],
            "assess_project": ["project_name", "project_description", "responses"],
            "assess_model_risk": ["project_name", "project_description"],
            "export_assessment_report": ["project_name", "project_description", "assessment_results"]
        }
        return data_requirements.get(tool_name, [])

    def _get_tool_description(self, tool_name: str) -> str:
        """Get comprehensive tool description for recommendations."""
        descriptions = {
            "validate_project_description": "🔍 Validate project description adequacy (REQUIRED FIRST STEP)",
            "analyze_project_description": "📋 Analyze project and auto-answer AIA questions for review",
            "functional_preview": "⚡ Get early functional risk assessment (AIA preview mode)",
            "get_questions": "❓ Retrieve framework questions for manual assessment",
            "assess_project": "🎯 Calculate official AIA risk score using actual responses",
            "assess_model_risk": "🏦 Conduct OSFI E-23 model risk assessment",
            "evaluate_lifecycle_compliance": "📊 Evaluate model lifecycle compliance (OSFI E-23)",
            "generate_risk_rating": "⚖️ Generate detailed risk rating assessment (OSFI E-23)",
            "create_compliance_framework": "📋 Create comprehensive compliance framework (OSFI E-23)",
            "export_assessment_report": "📄 Generate comprehensive AIA assessment report",
            "export_e23_report": "📄 Generate comprehensive OSFI E-23 assessment report"
        }
        return descriptions.get(tool_name, "🔧 Execute framework tool")

    def get_detailed_workflow_sequence(self, assessment_type: str) -> List[Dict[str, Any]]:
        """Get detailed workflow sequence with step numbers and descriptions."""
        workflow_sequence = self.workflows.get(AssessmentType(assessment_type), [])

        detailed_sequence = []
        for index, tool_name in enumerate(workflow_sequence):
            detailed_sequence.append({
                "step_number": index + 1,
                "total_steps": len(workflow_sequence),
                "tool_name": tool_name,
                "description": self._get_tool_description(tool_name),
                "requires_manual_input": self._requires_manual_input(tool_name),
                "auto_executable": not self._requires_manual_input(tool_name),
                "dependencies": self.dependencies.get(tool_name, []),
                "data_requirements": self._get_required_data(tool_name, {})
            })

        return detailed_sequence

    def _generate_progress_display(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhanced progress display with step-by-step status."""
        workflow_sequence = session["workflow_sequence"]
        completed_tools = session["completed_tools"]

        step_status = []
        for index, tool_name in enumerate(workflow_sequence):
            step_number = index + 1
            is_completed = tool_name in completed_tools
            is_current = (not is_completed and
                         all(prev_tool in completed_tools for prev_tool in workflow_sequence[:index]))

            status_icon = "✅" if is_completed else ("🔄" if is_current else "⏳")
            step_status.append({
                "step_number": step_number,
                "tool_name": tool_name,
                "description": self._get_tool_description(tool_name),
                "status": "completed" if is_completed else ("current" if is_current else "pending"),
                "status_icon": status_icon,
                "display": f"{status_icon} Step {step_number}: {self._get_tool_description(tool_name)}"
            })

        return {
            "workflow_title": f"📋 {session['assessment_type'].upper()} Assessment Progress",
            "total_steps": len(workflow_sequence),
            "completed_steps": len(completed_tools),
            "progress_percentage": round((len(completed_tools) / len(workflow_sequence)) * 100, 1),
            "step_details": step_status,
            "visual_progress": self._create_progress_bar(len(completed_tools), len(workflow_sequence))
        }

    def _create_progress_bar(self, completed: int, total: int, width: int = 20) -> str:
        """Create a visual progress bar."""
        filled = int((completed / total) * width)
        bar = "█" * filled + "░" * (width - filled)
        percentage = round((completed / total) * 100, 1)
        return f"[{bar}] {percentage}% ({completed}/{total})"

    def cleanup_expired_sessions(self):
        """Remove expired sessions."""
        current_time = datetime.now()
        expired_sessions = []

        for session_id, session in self.sessions.items():
            last_accessed = datetime.fromisoformat(session["last_accessed"])
            if current_time - last_accessed > self.session_timeout:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.sessions[session_id]

        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")