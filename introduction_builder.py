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
            "version": "3.2.0",
            "key_feature": {
                "title": "🧠 AI-Assisted Contextual Extraction with Deterministic Scoring",
                "description": "Step 2 uses a two-phase approach that combines AI understanding with rule-based scoring",
                "how_it_works": [
                    "📝 Phase 1: I analyze your project description and extract values for 47 risk factors across 8 dimensions",
                    "✅ You confirm: I present the extracted values for your review and confirmation",
                    "🔢 Phase 2: The MCP server scores deterministically using fixed thresholds (no AI interpretation)",
                    "📊 Result: Transparent, reproducible risk scores with clear audit trail"
                ],
                "benefits": [
                    "✅ Contextual understanding - Not crude keyword matching",
                    "✅ User verification - You confirm extracted values before scoring",
                    "✅ Deterministic scoring - Same values always produce same risk score",
                    "✅ Transparent defaults - Missing information defaults to Medium and is flagged"
                ]
            },
            "risk_dimensions": {
                "title": "📊 8 Risk Dimensions (47 Factors)",
                "dimensions": [
                    {"name": "Misuse & Unintended Harm", "factors": 5, "example": "Financial exposure, decision volume, scope expansion, confabulation risk"},
                    {"name": "Output Reliability & Integrity", "factors": 6, "example": "Error rate, consistency, explainability, GenAI output benchmark"},
                    {"name": "Fairness & Customer Impact", "factors": 7, "example": "Disparate impact, population affected, adverse action severity, pre-deployment fairness testing"},
                    {"name": "Operational & Security Risk", "factors": 7, "example": "Uptime requirements, data sensitivity, attack surface, adversarial robustness testing"},
                    {"name": "Model Complexity & Opacity", "factors": 8, "example": "Feature count, model type, autonomy level, AI system classification, automation bias"},
                    {"name": "Governance & Oversight", "factors": 7, "example": "Human review, regulatory scrutiny, model ownership, AI incident response, kill switch"},
                    {"name": "Data Provenance & Supply Chain Risk", "factors": 4, "example": "Training data documentation, PII in training/context data, third-party/OSS component integrity, synthetic data quality"},
                    {"name": "Systemic & Concentration Risk", "factors": 3, "example": "Infrastructure concentration, foundation-model/vendor concentration, portfolio-level AI estate concentration"}
                ],
                "scoring": "Each factor scored on 4-level scale: Low (1) | Medium (2) | High (3) | Critical (4)"
            },
            "implementation_notice": {
                "critical_understanding": "🔧 IMPLEMENTATION STATUS: Proof of Concept with Exemplification Logic",
                "what_this_means": [
                    "✅ OSFI E-23 REQUIREMENTS: Framework structure, principles, and lifecycle stages are official OSFI requirements",
                    "⚙️ IMPLEMENTATION CHOICES: Risk scoring weights, thresholds, and governance mappings are exemplification - NOT official OSFI specifications",
                    "🔧 TUNABLE PARAMETERS: All risk factors, weights, and thresholds can be customized",
                    "🏦 INSTITUTIONAL CUSTOMIZATION REQUIRED: Financial institutions must tune parameters to match their risk appetite"
                ],
                "professional_requirement": "⚠️ CRITICAL: All parameters, scores, and governance requirements must be validated by your institution's Model Risk Management function"
            },
            "lifecycle_stage_selection": {
                "instruction": "🔄 CRITICAL: You must explicitly state which lifecycle stage your model is in",
                "default": "Design (will be used if you do not explicitly specify a different stage)",
                "options": [
                    {"stage": "Design", "description": "Initial model development and planning phase"},
                    {"stage": "Review", "description": "Independent validation and testing phase"},
                    {"stage": "Deployment", "description": "Implementation and go-live preparation"},
                    {"stage": "Monitoring", "description": "Production operation and ongoing performance tracking"},
                    {"stage": "Decommission", "description": "Model retirement or replacement"}
                ],
                "user_prompt": "QUESTION: Which lifecycle stage is your model currently in?\n\nOptions: Design | Review | Deployment | Monitoring | Decommission"
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
                    "purpose": "Risk assessment using 8 Risk Dimensions with AI-assisted extraction",
                    "how_it_works": {
                        "phase_1": "Returns extraction prompt → I analyze description and extract 47 factor values → You confirm",
                        "phase_2": "Extracted values submitted → MCP validates and scores deterministically → Risk rating produced"
                    },
                    "output": "Risk rating (Low/Medium/High/Critical) with dimension-level breakdown and NOT_STATED tracking"
                },
                {
                    "step": 3,
                    "tool": "export_e23_report",
                    "purpose": "Generate stage-specific compliance report with risk-scaled requirements",
                    "output": "Professional Word document (~4 pages) with lifecycle requirements and checklists"
                }
            ],
            "not_stated_handling": {
                "what_happens": "When a risk factor value cannot be determined from your description",
                "default_behavior": "Factor defaults to Medium risk (score = 2)",
                "transparency": "All NOT_STATED factors are tracked and listed in the report",
                "recommendation": "The report includes suggestions to clarify missing information for more accurate assessment"
            },
            "recommended_use": "Models used by federally regulated financial institutions (banks, credit unions, insurance companies)",
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
                "version": "3.2.0",
                "key_feature": {
                    "title": "🧠 AI-Assisted Contextual Extraction with Deterministic Scoring",
                    "description": "Step 2 uses a two-phase approach combining AI understanding with rule-based scoring",
                    "how_it_works": [
                        "📝 Phase 1: Claude analyzes description and extracts 47 risk factor values",
                        "✅ User confirms extracted values before scoring",
                        "🔢 Phase 2: MCP scores deterministically using fixed thresholds",
                        "📊 Transparent, reproducible risk scores with audit trail"
                    ]
                },
                "risk_dimensions": {
                    "count": 8,
                    "total_factors": 47,
                    "dimensions": [
                        "Misuse & Unintended Harm (5 factors)",
                        "Output Reliability & Integrity (6 factors)",
                        "Fairness & Customer Impact (7 factors)",
                        "Operational & Security Risk (7 factors)",
                        "Model Complexity & Opacity (8 factors)",
                        "Governance & Oversight (7 factors)",
                        "Data Provenance & Supply Chain Risk (4 factors)",
                        "Systemic & Concentration Risk (3 factors)"
                    ],
                    "scoring": "4-level scale: Low (1) | Medium (2) | High (3) | Critical (4)"
                },
                "implementation_notice": {
                    "critical_understanding": "🔧 PROOF OF CONCEPT with exemplification logic",
                    "professional_requirement": "⚠️ All scores must be validated by your institution's Model Risk Management function"
                },
                "lifecycle_stage_selection": {
                    "instruction": "🔄 You must specify lifecycle stage",
                    "default": "Design (if not specified)",
                    "options": ["Design", "Review", "Deployment", "Monitoring", "Decommission"]
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
                        "purpose": "Risk assessment using 8 Risk Dimensions with AI-assisted extraction",
                        "how_it_works": {
                            "phase_1": "Returns extraction prompt → Claude extracts 47 factor values → User confirms",
                            "phase_2": "Extracted values submitted → MCP validates and scores deterministically"
                        },
                        "output": "Risk rating (Low/Medium/High/Critical) with dimension-level breakdown"
                    },
                    {
                        "step": 3,
                        "tool": "export_e23_report",
                        "purpose": "Generate stage-specific compliance report with risk-scaled requirements",
                        "output": "Professional Word document (~4 pages) with lifecycle requirements and checklists"
                    }
                ],
                "not_stated_handling": {
                    "behavior": "Missing factors default to Medium risk (score = 2)",
                    "transparency": "All NOT_STATED factors tracked and listed in report"
                },
                "recommended_use": "Models used by federally regulated financial institutions",
                "note": "All 3 steps provide comprehensive OSFI E-23 coverage."
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
                "behavioral_requirement": "After presenting the OSFI E-23 introduction: (1) You MAY analyze the project description and suggest a likely stage if clear indicators exist (e.g., 'deployed 18 months ago' → Monitoring, 'planning phase' → Design, 'validation testing' → Review, 'going live' → Deployment, 'being retired' → Decommission). (2) Present all 5 stage options clearly. (3) CRITICAL: Clearly state 'However, if you don't specify or say \"proceed\", we will use Design stage as the default.' (4) When user responds: If they explicitly confirm a stage (e.g., 'Monitoring', 'yes Monitoring', 'Review stage') - use that stage and continue. If they say 'proceed', 'yes', 'continue', or don't specify - IMMEDIATELY use Design stage (NOT the suggested stage) and continue. Do NOT get stuck - 'proceed' always means Design."
            }
        else:  # both
            assistant_directive = {
                "critical_instruction": "STOP AND PRESENT THIS INTRODUCTION FIRST. Present BOTH frameworks since the context is unclear. Do NOT call any other tools immediately after this. Ask the user which framework applies to their project.",
                "behavioral_requirement": "After presenting both workflows, ask which framework they want (AIA, OSFI E-23, or both). If they choose OSFI E-23 or both: (1) You MAY analyze the project description and suggest a likely lifecycle stage if clear indicators exist (e.g., 'deployed 18 months ago' → Monitoring, 'planning' → Design, 'validation' → Review, 'going live' → Deployment, 'retiring' → Decommission). (2) Present all 5 stage options. (3) CRITICAL: Clearly state 'However, if you don't specify or say \"proceed\", we will use Design stage as the default.' (4) If user explicitly confirms a stage - use that stage. If user says 'proceed' - IMMEDIATELY use Design stage (NOT suggested stage) and continue. Do NOT get stuck."
            }

        # Build base introduction (common to all)
        base_response = {
            "assistant_directive": assistant_directive,
            "server_introduction": {
                "title": "🇨🇦 Canada's Regulatory Assessment MCP Server",
                "version": "3.2.0",
                "purpose": "Proof of Concept implementation leveraging Canada's AIA and OSFI E-23 frameworks",
                "transparency_notice": {
                    "critical_distinction": "⚠️ PROOF OF CONCEPT: This server uses official framework structures but implements exemplification logic that requires institutional customization.",
                    "what_is_official": [
                        "✅ AIA OFFICIAL: 104 questions from Canada.ca Treasury Board Directive",
                        "✅ OSFI E-23 OFFICIAL: Principles (1.1-3.6), lifecycle stages, Appendix 1 structure",
                        "✅ FRAMEWORK STRUCTURE: Official regulatory requirements and terminology"
                    ],
                    "what_is_proof_of_concept": [
                        "⚙️ IMPLEMENTATION CHOICE: Risk scoring weights, thresholds, and formulas (NOT official)",
                        "⚙️ IMPLEMENTATION CHOICE: Governance mappings and approval authorities (exemplification only)",
                        "⚙️ IMPLEMENTATION CHOICE: Amplification factors and risk calculations (tunable parameters)",
                        "⚙️ IMPLEMENTATION CHOICE: Specific requirements mapped to lifecycle stages (interpretation)"
                    ],
                    "data_sources": [
                        "🔧 MCP SERVER: Official framework questions and structures from government sources",
                        "⚙️ MCP SERVER: Proof of concept risk scoring and governance logic (requires customization)",
                        "🧠 CLAUDE (AI): Result interpretations, gap analysis, and recommendations"
                    ],
                    "critical_requirement": "⚠️ ALL IMPLEMENTATION LOGIC must be validated and customized by your institution's Model Risk Management and compliance teams. This is NOT production-ready without institutional adaptation."
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
                    "description": "🏦 OSFI Guideline E-23 Model Risk Management (3-step workflow)",
                    "tools": ["assess_model_risk", "export_e23_report"],
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
                "proof_of_concept": "⚠️ CRITICAL: This is a PROOF OF CONCEPT implementation. All scoring logic, risk calculations, and governance mappings are exemplification - NOT official government specifications",
                "professional_validation": "⚠️ ALL RESULTS require validation by qualified professionals and approval by appropriate governance authorities before any regulatory use",
                "customization_required": "⚠️ Financial institutions MUST customize risk weights, thresholds, governance structures, and approval authorities to match their institutional framework",
                "regulatory_compliance": "⚠️ This tool provides FRAMEWORK STRUCTURE from official sources - but implementation logic requires institutional adaptation and professional validation",
                "audit_requirements": "⚠️ Results must be validated, customized, and approved by your institution's Model Risk Management and compliance teams before regulatory use"
            },
            "usage_examples": {
                "proper_usage": [
                    "✅ Use workflows for complete guided assessments",
                    "✅ Validate project descriptions before framework tools",
                    "✅ Follow the complete framework workflow sequences",
                    "✅ Customize risk parameters to match your institutional framework",
                    "✅ Export generated documents as templates for institutional adaptation"
                ],
                "improper_usage": [
                    "❌ Do NOT skip workflow steps or call tools out of sequence",
                    "❌ Do NOT use AI interpretations for regulatory decisions",
                    "❌ Do NOT bypass description validation requirements",
                    "❌ Do NOT use proof-of-concept scoring without institutional customization",
                    "❌ Do NOT treat exemplification logic as production-ready specifications"
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


