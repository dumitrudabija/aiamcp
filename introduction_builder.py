"""
Introduction Builder Module

Handles construction of server introduction responses with workflow guidance.
Extracted from server.py to reduce complexity and improve code organization.

This module provides smart framework-specific introductions that guide users
through AIA and OSFI E-23 assessment workflows.
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class IntroductionBuilder:
    """
    Builds framework-specific server introduction responses.
    
    Constructs introduction messages with complete workflow guidance for:
    - AIA (Algorithmic Impact Assessment) workflows
    - OSFI E-23 (Model Risk Management) workflows
    - Combined workflows when both frameworks apply
    """

    def __init__(self, framework_detector):
        """
        Initialize introduction builder.
        
        Args:
            framework_detector: FrameworkDetector instance for context detection
        """
        self.framework_detector = framework_detector

    def _build_aia_workflow_section(self) -> Dict[str, Any]:
        """Build AIA-focused workflow information."""
        return {
            "title": "🇨🇦 AIA Framework Assessment",
            "description": "Canada's Algorithmic Impact Assessment for automated decision-making systems",
            "framework": "aia",
            "sequence": [
                {
                    "step": 1,
                    "tool": "validate_project_description",
                    "purpose": "Ensure project description has sufficient detail for assessment",
                    "output": "Validation report with coverage analysis"
                },
                {
                    "step": 2,
                    "tool": "functional_preview OR analyze_project_description",
                    "purpose": "Get preliminary risk assessment or auto-answer questions",
                    "output": "Initial risk level and question analysis"
                },
                {
                    "step": 3,
                    "tool": "get_questions",
                    "purpose": "Review all 104 official AIA questions if needed",
                    "output": "Complete question set with categories"
                },
                {
                    "step": 4,
                    "tool": "assess_project",
                    "purpose": "Complete full AIA assessment with all responses",
                    "output": "Official AIA score and impact level (1-4)"
                },
                {
                    "step": 5,
                    "tool": "export_assessment_report",
                    "purpose": "Generate professional Word document for compliance",
                    "output": "Complete AIA report (.docx file)"
                }
            ],
            "recommended_use": "Federal government automated decision-making systems",
            "note": "💡 If your system is also subject to financial regulation (e.g., used by a bank), you may need OSFI E-23 framework too. Just ask!"
        }


    def _build_osfi_workflow_section(self) -> Dict[str, Any]:
        """Build OSFI E-23-focused workflow information."""
        return {
            "title": "🏦 OSFI E-23 Model Risk Management",
            "description": "OSFI Guideline E-23 for federally regulated financial institutions",
            "framework": "osfi_e23",
            "lifecycle_stage_selection": {
                "instruction": "🔄 CRITICAL: You must explicitly state which lifecycle stage your model is in",
                "default": "Design (will be used if you do not explicitly specify a different stage)",
                "important_note": "⚠️ The system will NOT attempt to detect or interpret the stage from your project description. You must explicitly state the stage.",
                "options": [
                    {"stage": "Design", "description": "Initial model development and planning phase"},
                    {"stage": "Review", "description": "Independent validation and testing phase"},
                    {"stage": "Deployment", "description": "Implementation and go-live preparation"},
                    {"stage": "Monitoring", "description": "Production operation and ongoing performance tracking"},
                    {"stage": "Decommission", "description": "Model retirement or replacement"}
                ],
                "user_prompt": "QUESTION: Which lifecycle stage is your model currently in?\n\nOptions: Design | Review | Deployment | Monitoring | Decommission\n\n⚠️ DEFAULT: If you say 'proceed' or don't specify a stage, we will use Design stage.\n\nTo specify a different stage, reply with the stage name:\n- 'Monitoring'\n- 'My model is in the Review stage'\n- 'Deployment stage'\n\nTo use Design stage (default), simply say:\n- 'proceed'\n- 'Design'\n- 'continue'",
                "note": "The stage you explicitly specify will be used consistently across all assessment steps (Steps 3, 4, and 5)."
            },
            "sequence": [
                {
                    "step": 1,
                    "tool": "validate_project_description",
                    "purpose": "Ensure model description has sufficient detail for risk assessment",
                    "output": "Validation report confirming OSFI E-23 readiness"
                },
                {
                    "step": 2,
                    "tool": "assess_model_risk",
                    "purpose": "Comprehensive model risk assessment using quantitative and qualitative factors",
                    "output": "Risk rating (Low/Medium/High/Critical) with detailed factor analysis"
                },
                {
                    "step": 3,
                    "tool": "evaluate_lifecycle_compliance",
                    "purpose": "Assess coverage of OSFI E-23 lifecycle elements (checks for 3 subcomponents per stage)",
                    "output": "Coverage percentage (0/33/67/100%) and indication of which OSFI elements are detected"
                },
                {
                    "step": 4,
                    "tool": "create_compliance_framework",
                    "purpose": "Build complete governance and compliance framework",
                    "output": "Full E-23 compliance structure with policies and controls"
                },
                {
                    "step": 5,
                    "tool": "export_e23_report",
                    "purpose": "Generate executive-ready stage-specific report",
                    "output": "Professional Word document (4-6 pages) with stage-specific content"
                }
            ],
            "recommended_use": "Models used by federally regulated financial institutions (banks, credit unions, insurance companies)",
            "minimum_viable": "Steps 1, 2, and 5 provide basic compliance; all 5 steps provide comprehensive coverage",
            "note": "💡 If your model makes automated decisions affecting citizens, you may need AIA framework too. Just ask!"
        }


    def _build_both_workflows_section(self) -> Dict[str, Any]:
        """Build combined workflow information (both AIA and OSFI E-23)."""
        return {
            "aia_workflow": {
                "title": "🇨🇦 AIA Framework Complete Workflow",
                "description": "Canada's Algorithmic Impact Assessment for automated decision-making systems",
                "sequence": [
                    {
                        "step": 1,
                        "tool": "validate_project_description",
                        "purpose": "Ensure project description has sufficient detail for assessment",
                        "output": "Validation report with coverage analysis"
                    },
                    {
                        "step": 2,
                        "tool": "functional_preview OR analyze_project_description",
                        "purpose": "Get preliminary risk assessment or auto-answer questions",
                        "output": "Initial risk level and question analysis"
                    },
                    {
                        "step": 3,
                        "tool": "get_questions",
                        "purpose": "Review all 104 official AIA questions if needed",
                        "output": "Complete question set with categories"
                    },
                    {
                        "step": 4,
                        "tool": "assess_project",
                        "purpose": "Complete full AIA assessment with all responses",
                        "output": "Official AIA score and impact level (1-4)"
                    },
                    {
                        "step": 5,
                        "tool": "export_assessment_report",
                        "purpose": "Generate professional Word document for compliance",
                        "output": "Complete AIA report (.docx file)"
                    }
                ],
                "recommended_use": "Federal government automated decision-making systems"
            },
            "osfi_e23_workflow": {
                "title": "🏦 OSFI E-23 Framework Complete Workflow",
                "description": "OSFI Guideline E-23 Model Risk Management for federally regulated financial institutions",
                "lifecycle_stage_selection": {
                    "instruction": "🔄 CRITICAL: You must explicitly state which lifecycle stage your model is in",
                    "default": "Design (will be used if you do not explicitly specify a different stage)",
                    "important_note": "⚠️ The system will NOT attempt to detect or interpret the stage from your project description. You must explicitly state the stage.",
                    "options": [
                        {"stage": "Design", "description": "Initial model development and planning phase"},
                        {"stage": "Review", "description": "Independent validation and testing phase"},
                        {"stage": "Deployment", "description": "Implementation and go-live preparation"},
                        {"stage": "Monitoring", "description": "Production operation and ongoing performance tracking"},
                        {"stage": "Decommission", "description": "Model retirement or replacement"}
                    ],
                    "user_prompt": "QUESTION: Which lifecycle stage is your model currently in?\n\nOptions: Design | Review | Deployment | Monitoring | Decommission\n\n⚠️ DEFAULT: If you say 'proceed' or don't specify a stage, we will use Design stage.\n\nTo specify a different stage, reply with the stage name:\n- 'Monitoring'\n- 'My model is in the Review stage'\n- 'Deployment stage'\n\nTo use Design stage (default), simply say:\n- 'proceed'\n- 'Design'\n- 'continue'",
                    "note": "The stage you explicitly specify will be used consistently across all assessment steps (Steps 3, 4, and 5)."
                },
                "sequence": [
                    {
                        "step": 1,
                        "tool": "validate_project_description",
                        "purpose": "Ensure model description has sufficient detail for risk assessment",
                        "output": "Validation report confirming OSFI E-23 readiness"
                    },
                    {
                        "step": 2,
                        "tool": "assess_model_risk",
                        "purpose": "Comprehensive model risk assessment using quantitative and qualitative factors",
                        "output": "Risk rating (Low/Medium/High/Critical) with detailed factor analysis"
                    },
                    {
                        "step": 3,
                        "tool": "evaluate_lifecycle_compliance",
                        "purpose": "Assess coverage of OSFI E-23 lifecycle elements (checks for 3 subcomponents per stage)",
                        "output": "Coverage percentage (0/33/67/100%) and indication of which OSFI elements are detected"
                    },
                    {
                        "step": 4,
                        "tool": "create_compliance_framework",
                        "purpose": "Build complete governance and compliance framework",
                        "output": "Full E-23 compliance structure with policies and controls"
                    },
                    {
                        "step": 5,
                        "tool": "export_e23_report",
                        "purpose": "Generate executive-ready stage-specific report",
                        "output": "Professional Word document (4-6 pages) with stage-specific content"
                    }
                ],
                "recommended_use": "Models used by federally regulated financial institutions (banks, credit unions, insurance companies)",
                "note": "All 5 steps provide comprehensive OSFI E-23 coverage. Minimum viable assessment: steps 1-2 and 5."
            },
            "combined_workflow": {
                "title": "🇨🇦🏦 Combined AIA + OSFI E-23 Workflow",
                "description": "For AI systems in financial institutions requiring both frameworks",
                "use_case": "Automated decision-making systems in federally regulated financial institutions",
                "approach": "Run both complete workflows sequentially, starting with project description validation"
            }
        }

    def _detect_framework_context(self, user_context: str = "", session_id: str = None) -> str:
        """
        Detect which framework to emphasize based on user context.

        Delegates to FrameworkDetector for the actual detection logic.

        Args:
            user_context: User's statement or project context
            session_id: Optional session ID to check for existing workflow type

        Returns:
            'aia' | 'osfi_e23' | 'both'
        """
        return self.framework_detector.detect(user_context, session_id)

    def _get_server_introduction(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide framework-specific or combined introduction based on user context.

        Uses smart detection to show only the relevant framework, reducing cognitive load.

        Note: The server (MCPServer class) tracks introduction_shown flag for workflow enforcement.
        """

        logger.info("Building server introduction with workflow guidance")

        # Detect which framework to emphasize
        user_context = arguments.get('user_context', '')
        session_id = arguments.get('session_id')
        framework_focus = self._detect_framework_context(user_context, session_id)

        # Build framework-specific assistant directive
        if framework_focus == 'aia':
            assistant_directive = {
                "critical_instruction": "STOP AND PRESENT THIS INTRODUCTION FIRST. Present the AIA workflow to the user. Do NOT call any other tools immediately after this. Mention that OSFI E-23 is also available if they ask, but focus on AIA since that's what was detected from context.",
                "behavioral_requirement": "After presenting the AIA introduction, you MUST ask the user if they want to proceed with this AIA workflow and WAIT for their explicit confirmation (e.g., 'yes', 'proceed', 'run AIA') before calling Step 1 (validate_project_description)."
            }
        elif framework_focus == 'osfi_e23':
            assistant_directive = {
                "critical_instruction": "STOP AND PRESENT THIS INTRODUCTION FIRST. Present the OSFI E-23 workflow to the user. Do NOT call any other tools immediately after this. Mention that AIA is also available if they ask, but focus on OSFI E-23 since that's what was detected from context.",
                "behavioral_requirement": "After presenting the OSFI E-23 introduction, ask: 'Which lifecycle stage is your model in? (Design/Review/Deployment/Monitoring/Decommission)' - Do NOT analyze the project description, do NOT suggest a stage, do NOT say 'it looks like Monitoring' - simply present the 5 options and clearly state 'If you don't specify, we will use Design stage as the default.' When the user responds: (1) If they specify a stage (e.g., 'Monitoring', 'Review stage') - use that stage, (2) If they say 'proceed', 'yes', 'continue', or don't specify a stage - IMMEDIATELY use Design stage and proceed to ask if they want to start the workflow. Do NOT get stuck waiting - 'proceed' without a stage = Design."
            }
        else:  # both
            assistant_directive = {
                "critical_instruction": "STOP AND PRESENT THIS INTRODUCTION FIRST. Present BOTH frameworks since the context is unclear. Do NOT call any other tools immediately after this. Ask the user which framework applies to their project.",
                "behavioral_requirement": "After presenting both workflows, ask which framework they want (AIA, OSFI E-23, or both). If they choose OSFI E-23 or both, ask: 'Which lifecycle stage is your model in? (Design/Review/Deployment/Monitoring/Decommission)' - Do NOT analyze the project description, do NOT suggest a stage - simply present the 5 options and clearly state 'If you don't specify, we will use Design stage as the default.' If user says 'proceed' without specifying stage, IMMEDIATELY use Design and continue. Do NOT get stuck."
            }

        # Build base introduction (common to all)
        base_response = {
            "assistant_directive": assistant_directive,
            "server_introduction": {
                "title": "🇨🇦 Canada's Regulatory Assessment MCP Server",
                "version": "2.2.0",
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
                    "tools": ["assess_model_risk", "evaluate_lifecycle_compliance", "create_compliance_framework", "export_e23_report"],
                    "official_source": "Office of the Superintendent of Financial Institutions Canada"
                }
            }
        }

        # Add framework-specific workflow based on detection
        if framework_focus == 'aia':
            base_response["framework_workflow"] = self._build_aia_workflow_section()
        elif framework_focus == 'osfi_e23':
            base_response["framework_workflow"] = self._build_osfi_workflow_section()
        else:  # both
            base_response["framework_workflows"] = self._build_both_workflows_section()

        # Add common sections
        base_response.update({
            "workflow_guidance": {
                "recommended_approach": [
                    "1. 🔄 Use 'create_workflow' to start guided assessment",
                    "2. ⚡ Use 'auto_execute_workflow' for automated progression",
                    "3. 📊 Use 'get_workflow_status' for progress tracking",
                    "4. 🎯 Use 'execute_workflow_step' for manual control when needed"
                ],
                "manual_approach": [
                    "1. 🔍 Review the framework workflows above",
                    "2. ✅ Choose AIA, OSFI E-23, or Combined workflow",
                    "3. 📝 Follow the sequence step-by-step",
                    "4. 📄 Export final reports for compliance documentation"
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
                    "✅ Follow the complete framework workflow sequences",
                    "✅ Use official scores for regulatory compliance",
                    "✅ Export generated documents for audit trails"
                ],
                "improper_usage": [
                    "❌ Do NOT skip workflow steps or call tools out of sequence",
                    "❌ Do NOT use AI interpretations for regulatory decisions",
                    "❌ Do NOT bypass description validation requirements",
                    "❌ Do NOT use framework tools without proper project information",
                    "❌ Do NOT modify or substitute official scoring calculations"
                ]
            },
            "next_steps_guidance": {
                "user_choice_required": "ASK THE USER: Which framework do you want to use?",
                "options": {
                    "option_1": "🇨🇦 AIA Framework - For federal government automated decision systems",
                    "option_2": "🏦 OSFI E-23 Framework - For financial institution models",
                    "option_3": "🔄 Workflow Mode - For guided assessment with automatic progression",
                    "option_4": "🇨🇦🏦 Both Frameworks - For AI systems in regulated financial institutions"
                },
                "after_user_choice": "Once user selects a framework, follow the appropriate workflow sequence shown above"
            }
        })

        return base_response


