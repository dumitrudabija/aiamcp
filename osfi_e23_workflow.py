"""
OSFI E-23 Five-Step Capability Evidence Workflow

Enforces the mandatory assessment order:
    1. Model type identification            (model_type_identification)
    2. Capability Evidence Pack triggers     (capability_evidence_pack_triggers)
    3. Existing 47-question assessment       (forty_seven_question_assessment)
    4. Risk level + conditions               (risk_level_and_conditions)
    5. Required governance actions           (required_governance_actions)

This order is mandatory: Capability Evidence Packs are triggered BEFORE the
47-question assessment runs (they are not a post-report add-on), and no step
may run before its required predecessor has completed. Each step is a small,
independently testable, deterministic function - the LLM has already done
all its work upstream (supplying model_type_evidence + the 47-factor
extraction); every step here is pure server-side logic.

Capability Evidence Packs never produce independent risk scores - the base
risk score/level comes only from the existing 47-question assessment (step
3); packs only ever add conditions, blockers, and evidence gaps on top.
"""

from typing import Dict, Any, List, Optional
import logging

from model_type_classification import (
    classify_model_type,
    classify_delivery_model,
)
from conditional_modules import evaluate_capability_evidence_packs
from risk_dimension_extraction import process_extraction_response
from osfi_e23_risk_dimensions import get_dimension, get_total_factor_count

logger = logging.getLogger(__name__)


WORKFLOW_VERSION = "five_step_capability_evidence_workflow_v1"

STEP_MODEL_TYPE = "model_type_identification"
STEP_EVIDENCE_PACKS = "capability_evidence_pack_triggers"
STEP_47Q = "forty_seven_question_assessment"
STEP_RISK_CONDITIONS = "risk_level_and_conditions"
STEP_GOVERNANCE = "required_governance_actions"

WORKFLOW_STEP_ORDER = [
    STEP_MODEL_TYPE,
    STEP_EVIDENCE_PACKS,
    STEP_47Q,
    STEP_RISK_CONDITIONS,
    STEP_GOVERNANCE,
]


class WorkflowOrderError(Exception):
    """Raised when a workflow step is attempted before its required predecessor has completed."""
    pass


class AssessmentWorkflowContext:
    """
    Shared context that accumulates each step's output and tracks which
    steps have completed, in order. Steps read prior steps' output from
    `.data` and guard against running out of order via `require_completed`.
    """

    def __init__(self):
        self.steps_completed: List[str] = []
        self.data: Dict[str, Any] = {}

    def require_completed(self, required_step: str, current_step: str):
        if required_step not in self.steps_completed:
            raise WorkflowOrderError(
                f"{required_step} must complete before {current_step}"
            )

    def require_all_prior_completed(self, current_step: str):
        """
        Check every step that must precede `current_step` in
        WORKFLOW_STEP_ORDER, and raise naming the EARLIEST missing one (not
        just the immediate predecessor) - e.g. attempting step 3 with
        nothing done yet reports step 1 as missing, not step 2.
        """
        current_index = WORKFLOW_STEP_ORDER.index(current_step)
        for prior_step in WORKFLOW_STEP_ORDER[:current_index]:
            if prior_step not in self.steps_completed:
                raise WorkflowOrderError(
                    f"{prior_step} must complete before {current_step}"
                )

    def mark_completed(self, step: str):
        if step not in self.steps_completed:
            self.steps_completed.append(step)


# =============================================================================
# STEP 1: MODEL TYPE IDENTIFICATION
# =============================================================================

def classify_model_type_step(
    context: AssessmentWorkflowContext, model_type_evidence: Dict[str, Any]
) -> Dict[str, Any]:
    """Determine the model's highest verified capability level and delivery model."""
    model_type_classification = classify_model_type(model_type_evidence)
    delivery_model = classify_delivery_model(model_type_evidence)

    context.data["model_type_evidence"] = model_type_evidence
    context.data["model_type_classification"] = model_type_classification
    context.data["delivery_model"] = delivery_model
    context.mark_completed(STEP_MODEL_TYPE)

    return {"model_type_classification": model_type_classification, "delivery_model": delivery_model}


# =============================================================================
# STEP 2: CAPABILITY EVIDENCE PACK TRIGGERS
# =============================================================================

def trigger_capability_evidence_packs_step(context: AssessmentWorkflowContext) -> Dict[str, Any]:
    """Determine which Capability Evidence Packs are required, before the 47-question assessment runs."""
    context.require_all_prior_completed(STEP_EVIDENCE_PACKS)

    model_type_classification = context.data["model_type_classification"]
    delivery_model = context.data["delivery_model"]
    evidence = context.data["model_type_evidence"]

    triggered, not_triggered = evaluate_capability_evidence_packs(
        model_type_classification, delivery_model, evidence
    )
    for pack in triggered:
        pack["mapped_dimension_names"] = [
            get_dimension(dim_id)["name"] for dim_id in pack["mapped_dimensions"]
        ]

    capability_evidence_packs = {"triggered": triggered, "not_triggered": not_triggered}
    context.data["capability_evidence_packs"] = capability_evidence_packs
    context.mark_completed(STEP_EVIDENCE_PACKS)

    return capability_evidence_packs


# =============================================================================
# STEP 3: EXISTING 47-QUESTION ASSESSMENT
# =============================================================================

def run_forty_seven_question_assessment_step(
    context: AssessmentWorkflowContext, extracted_factors: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run the existing 47-question assessment core (unchanged questions,
    dimensions, scoring, and weights). Requires Capability Evidence Pack
    triggers to have already been evaluated (step 2) - packs identify
    required evidence for/around this assessment, they are not a
    post-report add-on run after the fact.
    """
    context.require_all_prior_completed(STEP_47Q)

    assessment_result = process_extraction_response(extracted_factors)
    context.data["assessment_result"] = assessment_result
    context.mark_completed(STEP_47Q)

    return assessment_result


# =============================================================================
# STEP 4: RISK LEVEL + CONDITIONS
# =============================================================================

def _compute_final_status(base_risk_level: str, blockers: List[str], conditions: List[str]) -> str:
    """
    Deterministic production/next-stage readiness status, in strict priority
    order: blockers always win (Blocked), then conditions (Conditional), then
    High/Critical base risk with neither (Escalation Required), else Ready.
    This is a report/status derivation on top of the risk level - it does not
    alter the risk level or scoring itself.
    """
    if blockers:
        return "Blocked"
    if conditions:
        return "Conditional"
    if base_risk_level in ("High", "Critical"):
        return "Escalation Required"
    return "Ready"


def determine_risk_level_and_conditions_step(context: AssessmentWorkflowContext) -> Dict[str, Any]:
    """
    Produce the final assessment result: the 47-question assessment supplies
    the base risk score/level; Capability Evidence Pack findings qualify it
    with conditions/blockers/evidence gaps - they never change the risk
    score or level itself (no independent Evidence Pack risk scores).
    """
    context.require_all_prior_completed(STEP_RISK_CONDITIONS)

    assessment_result = context.data["assessment_result"]
    overall = assessment_result["overall_assessment"]
    base_risk_level = overall["overall_risk_level"].title()  # low -> Low
    base_risk_score = int(overall["overall_numeric_score"] * 25)  # 1-4 scale to 0-100

    triggered_packs = context.data["capability_evidence_packs"]["triggered"]
    conditions = [c for pack in triggered_packs for c in pack["governance_conditions"]]
    blockers = [b for pack in triggered_packs for b in pack["blockers"]]
    evidence_gaps = [g for pack in triggered_packs for g in pack["evidence_gaps"]]

    # Capability Evidence Packs never create an independent risk score/level -
    # the final level always equals the base level from the 47-question core;
    # packs only ever add conditions/blockers/evidence gaps on top of it.
    final_risk_level = base_risk_level

    rationale_parts = [
        f"Base risk level {base_risk_level} ({base_risk_score}/100) determined by the 47-question assessment."
    ]
    if blockers:
        rationale_parts.append(
            f"{len(blockers)} production blocker(s) identified from triggered Capability Evidence Packs; "
            "these must be resolved but do not change the base risk level itself."
        )
    if conditions:
        rationale_parts.append(f"{len(conditions)} governance condition(s) identified from triggered Capability Evidence Packs.")
    if not triggered_packs:
        rationale_parts.append("No Capability Evidence Packs were triggered.")

    final_result = {
        "final_risk_level": final_risk_level,
        "base_risk_level": base_risk_level,
        "conditions": conditions,
        "blockers": blockers,
        "evidence_gaps": evidence_gaps,
        "final_status": _compute_final_status(base_risk_level, blockers, conditions),
        "rationale": " ".join(rationale_parts),
    }

    context.data["base_risk_score"] = base_risk_score
    context.data["base_risk_level"] = base_risk_level
    context.data["final_result"] = final_result
    context.mark_completed(STEP_RISK_CONDITIONS)

    return final_result


# =============================================================================
# STEP 5: REQUIRED GOVERNANCE ACTIONS
# =============================================================================

def generate_required_governance_actions_step(context: AssessmentWorkflowContext) -> List[Dict[str, str]]:
    """
    Translate the risk level, conditions, blockers, and evidence gaps into a
    practical governance action list, categorized per the spec's governance
    action categories (Documentation, Validation, Security/access controls,
    Vendor assurance, Monitoring, Human oversight, Approval, Issue
    remediation, Model inventory update, Workflow/ticket creation).

    Each action carries source_pack, priority (blocker/high/medium/low - set
    at the source in conditional_modules.py for pack-derived actions, or
    assigned here for baseline workflow actions), an owner placeholder
    ("TBD" - institution-assignable), and a due_stage placeholder (a
    reasonable default lifecycle stage, institution-adjustable).
    """
    context.require_all_prior_completed(STEP_GOVERNANCE)

    final_result = context.data["final_result"]
    triggered_packs = context.data["capability_evidence_packs"]["triggered"]

    actions: List[Dict[str, str]] = []

    # Pack-level governance actions (category + priority already set in conditional_modules.py).
    for pack in triggered_packs:
        for action in pack["governance_actions"]:
            actions.append({
                "category": action["category"],
                "action": action["action"],
                "source_pack": pack["pack_id"],
                "priority": action.get("priority", "high"),
                "owner": "TBD",
                "due_stage": "Deployment",
            })

    # Baseline actions that always apply, scaled by risk level / blockers / gaps.
    risk_level = final_result["final_risk_level"]
    actions.append({
        "category": "Approval",
        "action": f"Obtain risk-appropriate governance approval for a {risk_level}-rated model prior to deployment.",
        "source_pack": None,
        "priority": "high",
        "owner": "TBD",
        "due_stage": "Deployment",
    })
    actions.append({
        "category": "Model inventory update",
        "action": "Register this model in the institution's AI/model inventory with its classification, delivery model, and risk level.",
        "source_pack": None,
        "priority": "medium",
        "owner": "TBD",
        "due_stage": "Design",
    })
    actions.append({
        "category": "Documentation",
        "action": "Document the classification, 47-question assessment results, risk level, and conditions for audit purposes.",
        "source_pack": None,
        "priority": "medium",
        "owner": "TBD",
        "due_stage": "Design",
    })
    if final_result["blockers"]:
        actions.append({
            "category": "Issue remediation",
            "action": "Resolve all identified production blockers before deployment.",
            "source_pack": None,
            "priority": "blocker",
            "owner": "TBD",
            "due_stage": "Deployment",
        })
    if final_result["evidence_gaps"]:
        actions.append({
            "category": "Workflow / ticket creation",
            "action": "Create tracking tickets for all identified evidence gaps and assign owners.",
            "source_pack": None,
            "priority": "medium",
            "owner": "TBD",
            "due_stage": "Review",
        })

    context.data["required_governance_actions"] = actions
    context.mark_completed(STEP_GOVERNANCE)

    return actions


# =============================================================================
# FULL PIPELINE ORCHESTRATION
# =============================================================================

def run_five_step_workflow(
    model_type_evidence: Dict[str, Any], extracted_factors: Dict[str, Any]
) -> AssessmentWorkflowContext:
    """
    Run all 5 steps in the mandatory order and return the populated context.
    This is the single entry point server.py should call - it guarantees
    the order is enforced (each step's own guard would raise otherwise).
    """
    context = AssessmentWorkflowContext()
    classify_model_type_step(context, model_type_evidence)
    trigger_capability_evidence_packs_step(context)
    run_forty_seven_question_assessment_step(context, extracted_factors)
    determine_risk_level_and_conditions_step(context)
    generate_required_governance_actions_step(context)
    return context
