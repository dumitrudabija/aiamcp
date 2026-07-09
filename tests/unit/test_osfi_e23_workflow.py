#!/usr/bin/env python3
"""
Unit tests for osfi_e23_workflow.py - the mandatory five-step Capability
Evidence Workflow order enforcement. Pure logic, no server/MCP dependency.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import osfi_e23_workflow as workflow
from model_type_classification import validate_model_type_evidence

_EXTRACTED_FACTORS = {
    "dimensions": {
        "misuse_unintended_harm": {"financial_exposure": {"value": 1000, "evidence": None}},
    }
}


def test_happy_path_completes_all_five_steps_in_order():
    evidence = validate_model_type_evidence({"uses_traditional_ml_or_statistical_model": "yes"})
    context = workflow.run_five_step_workflow(evidence, _EXTRACTED_FACTORS)
    assert context.steps_completed == [
        "model_type_identification",
        "capability_evidence_pack_triggers",
        "forty_seven_question_assessment",
        "risk_level_and_conditions",
        "required_governance_actions",
    ]
    print("PASS: happy path completes all 5 steps in the mandatory order")


def test_workflow_version_constant():
    assert workflow.WORKFLOW_VERSION == "five_step_capability_evidence_workflow_v1"
    print("PASS: workflow_version matches required schema constant")


def test_guardrail_forty_seven_question_before_model_type():
    """
    Test 5 (required): simulate running the 47-question assessment before
    model type classification. Expected: WorkflowOrderError naming
    model_type_identification and forty_seven_question_assessment.
    """
    context = workflow.AssessmentWorkflowContext()
    try:
        workflow.run_forty_seven_question_assessment_step(context, _EXTRACTED_FACTORS)
        raise AssertionError("Expected WorkflowOrderError to be raised")
    except workflow.WorkflowOrderError as e:
        message = str(e)
        assert "model_type_identification" in message, message
        assert "forty_seven_question_assessment" in message, message
        print(f"PASS: guardrail raised correctly: {message}")


def test_guardrail_evidence_packs_before_model_type():
    context = workflow.AssessmentWorkflowContext()
    try:
        workflow.trigger_capability_evidence_packs_step(context)
        raise AssertionError("Expected WorkflowOrderError to be raised")
    except workflow.WorkflowOrderError as e:
        assert "model_type_identification" in str(e)
        assert "capability_evidence_pack_triggers" in str(e)
        print("PASS: guardrail blocks capability_evidence_pack_triggers before model_type_identification")


def test_guardrail_risk_conditions_before_47q():
    context = workflow.AssessmentWorkflowContext()
    evidence = validate_model_type_evidence({"uses_traditional_ml_or_statistical_model": "yes"})
    workflow.classify_model_type_step(context, evidence)
    workflow.trigger_capability_evidence_packs_step(context)
    try:
        workflow.determine_risk_level_and_conditions_step(context)
        raise AssertionError("Expected WorkflowOrderError to be raised")
    except workflow.WorkflowOrderError as e:
        assert "forty_seven_question_assessment" in str(e)
        print("PASS: guardrail blocks risk_level_and_conditions before forty_seven_question_assessment")


def test_guardrail_governance_actions_before_risk_conditions():
    context = workflow.AssessmentWorkflowContext()
    evidence = validate_model_type_evidence({"uses_traditional_ml_or_statistical_model": "yes"})
    workflow.classify_model_type_step(context, evidence)
    workflow.trigger_capability_evidence_packs_step(context)
    workflow.run_forty_seven_question_assessment_step(context, _EXTRACTED_FACTORS)
    try:
        workflow.generate_required_governance_actions_step(context)
        raise AssertionError("Expected WorkflowOrderError to be raised")
    except workflow.WorkflowOrderError as e:
        assert "risk_level_and_conditions" in str(e)
        print("PASS: guardrail blocks required_governance_actions before risk_level_and_conditions")


def test_earliest_missing_step_reported_not_immediate_predecessor():
    """
    Attempting a step with NOTHING done yet must name the earliest missing
    prerequisite (model_type_identification), not just the immediate
    predecessor (capability_evidence_pack_triggers).
    """
    context = workflow.AssessmentWorkflowContext()
    try:
        workflow.run_forty_seven_question_assessment_step(context, _EXTRACTED_FACTORS)
        raise AssertionError("Expected WorkflowOrderError")
    except workflow.WorkflowOrderError as e:
        assert str(e) == "model_type_identification must complete before forty_seven_question_assessment"
        print("PASS: earliest missing step (not immediate predecessor) is reported")


def test_packs_never_change_final_risk_level():
    """Capability Evidence Packs must never create an independent risk score/level."""
    evidence = validate_model_type_evidence({
        "vendor_product_named": "ServiceNow",
        "ai_selects_tool_or_action": "yes",
        "ai_decides_to_act_or_continue": "yes",
        "has_adaptive_plan_revision": "yes",
        "runs_on_schedule_or_event_trigger": "yes",
        "requires_human_approval_per_action": "no",
    })
    context = workflow.run_five_step_workflow(evidence, _EXTRACTED_FACTORS)
    final_result = context.data["final_result"]
    assert final_result["final_risk_level"] == final_result["base_risk_level"]
    assert len(context.data["capability_evidence_packs"]["triggered"]) > 0  # packs did fire
    print("PASS: triggered Capability Evidence Packs do not change the final risk level from the base level")


def test_governance_actions_produced_even_with_no_packs_triggered():
    """Test 1 requirement: governance actions still produced when no packs trigger."""
    evidence = validate_model_type_evidence({"uses_traditional_ml_or_statistical_model": "yes", "uses_llm_or_generative_ai": "no"})
    context = workflow.run_five_step_workflow(evidence, _EXTRACTED_FACTORS)
    assert len(context.data["capability_evidence_packs"]["triggered"]) == 0
    assert len(context.data["required_governance_actions"]) > 0
    print("PASS: baseline governance actions are produced even when no Capability Evidence Packs trigger")


if __name__ == "__main__":
    tests = [
        test_happy_path_completes_all_five_steps_in_order,
        test_workflow_version_constant,
        test_guardrail_forty_seven_question_before_model_type,
        test_guardrail_evidence_packs_before_model_type,
        test_guardrail_risk_conditions_before_47q,
        test_guardrail_governance_actions_before_risk_conditions,
        test_earliest_missing_step_reported_not_immediate_predecessor,
        test_packs_never_change_final_risk_level,
        test_governance_actions_produced_even_with_no_packs_triggered,
    ]
    failures = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            failures += 1
            print(f"FAIL: {test.__name__}: {e}")

    print(f"\n{len(tests) - failures}/{len(tests)} tests passed")
    sys.exit(0 if failures == 0 else 1)
