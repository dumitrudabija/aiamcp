#!/usr/bin/env python3
"""
Unit tests for conditional_modules.py (Capability Evidence Packs) - pure
deterministic logic, no server/MCP dependency. Exactly 4 packs (per spec -
client/regulated impact is intentionally NOT a fifth pack): knowledge_access,
action_execution, autonomy, vendor_platform. Packs trigger off
model_type_classification promotion gate `.verified` flags and delivery_model.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from model_type_classification import validate_model_type_evidence, classify_model_type, classify_delivery_model
from conditional_modules import evaluate_capability_evidence_packs, ALL_CAPABILITY_EVIDENCE_PACKS


def _classify(**overrides):
    evidence = validate_model_type_evidence(overrides)
    model_type = classify_model_type(evidence)
    delivery_model = classify_delivery_model(evidence)
    return model_type, delivery_model, evidence


def _pack_ids(triggered):
    return {p["pack_id"] for p in triggered}


def test_exactly_four_packs_defined():
    assert len(ALL_CAPABILITY_EVIDENCE_PACKS) == 4
    ids = {p["pack_id"] for p in ALL_CAPABILITY_EVIDENCE_PACKS}
    assert ids == {"knowledge_access", "action_execution", "autonomy", "vendor_platform"}
    assert "client_regulated_impact" not in ids
    print("PASS: exactly 4 Capability Evidence Packs defined, no Client/Regulated Impact pack")


def test_no_packs_for_traditional_ml():
    model_type, delivery_model, evidence = _classify(uses_traditional_ml_or_statistical_model="yes", uses_llm_or_generative_ai="no")
    triggered, not_triggered = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    assert triggered == []
    assert len(not_triggered) == 4
    print("PASS: no packs triggered for a traditional ML model; all 4 recorded as not_triggered")


def test_knowledge_access_triggers_on_runtime_retrieval_gate():
    model_type, delivery_model, evidence = _classify(uses_llm_or_generative_ai="yes", uses_runtime_retrieval_for_genai_grounding="yes")
    triggered, not_triggered = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    assert _pack_ids(triggered) == {"knowledge_access"}
    pack = triggered[0]
    assert "runtime_retrieval.verified=true" in pack["trigger_reason"]
    assert "checks" in pack and "evidence_gaps" in pack and "governance_actions" in pack
    print("PASS: Knowledge Access pack triggers exactly on runtime_retrieval.verified=true")


def test_action_execution_triggers_on_tool_gate():
    model_type, delivery_model, evidence = _classify(ai_selects_tool_or_action="yes")
    triggered, _ = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    assert "action_execution" in _pack_ids(triggered)
    print("PASS: Action Execution pack triggers on tool_or_action_execution.verified=true")


def test_action_execution_produces_blocker_when_audit_logging_missing():
    """Worked example from spec: write actions + missing audit logging = production blocker."""
    model_type, delivery_model, evidence = _classify(ai_selects_tool_or_action="yes")
    triggered, _ = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    pack = next(p for p in triggered if p["pack_id"] == "action_execution")
    assert len(pack["blockers"]) > 0
    assert any("audit logging" in b for b in pack["blockers"])
    assert any("audit logging" in c for c in pack["governance_conditions"])
    print("PASS: missing action audit logging produces a production blocker and matching condition")


def test_action_execution_no_blocker_when_audit_logging_confirmed():
    model_type, delivery_model, evidence = _classify(
        ai_selects_tool_or_action="yes", has_action_audit_logging="yes",
    )
    triggered, _ = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    pack = next(p for p in triggered if p["pack_id"] == "action_execution")
    assert pack["blockers"] == []
    print("PASS: confirmed action audit logging produces no blocker")


def test_autonomy_pack_does_not_trigger_without_verified_action_capability():
    """
    Per spec: autonomous_operation.verified requires tool_or_action_execution.verified
    as one of its 3 required conjuncts, so agentic signals (AI decides to act, goal
    pursuit) alone - without verified action capability - must NOT trigger the
    Autonomy Pack. The Autonomy Pack can never trigger without Action Execution.
    """
    model_type, delivery_model, evidence = _classify(
        uses_llm_or_generative_ai="yes",
        ai_decides_to_act_or_continue="yes",
        has_goal_pursuit="yes",
    )
    assert model_type["promotion_gates"]["autonomous_operation"]["verified"] is False
    triggered, not_triggered = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    assert "autonomy" not in _pack_ids(triggered)
    assert "autonomy" in {p["pack_id"] for p in not_triggered}
    print("PASS: agentic signals without verified action capability do not trigger the Autonomy Pack")


def test_autonomy_pack_triggers_only_alongside_action_execution():
    """Confirms the Autonomy Pack can never trigger independent of the Action Execution Pack."""
    model_type, delivery_model, evidence = _classify(
        uses_llm_or_generative_ai="yes",
        ai_selects_tool_or_action="yes",
        ai_decides_to_act_or_continue="yes",
        has_looping_or_retry_based_on_outcomes="yes",
    )
    triggered, _ = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    triggered_ids = _pack_ids(triggered)
    if "autonomy" in triggered_ids:
        assert "action_execution" in triggered_ids
    print("PASS: whenever Autonomy Pack triggers, Action Execution Pack triggers alongside it")


def test_vendor_platform_triggers_on_delivery_model():
    model_type, delivery_model, evidence = _classify(vendor_product_named="ServiceNow")
    triggered, _ = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    assert "vendor_platform" in _pack_ids(triggered)
    print("PASS: Vendor / Platform pack triggers on delivery_model label")


def test_no_client_regulated_impact_pack_exists():
    """Client impact must stay within the 47 questions/governance escalation, not a 5th pack."""
    model_type, delivery_model, evidence = _classify(affects_customers_employees_or_regulated_decisions="yes")
    triggered, _ = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    assert "client_regulated_impact" not in _pack_ids(triggered)
    assert all(p["pack_id"] in {"knowledge_access", "action_execution", "autonomy", "vendor_platform"} for p in triggered)
    print("PASS: no Client/Regulated Impact pack triggers, even with client-impact evidence present")


def test_scenario_agentforce_bounded_workflow_exact_packs():
    """Agentforce bounded workflow (human-initiated, no AI discretion over continuation) - Action Execution + Vendor/Platform, NOT Autonomy."""
    model_type, delivery_model, evidence = _classify(
        vendor_product_named="Salesforce Agentforce",
        ai_selects_tool_or_action="yes",
        requires_human_approval_per_action="yes",
    )
    triggered, _ = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    assert model_type["final_level"] == 4
    assert _pack_ids(triggered) == {"action_execution", "vendor_platform"}
    print("PASS: Agentforce bounded workflow triggers exactly Action Execution + Vendor/Platform Pack (not Autonomy)")


def test_scenario_servicenow_autonomous_triage_exact_packs():
    """ServiceNow autonomous incident triage - AI decides to act/continue + agentic capability + action execution -> all 3 relevant packs."""
    model_type, delivery_model, evidence = _classify(
        vendor_product_named="ServiceNow",
        ai_selects_tool_or_action="yes",
        ai_decides_to_act_or_continue="yes",
        has_adaptive_plan_revision="yes",
        runs_on_schedule_or_event_trigger="yes",
        requires_human_approval_per_action="no",
    )
    triggered, _ = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    assert model_type["final_level"] == 5
    assert _pack_ids(triggered) == {"action_execution", "autonomy", "vendor_platform"}
    print("PASS: ServiceNow autonomous triage triggers Action Execution + Autonomy + Vendor/Platform Pack")


def test_scenario_servicenow_scheduled_trigger_alone_does_not_trigger_autonomy():
    """Same ServiceNow vendor + schedule/trigger + no human review, but WITHOUT AI discretion -> Level 4, no Autonomy Pack."""
    model_type, delivery_model, evidence = _classify(
        vendor_product_named="ServiceNow",
        ai_selects_tool_or_action="yes",
        runs_on_schedule_or_event_trigger="yes",
        requires_human_approval_per_action="no",
        # ai_decides_to_act_or_continue deliberately not stated
    )
    triggered, _ = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    assert model_type["final_level"] == 4
    assert _pack_ids(triggered) == {"action_execution", "vendor_platform"}
    assert "autonomy" not in _pack_ids(triggered)
    print("PASS: schedule/trigger + no human review alone (no AI discretion) does not trigger the Autonomy Pack")


def test_every_triggered_pack_maps_to_at_least_one_dimension():
    model_type, delivery_model, evidence = _classify(
        ai_selects_tool_or_action="yes", ai_decides_to_act_or_continue="yes",
        has_looping_or_retry_based_on_outcomes="yes", vendor_product_named="Agentforce",
        uses_runtime_retrieval_for_genai_grounding="yes", uses_llm_or_generative_ai="yes",
    )
    triggered, _ = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    assert len(triggered) > 0
    for pack in triggered:
        assert len(pack["mapped_dimensions"]) >= 1
    print("PASS: every triggered pack maps to at least one existing dimension")


def test_every_pack_maps_to_exactly_five_dimensions():
    """Per spec, each of the 4 packs maps to exactly 5 of the 8 risk dimensions."""
    from conditional_modules import ALL_CAPABILITY_EVIDENCE_PACKS
    valid_dims = {
        "misuse_unintended_harm", "output_reliability", "fairness_customer_impact",
        "operational_security", "complexity_opacity", "governance_oversight",
        "data_provenance_supply_chain", "systemic_concentration_risk",
    }
    for pack in ALL_CAPABILITY_EVIDENCE_PACKS:
        assert len(pack["mapped_dimensions"]) == 5, f"{pack['pack_id']} has {len(pack['mapped_dimensions'])} dims"
        assert set(pack["mapped_dimensions"]).issubset(valid_dims)
        assert pack.get("risk_dimension_mapping_notes")
    print("PASS: every pack maps to exactly 5 valid risk dimensions with mapping notes")


def test_key_questions_are_reference_only_not_computed():
    """Key questions are static reference content, not verified against evidence."""
    model_type, delivery_model, evidence = _classify(ai_selects_tool_or_action="yes")
    triggered, _ = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    pack = next(p for p in triggered if p["pack_id"] == "action_execution")
    assert len(pack["key_questions"]) == 12
    for q in pack["key_questions"]:
        assert q["evidence_status"] == "not_verified"
        assert set(q.keys()) == {
            "question_id", "question", "expected_evidence_or_control", "evidence_status",
            "evidence_summary", "missing_evidence", "condition_if_missing",
            "blocker_if_missing", "blocker_reason",
        }
    print("PASS: key_questions are static reference content (12 per pack, uniformly not_verified)")


def test_required_actions_derived_from_governance_actions():
    model_type, delivery_model, evidence = _classify(ai_selects_tool_or_action="yes")
    triggered, _ = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    pack = next(p for p in triggered if p["pack_id"] == "action_execution")
    assert pack["required_actions"] == [ga["action"] for ga in pack["governance_actions"]]
    print("PASS: required_actions is derived 1:1 from governance_actions")


def test_governance_actions_carry_priority():
    model_type, delivery_model, evidence = _classify(ai_selects_tool_or_action="yes")
    triggered, _ = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    pack = next(p for p in triggered if p["pack_id"] == "action_execution")
    priorities = {ga["priority"] for ga in pack["governance_actions"]}
    assert "blocker" in priorities  # missing audit logging -> blocker priority
    print("PASS: pack governance actions carry a priority, with blocker-linked ones marked 'blocker'")


def test_not_triggered_packs_have_triggered_false():
    model_type, delivery_model, evidence = _classify(uses_traditional_ml_or_statistical_model="yes", uses_llm_or_generative_ai="no")
    _, not_triggered = evaluate_capability_evidence_packs(model_type, delivery_model, evidence)
    assert len(not_triggered) == 4
    for pack in not_triggered:
        assert pack["triggered"] is False
        assert "pack_name" in pack and "reason" in pack
    print("PASS: not-triggered packs carry triggered=False, pack_name, and reason")


if __name__ == "__main__":
    tests = [
        test_exactly_four_packs_defined,
        test_no_packs_for_traditional_ml,
        test_knowledge_access_triggers_on_runtime_retrieval_gate,
        test_action_execution_triggers_on_tool_gate,
        test_action_execution_produces_blocker_when_audit_logging_missing,
        test_action_execution_no_blocker_when_audit_logging_confirmed,
        test_autonomy_pack_does_not_trigger_without_verified_action_capability,
        test_autonomy_pack_triggers_only_alongside_action_execution,
        test_vendor_platform_triggers_on_delivery_model,
        test_no_client_regulated_impact_pack_exists,
        test_scenario_agentforce_bounded_workflow_exact_packs,
        test_scenario_servicenow_autonomous_triage_exact_packs,
        test_scenario_servicenow_scheduled_trigger_alone_does_not_trigger_autonomy,
        test_every_triggered_pack_maps_to_at_least_one_dimension,
        test_every_pack_maps_to_exactly_five_dimensions,
        test_key_questions_are_reference_only_not_computed,
        test_required_actions_derived_from_governance_actions,
        test_governance_actions_carry_priority,
        test_not_triggered_packs_have_triggered_false,
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
