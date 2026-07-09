#!/usr/bin/env python3
"""
Functional tests for the 4 required workflow-order scenarios, exercised
end-to-end through server._assess_model_risk() (Phase 2 - as if Claude had
already extracted factors + model_type_evidence), verifying the mandatory
five-step Capability Evidence Workflow order and outputs.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from server import MCPServer

# Minimal shared 47-factor payload - just enough to exercise the pipeline;
# any factor not listed defaults to NOT_STATED (Medium), which is fine here
# since these tests assert on workflow structure/classification/packs, not
# the exact risk score itself.
_MINIMAL_DIMENSIONS_PAYLOAD = {
    "misuse_unintended_harm": {
        "financial_exposure": {"value": 10000, "evidence": None},
    },
    "complexity_opacity": {
        "feature_count": {"value": 20, "evidence": None},
    },
}

_EXPECTED_STEP_ORDER = [
    "model_type_identification",
    "capability_evidence_pack_triggers",
    "forty_seven_question_assessment",
    "risk_level_and_conditions",
    "required_governance_actions",
]


def _make_server() -> MCPServer:
    server = MCPServer()
    server._load_processors()
    server.introduction_shown = True
    return server


def _assess(server, model_type_evidence):
    return server._assess_model_risk({
        "projectName": "Scenario Test",
        "projectDescription": "A system used for testing the five-step workflow scenarios.",
        "currentStage": "design",
        "extracted_factors": {
            "dimensions": _MINIMAL_DIMENSIONS_PAYLOAD,
            "model_type_evidence": model_type_evidence,
        },
    })


def _assert_workflow_order(result):
    assert result["workflow_version"] == "five_step_capability_evidence_workflow_v1"
    assert result["workflow_steps_completed"] == _EXPECTED_STEP_ORDER


def test_1_traditional_scorecard():
    """Step 1 final_level=1; Step 2 no packs; Step 3 47 questions run; Step 4 base risk level; Step 5 governance actions."""
    server = _make_server()
    result = _assess(server, {
        "uses_traditional_ml_or_statistical_model": "yes",
        "uses_llm_or_generative_ai": "no",
        "uses_runtime_retrieval_for_genai_grounding": "no",
    })

    assert result["phase"] == "assessment_complete"
    _assert_workflow_order(result)

    # Step 1
    assert result["model_type_classification"]["final_level"] == 1

    # Step 2 - no Knowledge/Action/Autonomy/Vendor packs
    triggered_ids = {p["pack_id"] for p in result["capability_evidence_packs"]["triggered"]}
    assert triggered_ids == set()

    # Step 3 - 47 questions ran
    assert result["core_assessment"]["question_count"] == 47
    assert result["core_assessment"]["base_risk_level"]

    # Step 4 - base risk level produced
    assert result["final_result"]["base_risk_level"] == result["core_assessment"]["base_risk_level"]
    assert result["final_result"]["final_risk_level"] == result["final_result"]["base_risk_level"]

    # Step 5 - governance actions produced
    assert len(result["required_governance_actions"]) > 0
    print("PASS: (1) traditional scorecard - full 5-step order, Level 1, no packs, governance actions produced")


def test_2_internal_rag_chatbot():
    """Step 1 final_level=3; Step 2 Knowledge Access Pack triggered; Step 4/5 include retrieval conditions if gaps exist."""
    server = _make_server()
    result = _assess(server, {
        "uses_llm_or_generative_ai": "yes",
        "uses_runtime_retrieval_for_genai_grounding": "yes",
        # has_retrieval_access_controls deliberately not_stated -> evidence gap expected
    })

    _assert_workflow_order(result)
    assert result["model_type_classification"]["final_level"] == 3

    triggered_ids = {p["pack_id"] for p in result["capability_evidence_packs"]["triggered"]}
    assert triggered_ids == {"knowledge_access"}

    # Step 4: conditions include the retrieval/access-control gap
    assert any("access" in c.lower() or "authorized" in c.lower() for c in result["final_result"]["conditions"])

    # Step 5: governance actions include retrieval/source/entitlement-related actions
    actions_text = " ".join(a["action"] for a in result["required_governance_actions"]).lower()
    assert "access" in actions_text or "authorized" in actions_text or "entitl" in actions_text
    print("PASS: (2) internal RAG chatbot - Level 3, Knowledge Access Pack, retrieval/access-control conditions and governance actions present")


def test_3_agentforce_bounded_case_workflow():
    """Step 1 final_level=4, vendor_platform; Step 2 Action Execution + Vendor/Platform triggered, not Autonomy."""
    server = _make_server()
    result = _assess(server, {
        "vendor_product_named": "Salesforce Agentforce",
        "ai_selects_tool_or_action": "yes",
        "requires_human_approval_per_action": "yes",
        # has_action_audit_logging / has_vendor_assurance_evidence not_stated -> gaps expected
    })

    _assert_workflow_order(result)
    assert result["model_type_classification"]["final_level"] == 4
    assert result["delivery_model"]["label"] == "vendor_platform"

    triggered_ids = {p["pack_id"] for p in result["capability_evidence_packs"]["triggered"]}
    assert triggered_ids == {"action_execution", "vendor_platform"}
    assert "autonomy" not in triggered_ids

    # Step 5: governance actions include logging, approvals, vendor assurance, ownership as applicable
    actions_text = " ".join(a["action"] for a in result["required_governance_actions"]).lower()
    assert "logging" in actions_text
    assert "approval" in actions_text
    assert "vendor" in actions_text
    print("PASS: (3) Agentforce bounded case - Level 4, vendor_platform, Action Execution + Vendor/Platform Pack, not Autonomy")


def test_4_servicenow_autonomous_incident_agent():
    """Step 1 final_level=5, vendor_platform; Step 2 Action Execution + Autonomy + Vendor/Platform triggered."""
    server = _make_server()
    result = _assess(server, {
        "vendor_product_named": "ServiceNow",
        "ai_selects_tool_or_action": "yes",
        "ai_decides_to_act_or_continue": "yes",
        "has_adaptive_plan_revision": "yes",
        "runs_on_schedule_or_event_trigger": "yes",
        "requires_human_approval_per_action": "no",
        # has_kill_switch_or_stop_condition not_stated -> blocker expected
    })

    _assert_workflow_order(result)
    assert result["model_type_classification"]["final_level"] == 5
    assert result["delivery_model"]["label"] == "vendor_platform"

    triggered_ids = {p["pack_id"] for p in result["capability_evidence_packs"]["triggered"]}
    assert triggered_ids == {"action_execution", "autonomy", "vendor_platform"}

    # Step 4: conditions/blockers generated for missing stop conditions, logging, or vendor evidence
    assert len(result["final_result"]["blockers"]) > 0
    assert len(result["final_result"]["evidence_gaps"]) > 0

    # Step 5: governance actions generated
    assert len(result["required_governance_actions"]) > 0
    print("PASS: (4) ServiceNow autonomous incident agent - Level 5, all 3 packs, blockers/gaps/governance actions generated")


def test_scheduled_trigger_without_ai_discretion_stays_level4_not_5():
    """
    Regression test for the core fix: the same ServiceNow vendor + tool
    execution + schedule/trigger + no human review pattern that PREVIOUSLY
    (incorrectly) reached Level 5 must now stay at Level 4, since
    ai_decides_to_act_or_continue is not stated - schedule/trigger-based
    execution alone must never imply autonomous agentic decision-making.
    """
    server = _make_server()
    result = _assess(server, {
        "vendor_product_named": "ServiceNow",
        "ai_selects_tool_or_action": "yes",
        "runs_on_schedule_or_event_trigger": "yes",
        "requires_human_approval_per_action": "no",
        # ai_decides_to_act_or_continue deliberately NOT stated
    })

    assert result["model_type_classification"]["final_level"] == 4
    assert result["model_type_classification"]["promotion_gates"]["autonomous_operation"]["verified"] is False

    triggered_ids = {p["pack_id"] for p in result["capability_evidence_packs"]["triggered"]}
    assert "autonomy" not in triggered_ids
    assert triggered_ids == {"action_execution", "vendor_platform"}
    print("PASS: schedule/trigger-based execution without AI discretion correctly stays at Level 4, not Level 5")


def test_5_workflow_guardrail_via_osfi_e23_workflow_module():
    """Test 5: running the 47-question step before model type classification must raise a workflow validation error."""
    import osfi_e23_workflow as workflow

    context = workflow.AssessmentWorkflowContext()
    try:
        workflow.run_forty_seven_question_assessment_step(
            context, {"dimensions": _MINIMAL_DIMENSIONS_PAYLOAD}
        )
        raise AssertionError("Expected WorkflowOrderError to be raised")
    except workflow.WorkflowOrderError as e:
        assert "model_type_identification" in str(e)
        assert "forty_seven_question_assessment" in str(e)
    print("PASS: (5) attempting the 47-question assessment before model type classification raises a workflow validation error")


if __name__ == "__main__":
    tests = [
        test_1_traditional_scorecard,
        test_2_internal_rag_chatbot,
        test_3_agentforce_bounded_case_workflow,
        test_4_servicenow_autonomous_incident_agent,
        test_scheduled_trigger_without_ai_discretion_stays_level4_not_5,
        test_5_workflow_guardrail_via_osfi_e23_workflow_module,
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
