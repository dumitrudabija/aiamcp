"""
Model Type & Delivery Model Classification (deterministic capability gates)

Adds a second, orthogonal, NON-scored layer on top of the existing 47-factor
OSFI E-23 risk engine: a model capability classification (Level 1-5) and a
delivery-model label (internal_build / vendor_platform / embedded_saas_ai).

Core rule: model type classification is based on OBJECTIVE, VERIFIABLE
capability gates, not on marketing labels ("agent", "copilot", "assistant",
"chatbot", "autonomous", "Agentforce", "ServiceNow" are candidate signals
only). Claude extracts factual evidence answers to a fixed checklist; this
module's deterministic Python logic - not Claude - decides each gate's
`verified` status and the final level.

Critical distinction enforced throughout this module:
    Automated execution (a predefined workflow/batch job/rule/schedule/
    trigger executes a predetermined action) is NOT the same as autonomous
    agentic decision-making (the AI decides WHETHER to act, WHAT action to
    take, and/or WHAT SEQUENCE of actions to pursue toward a goal). A system
    is never promoted to Level 5 solely because it runs on a schedule, is
    event-triggered, processes records in batch, auto-approves a predefined
    decision, applies a threshold rule, executes a fixed workflow, has no
    human review per transaction, or changes a system of record via
    predefined logic - those are Action Execution Pack / governance
    territory, not proof of autonomous agentic decision-making.

Promotion logic (sequential, highest verified level wins):
    Level 1 (default) -> Level 2 if genai_generation verified
                       -> Level 3 if runtime_retrieval verified
                       -> Level 4 if tool_or_action_execution verified
                       -> Level 5 only if tool_or_action_execution is
                          verified AND the AI has verified discretion over
                          whether to act/continue AND at least one agentic
                          autonomy capability is verified (see
                          autonomous_operation gate below).

This module has zero dependency on osfi_e23_risk_dimensions.py or the
scoring functions in risk_dimension_extraction.py - it cannot influence
dimension_scores/overall_assessment, by construction.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# =============================================================================
# MODEL TYPE LEVELS & DELIVERY MODEL LABELS
# =============================================================================

MODEL_TYPE_LABELS = {
    1: "Traditional ML / statistical model",
    2: "GenAI assistant / copilot",
    3: "RAG / knowledge-grounded assistant",
    4: "Agentic workflow / AI-mediated action execution",
    5: "Autonomous agent",
}

CLASSIFICATION_METHOD = "deterministic_capability_gates"

DELIVERY_MODEL_LABELS = {
    "internal_build": "Internal build",
    "vendor_platform": "Vendor platform",
    "embedded_saas_ai": "Embedded SaaS AI",
    "unknown": "Unknown",
}

# Vendor product names that indicate an AI feature embedded inside an
# existing SaaS product the institution already uses, rather than a
# standalone AI platform/product. Matched case-insensitively against
# Claude's own structured short-answer field, not the original prose.
_EMBEDDED_SAAS_KEYWORDS = ["copilot", "embedded", "add-on", "addon", "plugin", "extension"]

# Marketing/product labels that are candidate signals ONLY - never used to
# gate/verify anything in this module. Listed here purely for prompt text.
_CANDIDATE_LABEL_EXAMPLES = [
    "agent", "copilot", "assistant", "autonomous", "workflow",
    "AI agent", "Agentforce", "ServiceNow",
]

YES = "yes"
NO = "no"
NOT_STATED = "not_stated"


# =============================================================================
# EVIDENCE CHECKLIST SCHEMA
# =============================================================================
# Every field is a FACTUAL question - never "what level/type is this system."
# Marketing/product labels (product_label_mentioned) are captured separately
# and never feed gate verification directly.

MODEL_TYPE_EVIDENCE_CHECKLIST: List[Dict[str, Any]] = [
    {
        "id": "uses_traditional_ml_or_statistical_model",
        "type": "yes_no",
        "question": "Does the system process structured/defined inputs and produce scores, predictions, classifications, recommendations, calculations, rankings, limits, or decisions using statistical, mathematical, judgmental, rules-based, or traditional ML methods (e.g. regression, gradient boosting, a rules engine)?",
    },
    {
        "id": "uses_llm_or_generative_ai",
        "type": "yes_no",
        "question": "Does the system use an LLM, foundation model, or generative AI service to generate, summarize, draft, translate, classify, explain, answer, or recommend using natural language, code, images, audio, or other generative output?",
    },
    {
        "id": "uses_runtime_retrieval_for_genai_grounding",
        "type": "yes_no",
        "question": "At runtime, does the system retrieve enterprise or external knowledge (e.g. SharePoint, Confluence, CRM, email, policy documents, PDFs, websites, databases, knowledge bases, vector stores/embeddings, semantic search) and use that retrieved content to generate, ground, cite, or contextualize a GenAI output?",
    },
    {
        "id": "retrieves_data_for_features_or_batch_processing",
        "type": "yes_no",
        "question": "Does the system retrieve/query data only as model features, database lookups, or batch ETL - i.e. NOT used at runtime by a generative AI component to ground generated output?",
    },
    {
        "id": "model_output_changes_system_state",
        "type": "yes_no",
        "question": "Does the model's output directly cause a system-of-record change (e.g. updates a record, changes a limit, approves/denies an item, submits a transaction) without the AI itself choosing among multiple possible actions?",
    },
    {
        "id": "ai_selects_tool_or_action",
        "type": "yes_no",
        "question": "Does the AI itself select, choose, or decide WHICH tool, API, function, or action to invoke from among options (as opposed to always causing the same predefined action)?",
    },
    {
        "id": "predefined_workflow_triggered_by_model_output",
        "type": "yes_no",
        "question": "Does the model's output (e.g. crossing a threshold, a classification result) cause a predefined downstream workflow/action to run - a fixed, predetermined action rather than one the AI selects among alternatives?",
    },
    {
        "id": "runs_on_schedule_or_event_trigger",
        "type": "yes_no",
        "question": "Does the system run on a schedule, batch job, or event trigger (i.e. without a human initiating each run)?",
    },
    {
        "id": "requires_human_approval_per_action",
        "type": "yes_no",
        "question": "Does a human need to review or approve each individual action/transaction before or as it happens?",
    },
    {
        "id": "ai_decides_to_act_or_continue",
        "type": "yes_no",
        "question": "Does the AI itself decide WHETHER to act or continue (as opposed to always acting because a schedule, trigger, or threshold rule fired) - i.e. does it have discretion over whether to proceed, not just what predefined step runs next?",
    },
    {
        "id": "ai_selects_next_step",
        "type": "yes_no",
        "question": "Does the AI decide what the NEXT step/action should be based on intermediate results (as opposed to following a fixed, predetermined sequence)?",
    },
    {
        "id": "has_dynamic_multi_step_planning",
        "type": "yes_no",
        "question": "Does the system dynamically plan or sequence multiple steps/subtasks itself to reach a goal (as opposed to one prompt -> one response, or a fixed predefined sequence)?",
    },
    {
        "id": "has_goal_pursuit",
        "type": "yes_no",
        "question": "Does the system pursue a goal or objective over multiple actions, rather than performing a single discrete task?",
    },
    {
        "id": "has_looping_or_retry_based_on_outcomes",
        "type": "yes_no",
        "question": "Does the system loop, retry, or re-attempt based on the OUTCOME of a prior action/step, without a human deciding whether to retry?",
    },
    {
        "id": "has_memory_or_state_driven_continuation",
        "type": "yes_no",
        "question": "Does the system maintain memory/state across steps that influences whether/how it continues (as opposed to being stateless per invocation)?",
    },
    {
        "id": "has_delegation_to_other_agents",
        "type": "yes_no",
        "question": "Does the system delegate subtasks to other AI agents, models, or automated sub-processes?",
    },
    {
        "id": "has_adaptive_plan_revision",
        "type": "yes_no",
        "question": "Does the system revise its plan or approach based on observed results (as opposed to executing a fixed plan regardless of intermediate outcomes)?",
    },
    {
        "id": "vendor_product_named",
        "type": "text",
        "question": "If a specific named vendor product/platform is used (e.g., Salesforce Agentforce, ServiceNow, Microsoft Copilot, GitHub Copilot), what is it? (use null/empty if none)",
    },
    {
        "id": "foundation_model_hosting",
        "type": "enum",
        "options": ["internal_hosted", "vendor_hosted"],
        "question": "Is the underlying foundation/base model hosted and controlled internally, or is it vendor-hosted/managed?",
    },
    {
        "id": "product_label_mentioned",
        "type": "text",
        "question": (
            "Does the description describe the system using a marketing/product label such as "
            + ", ".join(f'"{label}"' for label in _CANDIDATE_LABEL_EXAMPLES)
            + "? If so, quote the label used. These labels are candidate signals only and never "
            "determine classification by themselves."
        ),
    },
    {
        "id": "evidence_notes",
        "type": "text",
        "question": "Brief (1-2 sentence) justification/quote from the project description supporting the above answers.",
    },
    # Supplementary evidence fields below: these do NOT affect the 4
    # promotion gates or the final level - they only feed Capability
    # Evidence Pack evidence-gap/blocker/condition logic (conditional_modules.py).
    {
        "id": "has_action_audit_logging",
        "type": "yes_no",
        "question": "If the system can take actions (calling APIs, writing records, executing transactions), is there audit logging of each action taken?",
    },
    {
        "id": "has_kill_switch_or_stop_condition",
        "type": "yes_no",
        "question": "If the system operates autonomously, is there a tested ability to halt, pause, or stop it (kill switch / circuit breaker / stop condition)?",
    },
    {
        "id": "has_retrieval_access_controls",
        "type": "yes_no",
        "question": "If the system retrieves from knowledge sources at runtime, are those sources access-controlled/entitled appropriately for this use case?",
    },
    {
        "id": "has_vendor_assurance_evidence",
        "type": "yes_no",
        "question": "If the system uses a vendor-hosted or vendor-platform AI capability, is there vendor assurance evidence (e.g. contractual audit rights, incident notification terms, compliance report)?",
    },
    # Additional Action Execution Pack trigger signals (OR'd into
    # tool_or_action_execution alongside model_output_changes_system_state /
    # ai_selects_tool_or_action / predefined_workflow_triggered_by_model_output).
    {
        "id": "system_of_record_write_permission",
        "type": "yes_no",
        "question": "Does the system/service account have write permission to a system of record (e.g. can create, update, or delete records)?",
    },
    {
        "id": "model_output_initiates_external_communication",
        "type": "yes_no",
        "question": "Can the model's output initiate an external communication (e.g. sending an email, SMS, or message to a customer or third party)?",
    },
    {
        "id": "model_output_triggers_transaction_or_approval",
        "type": "yes_no",
        "question": "Can the model's output trigger a financial transaction or an approval/denial decision?",
    },
    # Additional Vendor / Platform Pack trigger signals (OR'd alongside
    # delivery_model.label in the pack's own trigger check - conditional_modules.py).
    {
        "id": "vendor_controls_model_runtime",
        "type": "yes_no",
        "question": "Does a vendor control the runtime environment the model/AI capability executes in (as opposed to the institution controlling deployment/runtime)?",
    },
    {
        "id": "vendor_controls_model_updates",
        "type": "yes_no",
        "question": "Does a vendor control when/how the underlying model, prompts, or platform are updated (as opposed to the institution controlling change timing)?",
    },
    {
        "id": "vendor_hosts_customer_or_sensitive_data",
        "type": "yes_no",
        "question": "Does a vendor host customer, employee, confidential, or otherwise sensitive data used by this system?",
    },
    {
        "id": "vendor_provides_foundation_model_or_agent_platform",
        "type": "yes_no",
        "question": "Does a vendor provide the underlying foundation model or agent/orchestration platform this system runs on?",
    },
]

_YES_NO_FIELDS = [f["id"] for f in MODEL_TYPE_EVIDENCE_CHECKLIST if f["type"] == "yes_no"]
_TEXT_FIELDS = [f["id"] for f in MODEL_TYPE_EVIDENCE_CHECKLIST if f["type"] == "text"]
_ENUM_FIELDS = {f["id"]: f["options"] for f in MODEL_TYPE_EVIDENCE_CHECKLIST if f["type"] == "enum"}


# =============================================================================
# PHASE 1: PROMPT FRAGMENT GENERATION
# =============================================================================

def generate_model_type_evidence_prompt() -> str:
    """
    Build the evidence-checklist prompt fragment appended to the existing
    47-factor Phase-1 extraction prompt (single combined JSON response, no
    extra round trip - see server.py's _generate_extraction_phase).
    """
    lines = [
        "## Part 2: Model Type & Delivery Model Evidence",
        "",
        "In addition to the risk factors above, answer the following FACTUAL "
        "questions about the system based on the project description. Do NOT "
        "classify the model yourself (no 'level' or 'verified' judgment) - "
        "just answer each question factually, citing concrete evidence. "
        "Marketing/product labels (\"agent\", \"copilot\", \"assistant\", "
        "\"autonomous\", \"workflow\", \"Agentforce\", \"ServiceNow\") are NOT "
        "sufficient evidence on their own - only report yes/no answers based "
        "on verifiable capability descriptions. Running on a schedule or "
        "event trigger, processing records in batch, auto-approving a "
        "predefined decision, or having no human review per transaction do "
        "NOT by themselves indicate the AI decides whether/what/how to act - "
        "answer ai_decides_to_act_or_continue based only on evidence that the "
        "AI itself has discretion, not evidence of automation alone. If the "
        "description does not say, answer \"not_stated\".",
        "",
    ]
    for field in MODEL_TYPE_EVIDENCE_CHECKLIST:
        if field["type"] == "yes_no":
            lines.append(f"- {field['id']}: {field['question']} (yes/no/not_stated)")
        elif field["type"] == "enum":
            options = "/".join(field["options"] + ["not_stated"])
            lines.append(f"- {field['id']}: {field['question']} ({options})")
        else:
            lines.append(f"- {field['id']}: {field['question']} (short text, or null)")

    lines.append("")
    lines.append(
        "Return these as a \"model_type_evidence\" object, a sibling key to "
        "\"dimensions\" in the same JSON response:"
    )
    lines.append("")
    lines.append(_json_template_text())
    return "\n".join(lines)


def _json_template_text() -> str:
    body = ",\n".join(f'    "{field["id"]}": "..."' for field in MODEL_TYPE_EVIDENCE_CHECKLIST)
    return "{\n  \"model_type_evidence\": {\n" + body + "\n  }\n}"


# =============================================================================
# PHASE 2: EVIDENCE VALIDATION (defensive - never raises)
# =============================================================================

def validate_model_type_evidence(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Normalize Claude's model_type_evidence response. Missing/malformed input
    degrades safely to all-not_stated fields rather than raising - a legacy
    or malformed extraction must not crash the assessment.
    """
    raw = raw or {}
    evidence: Dict[str, Any] = {}

    for field_id in _YES_NO_FIELDS:
        value = raw.get(field_id)
        if isinstance(value, str) and value.strip().lower() in (YES, NO):
            evidence[field_id] = value.strip().lower()
        else:
            evidence[field_id] = NOT_STATED

    for field_id, options in _ENUM_FIELDS.items():
        value = raw.get(field_id)
        if isinstance(value, str) and value.strip().lower() in options:
            evidence[field_id] = value.strip().lower()
        else:
            evidence[field_id] = NOT_STATED

    for field_id in _TEXT_FIELDS:
        value = raw.get(field_id)
        if isinstance(value, str) and value.strip() and value.strip().lower() not in ("null", "none", "n/a"):
            evidence[field_id] = value.strip()
        else:
            evidence[field_id] = None

    return evidence


def _is_yes(evidence: Dict[str, Any], field_id: str) -> bool:
    return evidence.get(field_id) == YES


def _is_no(evidence: Dict[str, Any], field_id: str) -> bool:
    return evidence.get(field_id) == NO


def _is_explicit(evidence: Dict[str, Any], field_id: str) -> bool:
    return evidence.get(field_id) in (YES, NO)


def _has_named_detail(evidence: Dict[str, Any]) -> bool:
    """Whether there's a concrete, specific detail (not just a label) backing the evidence."""
    notes = evidence.get("evidence_notes")
    return bool(evidence.get("vendor_product_named")) or (bool(notes) and len(notes) > 20)


def _gate_confidence(evidence: Dict[str, Any], driving_fields: List[str], verified: Optional[bool] = None) -> str:
    """
    Gates are OR-based (any one signal can verify them), so confidence must
    be judged against whichever evidence actually decided the outcome, not
    against every possible signal field:

    - If the gate verified True: confidence is based on whether the positive
      signal(s) found have a concrete, named detail behind them (high) or
      are explicit but generic (medium). Unrelated not_stated fields don't
      matter - we already have positive proof.
    - If the gate verified False (or `verified` not given, e.g. for the
      Level-1 default): confidence requires ALL driving fields to be
      explicitly "no" to count as a confident absence (medium/high);
      otherwise (any not_stated) it's genuinely unknown, not confirmed
      absent, so confidence is low - this also naturally covers the
      "product label only" case, where nothing was explicitly answered.
    """
    if verified:
        return "high" if _has_named_detail(evidence) else "medium"

    all_explicit_no = all(_is_no(evidence, field) for field in driving_fields)
    if not all_explicit_no:
        return "low"
    return "high" if _has_named_detail(evidence) else "medium"


def _evidence_and_gaps(evidence: Dict[str, Any], field_descriptions: Dict[str, str]) -> Tuple[List[str], List[str]]:
    """Build (evidence, missing_evidence) string lists for a gate's driving fields."""
    found, missing = [], []
    for field_id, description in field_descriptions.items():
        value = evidence.get(field_id)
        if value in (YES, NO):
            found.append(f"{field_id}={value} ({description})")
        else:
            missing.append(f"{field_id}: not stated in description ({description})")
    return found, missing


# =============================================================================
# GATE 1: GENAI GENERATION
# =============================================================================

def _gate_genai_generation(evidence: Dict[str, Any]) -> Dict[str, Any]:
    driving_fields = ["uses_llm_or_generative_ai"]
    verified = _is_yes(evidence, "uses_llm_or_generative_ai")
    found, missing = _evidence_and_gaps(evidence, {
        "uses_llm_or_generative_ai": "LLM/foundation model/generative AI usage",
    })
    if _is_yes(evidence, "uses_traditional_ml_or_statistical_model"):
        found.append("uses_traditional_ml_or_statistical_model=yes (confirmed traditional statistical/ML model, non-generative)")

    if verified:
        rationale = "GenAI generation verified: " + "; ".join(found)
    elif _is_no(evidence, "uses_llm_or_generative_ai"):
        rationale = "GenAI generation not verified (explicitly confirmed non-generative)."
    else:
        rationale = "GenAI generation not verified - no evidence of LLM/generative AI usage stated."

    return {
        "verified": verified,
        "evidence": found,
        "missing_evidence": missing,
        "rationale": rationale,
        "_confidence": _gate_confidence(evidence, driving_fields, verified),
    }


# =============================================================================
# GATE 2: RUNTIME RETRIEVAL
# =============================================================================

def _gate_runtime_retrieval(evidence: Dict[str, Any], genai_verified: bool) -> Dict[str, Any]:
    # Per spec: Level 3 requires GenAI generation = true AND runtime
    # retrieval = true. Traditional ML feature retrieval, DB queries, and
    # batch ETL (retrieves_data_for_features_or_batch_processing) do NOT
    # count, even if present, unless the retrieved content actually grounds
    # a GenAI output at runtime.
    driving_fields = ["uses_llm_or_generative_ai", "uses_runtime_retrieval_for_genai_grounding"]
    has_retrieval = _is_yes(evidence, "uses_runtime_retrieval_for_genai_grounding")
    verified = genai_verified and has_retrieval

    found, missing = _evidence_and_gaps(evidence, {
        "uses_runtime_retrieval_for_genai_grounding": "runtime retrieval used to ground/cite/contextualize GenAI output",
    })
    if _is_yes(evidence, "retrieves_data_for_features_or_batch_processing"):
        found.append(
            "retrieves_data_for_features_or_batch_processing=yes (feature/batch/ETL retrieval - "
            "does not by itself count as GenAI runtime retrieval)"
        )

    if verified:
        rationale = "Runtime retrieval verified: GenAI generation is verified and " + "; ".join(found)
    elif has_retrieval and not genai_verified:
        rationale = (
            "Retrieval evidence present, but GenAI generation is not verified - retrieval alone "
            "(without generative usage) does not constitute RAG per the Level 3 definition."
        )
    elif _is_yes(evidence, "retrieves_data_for_features_or_batch_processing") and not has_retrieval:
        rationale = (
            "Retrieval is for model features, database lookups, or batch ETL, not used at runtime "
            "to ground a GenAI output - does not qualify as Level 3 runtime retrieval."
        )
    elif _is_no(evidence, "uses_runtime_retrieval_for_genai_grounding"):
        rationale = "Runtime retrieval not verified (explicitly confirmed no runtime retrieval)."
    else:
        rationale = "Runtime retrieval not verified - no evidence of runtime knowledge retrieval stated."

    return {
        "verified": verified,
        "evidence": found,
        "missing_evidence": missing,
        "rationale": rationale,
        "_confidence": _gate_confidence(evidence, driving_fields, verified),
    }


# =============================================================================
# GATE 3: TOOL / ACTION EXECUTION
# =============================================================================

_TOOL_ACTION_FIELDS = [
    "model_output_changes_system_state", "ai_selects_tool_or_action",
    "predefined_workflow_triggered_by_model_output",
    "system_of_record_write_permission", "model_output_initiates_external_communication",
    "model_output_triggers_transaction_or_approval",
]


def _gate_tool_or_action_execution(evidence: Dict[str, Any]) -> Dict[str, Any]:
    verified = any(_is_yes(evidence, f) for f in _TOOL_ACTION_FIELDS)
    found, missing = _evidence_and_gaps(evidence, {
        "model_output_changes_system_state": "model output directly changes system-of-record state",
        "ai_selects_tool_or_action": "AI selects which tool/action to invoke",
        "predefined_workflow_triggered_by_model_output": "model output triggers a predefined downstream workflow/action",
        "system_of_record_write_permission": "system/service account has write permission to a system of record",
        "model_output_initiates_external_communication": "model output can initiate external communication (email/SMS/message)",
        "model_output_triggers_transaction_or_approval": "model output can trigger a financial transaction or approval/denial decision",
    })

    if verified:
        rationale = "Tool/action execution verified: " + "; ".join(
            f"{f}=yes" for f in _TOOL_ACTION_FIELDS if _is_yes(evidence, f)
        )
    elif all(_is_no(evidence, f) for f in _TOOL_ACTION_FIELDS):
        rationale = "Tool/action execution not verified (explicitly confirmed no action-causing capability)."
    else:
        rationale = "Tool/action execution not verified - no evidence of AI-mediated action execution stated."

    return {
        "verified": verified,
        "evidence": found,
        "missing_evidence": missing,
        "rationale": rationale,
        "_confidence": _gate_confidence(evidence, _TOOL_ACTION_FIELDS, verified),
    }


# =============================================================================
# GATE 4: AUTONOMOUS OPERATION
# =============================================================================
# THE critical gate for the automated-execution vs autonomous-agentic-
# decision-making distinction. Per spec, verified requires ALL of:
#   1. tool_or_action_execution.verified == true
#   2. ai_decides_to_act_or_continue == true   <- the key differentiator;
#      running on a schedule/trigger, batch processing, auto-approving a
#      predefined decision, applying a threshold rule, or having no human
#      review per transaction NEVER satisfies this on their own.
#   3. at least one agentic autonomy capability verified (planning, goal
#      pursuit, looping/retry, memory/state continuation, delegation,
#      adaptive plan revision, or the AI itself selecting the tool/next step).

_AGENTIC_CAPABILITY_FIELDS = [
    "ai_selects_tool_or_action", "ai_selects_next_step", "has_dynamic_multi_step_planning",
    "has_goal_pursuit", "has_looping_or_retry_based_on_outcomes",
    "has_memory_or_state_driven_continuation", "has_delegation_to_other_agents",
    "has_adaptive_plan_revision",
]


def _gate_autonomous_operation(evidence: Dict[str, Any], tool_verified: bool) -> Dict[str, Any]:
    ai_decides = _is_yes(evidence, "ai_decides_to_act_or_continue")
    agentic_capability_present = any(_is_yes(evidence, f) for f in _AGENTIC_CAPABILITY_FIELDS)

    verified = tool_verified and ai_decides and agentic_capability_present

    driving_fields = ["ai_decides_to_act_or_continue"] + _AGENTIC_CAPABILITY_FIELDS
    found, missing = _evidence_and_gaps(evidence, {
        "ai_decides_to_act_or_continue": "AI has discretion over whether to act/continue",
        "ai_selects_next_step": "AI decides the next step based on intermediate results",
        "has_dynamic_multi_step_planning": "dynamic multi-step planning/sequencing",
        "has_goal_pursuit": "goal/objective pursuit across multiple actions",
        "has_looping_or_retry_based_on_outcomes": "looping/retry based on outcomes",
        "has_memory_or_state_driven_continuation": "memory/state-driven continuation",
        "has_delegation_to_other_agents": "delegation to other agents/sub-processes",
        "has_adaptive_plan_revision": "adaptive plan revision based on observed results",
    })
    if _is_yes(evidence, "ai_selects_tool_or_action"):
        found.insert(0, "ai_selects_tool_or_action=yes (AI selects among tools/actions)")

    rationale_parts = []

    # --- Explicit negative-logic messages (verbatim per spec) ---
    if _is_yes(evidence, "runs_on_schedule_or_event_trigger") and not ai_decides:
        rationale_parts.append(
            "Scheduled or event-triggered automation does not by itself establish autonomous "
            "agentic decision-making."
        )
    if (
        _is_yes(evidence, "predefined_workflow_triggered_by_model_output")
        and not _is_yes(evidence, "ai_selects_next_step")
        and not _is_yes(evidence, "has_dynamic_multi_step_planning")
    ):
        rationale_parts.append(
            "Predefined downstream action execution is action execution, not autonomous agency."
        )
    if _is_no(evidence, "requires_human_approval_per_action") and not ai_decides:
        rationale_parts.append(
            "Absence of human review per action is insufficient to establish autonomy unless AI "
            "discretion over action or continuation is verified."
        )

    if verified:
        rationale_parts.insert(0, "Autonomous operation verified: " + "; ".join(found))
    elif not tool_verified and (ai_decides or agentic_capability_present):
        missing.append(
            "tool_or_action_execution: agentic signals present without verified action capability - "
            "action capability is required before autonomy can be established"
        )
        rationale_parts.insert(0, (
            "Agentic behavior signals present, but tool/action execution is not verified. "
            "Autonomous agentic decision-making requires the AI to actually be able to act."
        ))
    elif tool_verified and not ai_decides:
        rationale_parts.insert(0, (
            "Tool/action execution is verified, but there is no evidence the AI itself decides "
            "whether to act or continue - this is action execution, not autonomous agency."
        ))
    elif tool_verified and ai_decides and not agentic_capability_present:
        rationale_parts.insert(0, (
            "AI discretion over acting/continuing is indicated, but no specific agentic capability "
            "(planning, goal pursuit, looping, memory/state, delegation, or plan revision) is verified."
        ))
    else:
        rationale_parts.insert(0, "Autonomous operation not verified - no evidence of autonomous agentic decision-making stated.")

    rationale = " ".join(rationale_parts)

    return {
        "verified": verified,
        "evidence": found,
        "missing_evidence": missing,
        "rationale": rationale,
        "_confidence": _gate_confidence(evidence, driving_fields, verified),
    }


# =============================================================================
# DETERMINISTIC MODEL TYPE CLASSIFICATION (sequential gate promotion)
# =============================================================================

def classify_model_type(evidence: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministically classify model capability level (1-5) from structured
    evidence answers, via 4 explicit promotion gates. Claude never assigns
    the level itself - only the factual per-field answers.
    """
    gate_genai = _gate_genai_generation(evidence)
    gate_retrieval = _gate_runtime_retrieval(evidence, genai_verified=gate_genai["verified"])
    gate_tool = _gate_tool_or_action_execution(evidence)
    gate_autonomy = _gate_autonomous_operation(evidence, tool_verified=gate_tool["verified"])

    # Sequential promotion: start at Level 1, promote per verified gate.
    # Level 5 requires the autonomous_operation gate itself (which already
    # requires tool_or_action_execution.verified as one of its 3 conjuncts).
    level = 1
    driving_gate_name = None
    if gate_genai["verified"]:
        level, driving_gate_name = 2, "genai_generation"
    if gate_retrieval["verified"]:
        level, driving_gate_name = 3, "runtime_retrieval"
    if gate_tool["verified"]:
        level, driving_gate_name = 4, "tool_or_action_execution"
    if gate_autonomy["verified"]:
        level, driving_gate_name = 5, "autonomous_operation"

    gates = {
        "genai_generation": gate_genai,
        "runtime_retrieval": gate_retrieval,
        "tool_or_action_execution": gate_tool,
        "autonomous_operation": gate_autonomy,
    }

    if driving_gate_name:
        confidence = gates[driving_gate_name]["_confidence"]
    else:
        # Level 1 by default - confidence reflects whether absence of higher
        # capabilities was explicitly confirmed or simply unknown.
        confidence = _gate_confidence(evidence, ["uses_llm_or_generative_ai"], verified=False)

    rationale_parts = [f"Final level {level} ({MODEL_TYPE_LABELS[level]})."]

    if level == 5:
        rationale_parts.append(
            "Level 5 (autonomous agent) reached: " + gate_autonomy["rationale"] +
            f" Goal/task pursuit: {'verified' if _is_yes(evidence, 'has_goal_pursuit') else 'not independently confirmed'}. "
            f"Action/tool discretion: {'AI selects among tools/actions' if _is_yes(evidence, 'ai_selects_tool_or_action') else 'not independently confirmed'}. "
            f"Sequencing/revision/retry/delegation/escalation: " + ", ".join(
                f for f in [
                    "dynamic multi-step planning" if _is_yes(evidence, "has_dynamic_multi_step_planning") else None,
                    "adaptive plan revision" if _is_yes(evidence, "has_adaptive_plan_revision") else None,
                    "looping/retry on outcomes" if _is_yes(evidence, "has_looping_or_retry_based_on_outcomes") else None,
                    "delegation to other agents" if _is_yes(evidence, "has_delegation_to_other_agents") else None,
                    "memory/state-driven continuation" if _is_yes(evidence, "has_memory_or_state_driven_continuation") else None,
                ] if f
            ) or "none independently itemized beyond the driving signal above." +
            f" Guardrails: human approval per action is {'required' if _is_yes(evidence, 'requires_human_approval_per_action') else ('not required' if _is_no(evidence, 'requires_human_approval_per_action') else 'not stated')}."
        )
    elif driving_gate_name == "tool_or_action_execution" or (gate_tool["verified"] and level == 4):
        # Non-Level-5 system with action-causing automation: explain what's
        # automated, whether predefined, whether AI has discretion, and why
        # it isn't autonomous.
        is_predefined = _is_yes(evidence, "predefined_workflow_triggered_by_model_output") or _is_yes(evidence, "model_output_changes_system_state")
        rationale_parts.append(
            f"This system causes system-of-record action ({'predefined/fixed action' if is_predefined else 'AI-selected action'}), "
            f"reaching Level 4 (Agentic workflow / AI-mediated action execution). "
            f"AI discretion over whether to act or continue: {'not verified' if not _is_yes(evidence, 'ai_decides_to_act_or_continue') else 'verified but no agentic capability confirmed'}. "
            "Not classified as Level 5 because autonomous agentic decision-making " +
            ("was not verified - " + gate_autonomy["rationale"] if gate_autonomy["rationale"] else "requires AI discretion over acting/continuing plus at least one agentic capability, neither of which is confirmed here.")
        )
    elif driving_gate_name:
        rationale_parts.append(f"Determined by the '{driving_gate_name}' gate: {gates[driving_gate_name]['rationale']}")
    else:
        rationale_parts.append("No higher-capability gates were verified; defaulted to Level 1.")

    if evidence.get("product_label_mentioned"):
        rationale_parts.append(
            f"Note: the description uses the label \"{evidence['product_label_mentioned']}\" - "
            "this is a candidate signal only and was not used to determine the level."
        )

    # Strip internal-only "_confidence" key before returning each gate.
    public_gates = {
        name: {k: v for k, v in gate.items() if k != "_confidence"}
        for name, gate in gates.items()
    }

    return {
        "final_level": level,
        "final_label": MODEL_TYPE_LABELS[level],
        "classification_method": CLASSIFICATION_METHOD,
        "confidence": confidence,
        "promotion_gates": public_gates,
        "rationale": " ".join(rationale_parts),
    }


# =============================================================================
# DELIVERY MODEL CLASSIFICATION
# =============================================================================

def classify_delivery_model(evidence: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deterministically classify delivery model from structured evidence
    answers. Classified separately from model type - does not change
    capability level, but is used for evidence ownership and Evidence Pack
    triggers (Vendor Platform Pack).
    """
    vendor_name = evidence.get("vendor_product_named")
    hosting = evidence.get("foundation_model_hosting")

    evidence_list: List[str] = []
    missing: List[str] = []

    if vendor_name:
        evidence_list.append(f"vendor_product_named={vendor_name}")
    else:
        missing.append("vendor_product_named: not stated in description")

    if hosting in ("internal_hosted", "vendor_hosted"):
        evidence_list.append(f"foundation_model_hosting={hosting}")
    else:
        missing.append("foundation_model_hosting: not stated in description")

    if vendor_name:
        label = "embedded_saas_ai" if _looks_embedded(vendor_name) else "vendor_platform"
        rationale = f"Named vendor product \"{vendor_name}\" identifies this as {DELIVERY_MODEL_LABELS[label]}."
        confidence = "high"
    elif hosting == "vendor_hosted":
        label = "vendor_platform"
        rationale = "Foundation model is vendor-hosted; no specific product name was given."
        confidence = "medium"
    elif hosting == "internal_hosted":
        label = "internal_build"
        rationale = "Foundation model is internally hosted and controlled, with no vendor product named."
        confidence = "medium"
    else:
        label = "unknown"
        rationale = "Insufficient evidence to determine hosting or vendor product."
        confidence = "low"

    return {
        "label": label,
        "confidence": confidence,
        "evidence": evidence_list,
        "missing_evidence": missing,
        "rationale": rationale,
    }


def _looks_embedded(vendor_name: str) -> bool:
    lowered = vendor_name.lower()
    return any(keyword in lowered for keyword in _EMBEDDED_SAAS_KEYWORDS)
