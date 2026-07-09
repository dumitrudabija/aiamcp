#!/usr/bin/env python3
"""
Unit tests for model_type_classification.py - deterministic capability-gate
classification. Pure logic, no server/MCP dependency.

Includes the 8 required test cases distinguishing automated execution from
autonomous agentic decision-making (Tests 1-8), plus delivery model and
determinism coverage.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from model_type_classification import (
    classify_model_type,
    classify_delivery_model,
    validate_model_type_evidence,
)


def _evidence(**overrides):
    return validate_model_type_evidence(overrides)


# =============================================================================
# Required Test 1-8 scenarios
# =============================================================================

def test_1_traditional_scorecard_no_action():
    """Logistic regression scorecard, no direct system action."""
    evidence = _evidence(uses_traditional_ml_or_statistical_model="yes")
    result = classify_model_type(evidence)
    assert result["final_level"] == 1
    assert result["promotion_gates"]["tool_or_action_execution"]["verified"] is False
    assert result["promotion_gates"]["autonomous_operation"]["verified"] is False
    print("PASS: (1) traditional scorecard with no action classifies as Level 1, no Action/Autonomy gates verified")


def test_2_traditional_ml_scheduled_batch_scoring():
    """XGBoost monthly batch rescoring, output reviewed by analysts, no direct system action."""
    evidence = _evidence(
        uses_traditional_ml_or_statistical_model="yes",
        runs_on_schedule_or_event_trigger="yes",
    )
    result = classify_model_type(evidence)
    assert result["final_level"] == 1
    assert result["promotion_gates"]["autonomous_operation"]["verified"] is False
    assert "Scheduled or event-triggered automation does not by itself establish autonomous agentic decision-making." in result["promotion_gates"]["autonomous_operation"]["rationale"]
    print("PASS: (2) scheduled batch scoring stays Level 1; rationale states scheduled automation is not autonomous agency")


def test_3_traditional_ml_fixed_auto_update():
    """XGBoost credit line model auto-updates on threshold - action execution, not autonomy."""
    evidence = _evidence(
        uses_traditional_ml_or_statistical_model="yes",
        predefined_workflow_triggered_by_model_output="yes",
    )
    result = classify_model_type(evidence)
    assert result["final_level"] == 4
    assert result["promotion_gates"]["tool_or_action_execution"]["verified"] is True
    assert result["promotion_gates"]["autonomous_operation"]["verified"] is False
    assert "Predefined downstream action execution is action execution, not autonomous agency." in result["promotion_gates"]["autonomous_operation"]["rationale"]
    print("PASS: (3) fixed threshold auto-update reaches Level 4 (Action Execution), not Level 5 (Autonomy)")


def test_4_genai_drafting_assistant():
    """LLM drafts customer email, human copies/sends, no retrieval, no action execution."""
    evidence = _evidence(uses_llm_or_generative_ai="yes")
    result = classify_model_type(evidence)
    assert result["final_level"] == 2
    assert result["promotion_gates"]["tool_or_action_execution"]["verified"] is False
    assert result["promotion_gates"]["autonomous_operation"]["verified"] is False
    print("PASS: (4) GenAI drafting assistant with no retrieval/action classifies as Level 2")


def test_5_rag_chatbot():
    """LLM + vector store + SharePoint retrieval + citations, no actions."""
    evidence = _evidence(
        uses_llm_or_generative_ai="yes",
        uses_runtime_retrieval_for_genai_grounding="yes",
    )
    result = classify_model_type(evidence)
    assert result["final_level"] == 3
    assert result["promotion_gates"]["tool_or_action_execution"]["verified"] is False
    assert result["promotion_gates"]["autonomous_operation"]["verified"] is False
    print("PASS: (5) RAG chatbot classifies as Level 3")


def test_6_genai_tool_calling_human_initiated():
    """LLM + function calling, AI selects case-update API, human starts session, no continuation."""
    evidence = _evidence(
        uses_llm_or_generative_ai="yes",
        ai_selects_tool_or_action="yes",
        requires_human_approval_per_action="yes",
    )
    result = classify_model_type(evidence)
    assert result["final_level"] == 4
    assert result["promotion_gates"]["tool_or_action_execution"]["verified"] is True
    assert result["promotion_gates"]["autonomous_operation"]["verified"] is False
    print("PASS: (6) human-initiated GenAI tool-calling workflow reaches Level 4, not Level 5")


def test_7_autonomous_incident_agent():
    """AI decides whether to run diagnostics, selects tools, revises plan, escalates if unresolved."""
    evidence = _evidence(
        uses_llm_or_generative_ai="yes",
        ai_selects_tool_or_action="yes",
        ai_decides_to_act_or_continue="yes",
        has_adaptive_plan_revision="yes",
        runs_on_schedule_or_event_trigger="yes",
    )
    result = classify_model_type(evidence)
    assert result["final_level"] == 5
    assert result["promotion_gates"]["tool_or_action_execution"]["verified"] is True
    assert result["promotion_gates"]["autonomous_operation"]["verified"] is True
    assert "Level 5 (autonomous agent) reached" in result["rationale"]
    print("PASS: (7) autonomous incident agent (AI decides to act, selects tools, revises plan) reaches Level 5")


def test_8_product_label_only():
    """Product called 'AI agent', no evidence of tools/action selection/planning/continuation/goal pursuit."""
    evidence = _evidence(product_label_mentioned="AI agent")
    result = classify_model_type(evidence)
    assert result["final_level"] == 1
    assert result["confidence"] == "low"
    assert len(result["promotion_gates"]["tool_or_action_execution"]["missing_evidence"]) > 0
    assert "AI agent" in result["rationale"]
    print("PASS: (8) product label 'AI agent' alone does not promote; confidence is low; missing evidence recorded")


# =============================================================================
# Additional gate-formula coverage
# =============================================================================

def test_retrieval_without_genai_does_not_reach_level3():
    """Retrieval alone (no GenAI) must not count as RAG per the Level 3 definition."""
    evidence = _evidence(uses_llm_or_generative_ai="no", uses_runtime_retrieval_for_genai_grounding="yes")
    result = classify_model_type(evidence)
    assert result["final_level"] == 1, result
    assert result["promotion_gates"]["runtime_retrieval"]["verified"] is False
    print("PASS: retrieval without GenAI does not promote to Level 3")


def test_feature_or_batch_retrieval_does_not_count_as_rag():
    """Traditional ML feature retrieval/DB queries/batch ETL must not count as Level 3 retrieval."""
    evidence = _evidence(
        uses_llm_or_generative_ai="yes",
        retrieves_data_for_features_or_batch_processing="yes",
    )
    result = classify_model_type(evidence)
    assert result["final_level"] == 2, result
    assert result["promotion_gates"]["runtime_retrieval"]["verified"] is False
    print("PASS: feature/batch/ETL retrieval does not count as GenAI runtime retrieval (stays Level 2)")


def test_level4_can_jump_from_genai_without_rag():
    """Edge case: GenAI + AI-selected tool execution but no RAG = Level 4 (jumps over 3)."""
    evidence = _evidence(
        uses_llm_or_generative_ai="yes",
        ai_selects_tool_or_action="yes",
    )
    result = classify_model_type(evidence)
    assert result["final_level"] == 4, result
    print("PASS: GenAI + tool execution without RAG jumps straight to Level 4")


def test_model_output_changes_system_state_alone_reaches_level4_not_5():
    """Traditional ML model output directly changes system state -> Level 4, never auto to Level 5."""
    evidence = _evidence(
        uses_traditional_ml_or_statistical_model="yes",
        model_output_changes_system_state="yes",
    )
    result = classify_model_type(evidence)
    assert result["final_level"] == 4
    assert result["promotion_gates"]["autonomous_operation"]["verified"] is False
    print("PASS: model output directly changing system state reaches Level 4, not Level 5")


def test_level5_requires_ai_discretion_plus_agentic_capability_plus_action():
    """All 3 Level 5 conjuncts required: action execution, AI decides to act/continue, and >=1 agentic capability."""
    evidence = _evidence(
        ai_selects_tool_or_action="yes",
        ai_decides_to_act_or_continue="yes",
        has_goal_pursuit="yes",
    )
    result = classify_model_type(evidence)
    assert result["final_level"] == 5, result
    assert result["promotion_gates"]["tool_or_action_execution"]["verified"] is True
    assert result["promotion_gates"]["autonomous_operation"]["verified"] is True
    print("PASS: action execution + AI discretion + agentic capability together reach Level 5")


def test_schedule_trigger_alone_never_promotes_to_level5():
    """Explicit acceptance criterion: scheduled/event-triggered automation alone is never sufficient for Level 5."""
    evidence = _evidence(
        ai_selects_tool_or_action="yes",
        runs_on_schedule_or_event_trigger="yes",
        requires_human_approval_per_action="no",
        # ai_decides_to_act_or_continue deliberately NOT set
    )
    result = classify_model_type(evidence)
    assert result["final_level"] == 4, result
    assert result["promotion_gates"]["autonomous_operation"]["verified"] is False
    print("PASS: schedule/event trigger + no human review, without AI discretion, never promotes past Level 4")


def test_absence_of_human_review_alone_does_not_establish_autonomy():
    evidence = _evidence(
        ai_selects_tool_or_action="yes",
        requires_human_approval_per_action="no",
    )
    result = classify_model_type(evidence)
    assert result["promotion_gates"]["autonomous_operation"]["verified"] is False
    assert "Absence of human review per action is insufficient to establish autonomy" in result["promotion_gates"]["autonomous_operation"]["rationale"]
    print("PASS: absence of human review alone does not establish autonomy; explicit rationale recorded")


def test_agentic_capability_without_action_execution_is_evidence_gap_not_level5():
    """Agentic signals present without verified action capability must not promote to Level 5."""
    evidence = _evidence(
        uses_llm_or_generative_ai="yes",
        ai_decides_to_act_or_continue="yes",
        has_dynamic_multi_step_planning="yes",
    )
    result = classify_model_type(evidence)
    assert result["final_level"] == 2, result
    assert result["promotion_gates"]["autonomous_operation"]["verified"] is False
    assert any("tool_or_action_execution" in m for m in result["promotion_gates"]["autonomous_operation"]["missing_evidence"])
    print("PASS: agentic capability signals without verified action execution do not reach Level 5")


def test_vendor_labels_do_not_determine_classification():
    """Vendor product names must not directly gate model type level."""
    evidence_bounded = _evidence(
        vendor_product_named="Salesforce Agentforce",
        ai_selects_tool_or_action="yes",
        requires_human_approval_per_action="yes",
    )
    result_bounded = classify_model_type(evidence_bounded)
    assert result_bounded["final_level"] == 4

    evidence_autonomous = _evidence(
        vendor_product_named="Salesforce Agentforce",
        ai_selects_tool_or_action="yes",
        ai_decides_to_act_or_continue="yes",
        has_looping_or_retry_based_on_outcomes="yes",
    )
    result_autonomous = classify_model_type(evidence_autonomous)
    assert result_autonomous["final_level"] == 5

    print("PASS: same vendor product classifies at different levels depending on verified capability, not the label")


def test_deterministic_repeatable():
    """Same evidence must always produce the same final level."""
    evidence = _evidence(uses_llm_or_generative_ai="yes", uses_runtime_retrieval_for_genai_grounding="yes")
    results = [classify_model_type(evidence) for _ in range(5)]
    levels = {r["final_level"] for r in results}
    assert len(levels) == 1
    print("PASS: classification is deterministic and repeatable across repeated calls")


# =============================================================================
# Delivery model coverage (unchanged logic)
# =============================================================================

def test_delivery_model_vendor_platform_with_named_vendor():
    evidence = _evidence(vendor_product_named="Salesforce Agentforce")
    result = classify_delivery_model(evidence)
    assert result["label"] == "vendor_platform"
    assert result["confidence"] == "high"
    assert len(result["evidence"]) > 0
    print("PASS: named standalone vendor product classifies as vendor_platform with evidence recorded")


def test_delivery_model_embedded_saas_ai_with_copilot_name():
    evidence = _evidence(vendor_product_named="Microsoft 365 Copilot")
    result = classify_delivery_model(evidence)
    assert result["label"] == "embedded_saas_ai"
    print("PASS: 'Copilot'-named product classifies as embedded_saas_ai")


def test_delivery_model_unknown_when_no_evidence():
    evidence = _evidence()
    result = classify_delivery_model(evidence)
    assert result["label"] == "unknown"
    assert result["confidence"] == "low"
    assert len(result["missing_evidence"]) > 0
    print("PASS: no evidence yields unknown delivery model with missing evidence recorded")


def test_delivery_model_independent_of_capability_level():
    """Delivery model must not change capability level."""
    evidence = _evidence(
        vendor_product_named="ServiceNow",
        ai_selects_tool_or_action="yes",
        requires_human_approval_per_action="yes",
    )
    model_type = classify_model_type(evidence)
    delivery = classify_delivery_model(evidence)
    assert model_type["final_level"] == 4
    assert delivery["label"] == "vendor_platform"
    print("PASS: delivery model classified independently of capability level")


def test_validate_model_type_evidence_missing_key_degrades_safely():
    evidence = validate_model_type_evidence(None)
    yes_no_fields = [
        "uses_llm_or_generative_ai", "uses_traditional_ml_or_statistical_model",
        "uses_runtime_retrieval_for_genai_grounding", "ai_selects_tool_or_action",
        "has_dynamic_multi_step_planning", "ai_decides_to_act_or_continue",
    ]
    assert all(evidence[f] == "not_stated" for f in yes_no_fields)
    result = classify_model_type(evidence)
    assert result["final_level"] == 1
    print("PASS: missing model_type_evidence degrades safely to Level 1, no exception")


if __name__ == "__main__":
    tests = [
        test_1_traditional_scorecard_no_action,
        test_2_traditional_ml_scheduled_batch_scoring,
        test_3_traditional_ml_fixed_auto_update,
        test_4_genai_drafting_assistant,
        test_5_rag_chatbot,
        test_6_genai_tool_calling_human_initiated,
        test_7_autonomous_incident_agent,
        test_8_product_label_only,
        test_retrieval_without_genai_does_not_reach_level3,
        test_feature_or_batch_retrieval_does_not_count_as_rag,
        test_level4_can_jump_from_genai_without_rag,
        test_model_output_changes_system_state_alone_reaches_level4_not_5,
        test_level5_requires_ai_discretion_plus_agentic_capability_plus_action,
        test_schedule_trigger_alone_never_promotes_to_level5,
        test_absence_of_human_review_alone_does_not_establish_autonomy,
        test_agentic_capability_without_action_execution_is_evidence_gap_not_level5,
        test_vendor_labels_do_not_determine_classification,
        test_deterministic_repeatable,
        test_delivery_model_vendor_platform_with_named_vendor,
        test_delivery_model_embedded_saas_ai_with_copilot_name,
        test_delivery_model_unknown_when_no_evidence,
        test_delivery_model_independent_of_capability_level,
        test_validate_model_type_evidence_missing_key_degrades_safely,
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
