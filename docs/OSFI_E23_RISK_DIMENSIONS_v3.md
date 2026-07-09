# OSFI E-23 Risk Dimensions Framework v3.4

## Overview

This document describes the risk assessment framework for OSFI E-23 Model Risk Management: 8 Risk Dimensions containing 47 factors, introduced as 6 dimensions/31 factors in v3.0 and expanded to 8 dimensions/47 factors in v3.4 (Data Provenance & Supply Chain Risk, Systemic & Concentration Risk, and 9 new factors folded into the original six). In v3.5, a separate non-scored **Model Type & Delivery Model Classification** layer was added (see below) - 4 factors that overlapped with it (`ai_system_classification`, `genai_scope_constraint`, `automation_bias_dependency`, `kill_switch_circuit_breaker`) were retired and replaced with 4 factors that measure something distinct, keeping the total at 47. The `Model type` factor in Complexity & Opacity was renamed to `Model architecture type` to avoid confusion with the new top-level model type classification.

**Key characteristics:**
- Each dimension contains multiple factors with 4-level scales (Low/Medium/High/Critical)
- 47 total factors across 8 dimensions provide granular assessment
- Two sentinel values beyond the 4 risk levels: `NOT_STATED` (missing evidence, defaults to Medium) and, for select factors, `NOT_APPLICABLE` (scores Low) or `PORTFOLIO_REVIEW_REQUIRED` (excluded from scoring, flagged for follow-up)
- Dimensions map to lifecycle stage requirements via `osfi_e23_structure.py`'s risk-scaled requirement tables

## The 8 Risk Dimensions

### 1. Misuse & Unintended Harm Potential
**Core Question:** Can the model be used in ways that cause harm beyond its intended purpose?

| Type | Factor | Low | Medium | High | Critical |
|------|--------|-----|--------|------|----------|
| Quantitative | Financial exposure if misused | <$1M | $1-10M | $10-100M | >$100M |
| Quantitative | Decisions influenced annually | <1,000 | 1K-50K | 50K-500K | >500K |
| Qualitative | Scope expansion potential | Tightly constrained | Limited secondary | Multiple uses | Broad applicability |
| Qualitative | Reversibility of decisions | Easily reversed | Reversible w/effort | Difficult | Irreversible |
| Qualitative | Confabulation / false-authority risk (GenAI) *(supports N/A)* | Grounded/cited, or non-generative | Occasional unsupported claims | Frequent unverifiable outputs | No fact-checking safeguard |

### 2. Output Reliability & Integrity
**Core Question:** How trustworthy and consistent are the model's outputs?

| Type | Factor | Low | Medium | High | Critical |
|------|--------|-----|--------|------|----------|
| Quantitative | Error rate | <1% | 1-5% | 5-10% | >10% |
| Quantitative | Output consistency | >99% | 95-99% | 90-95% | <90% |
| Quantitative | Monthly drift | <2% | 2-5% | 5-10% | >10% |
| Qualitative | Explainability | Fully | Mostly | Partially | Black box |
| Qualitative | Edge cases documented | Comprehensive | Most identified | Some gaps | Significant unknowns |
| Qualitative | GenAI output quality benchmark *(supports N/A)* | Benchmarked with documented results, or non-generative | Some benchmarking | Limited/informal | None performed |

### 3. Fairness & Customer Impact
**Core Question:** Does the model produce equitable outcomes? What's the impact on customers?

| Type | Factor | Low | Medium | High | Critical |
|------|--------|-----|--------|------|----------|
| Quantitative | Disparate impact ratio | >0.9 | 0.8-0.9 | 0.7-0.8 | <0.7 |
| Quantitative | Customer complaints | <0.1% | 0.1-0.5% | 0.5-2% | >2% |
| Quantitative | Population affected | <10K | 10K-100K | 100K-1M | >1M |
| Qualitative | Decision type | Informational | Influences | Significant factor | Sole determinant |
| Qualitative | Adverse action severity | Minor inconvenience | Moderate | Significant harm | Severe/irreversible |
| Qualitative | Vulnerable population | None | Limited | Moderate | Significant |
| Qualitative | Pre-deployment fairness / bias testing | Comprehensive & documented | Some testing, gaps remain | Limited/ad hoc | None conducted |

### 4. Operational & Security Risk
**Core Question:** What are the infrastructure, availability, and security risks?

| Type | Factor | Low | Medium | High | Critical |
|------|--------|-----|--------|------|----------|
| Quantitative | Uptime requirement | <95% | 95-99% | 99-99.9% | >99.9% |
| Quantitative | Recovery time objective | >24h | 4-24h | 1-4h | <1h |
| Quantitative | Third-party dependencies | 0-1 | 2-3 | 4-6 | >6 |
| Qualitative | Data sensitivity | Public | Internal | Confidential | PII/regulated |
| Qualitative | Attack surface | Internal only | Limited external | Broad external | Public-facing |
| Qualitative | Fallback available | Full backup | Partial | Limited | None |
| Qualitative | Adversarial robustness / prompt-injection testing *(supports N/A)* | Tested with mitigations, or not applicable | Some testing | Limited testing | None conducted for exposed system |

### 5. Model Complexity & Opacity
**Core Question:** How complex is the model and how well can it be understood?

| Type | Factor | Low | Medium | High | Critical |
|------|--------|-----|--------|------|----------|
| Quantitative | Features/parameters | <50 | 50-500 | 500-10K | >10K |
| Quantitative | Training data volume | <100K | 100K-1M | 1M-100M | >100M |
| Qualitative | Model architecture type | Linear/rules | Ensemble | Neural network | Deep learning/LLM |
| Qualitative | Autonomy level | None | Recommends | Auto w/override | Fully autonomous |
| Qualitative | Self-learning | Static | Periodic retrain | Continuous | Autonomous adaptation |
| Qualitative | Decision path traceability | Full lineage/audit trail | Traceable w/effort | Difficult to trace | Fully opaque |
| Qualitative | Pipeline component count | Single component | 2-3 chained | 4-6 chained | 7+ chained/undocumented |
| Qualitative | Model / configuration update velocity | Infrequent, scheduled, controlled | Periodic, controlled | Frequent or partly uncontrolled | Continuous/automatic, no release process |

*(v3.5, see below)* Model capability (traditional ML vs GenAI vs agentic) and delivery model (internal/vendor/embedded) are now captured as a separate, non-scored classification layer (`model_type_classification.py`) rather than as scored factors here - see "Model Type & Delivery Model Classification (v3.5)" below. The former `AI system classification (routing gate)`, `GenAI scope constraint`, and `Automation bias / cognitive dependency` factors were retired from this dimension's scored factors and replaced by the three traceability/complexity factors above, which measure something the new classification layer doesn't.

### 6. Governance & Oversight
**Core Question:** How robust are the controls and accountability structures?

| Type | Factor | Low | Medium | High | Critical |
|------|--------|-----|--------|------|----------|
| Quantitative | Override rate *(supports N/A)* | N/A | <5% | 5-20% | >20% |
| Quantitative | Time since validation | <6 mo | 6-12 mo | 12-24 mo | >24 mo |
| Qualitative | Human review | All reviewed | Sample | Exception-based | None |
| Qualitative | Regulatory scrutiny | None | Low | Moderate | High (SR 11-7) |
| Qualitative | Model ownership | Clear single | Shared | Unclear | None assigned |
| Qualitative | AI-specific incident response | Documented, tested, current | Exists, not AI-specific/tested | Informal/incomplete | None |
| Qualitative | Production monitoring & alerting coverage | Active monitoring/alerting, defined thresholds | Monitoring exists, alerting gaps | Largely manual/ad hoc | None |

The former `Kill switch / circuit breaker` factor was retired from this dimension's scored factors (v3.5) - it's now covered by the Agentic Autonomy conditional module's governance conditions instead, alongside the new model type classification.

### 7. Data Provenance & Supply Chain Risk *(new in v3.4)*
**Core Question:** Are the model's data, training inputs, fine-tuning data, validation data, RAG grounding sources, third-party components, and synthetic data understood, approved, traceable, and controlled?

| Type | Factor | Low | Medium | High | Critical |
|------|--------|-----|--------|------|----------|
| Qualitative | Training data documentation | Fully documented (source, owner, lineage, limitations) | Most sources documented, some metadata gaps | Partially documented, key gaps | Undocumented/unknown/untraceable |
| Qualitative | PII in training or context data | Documented, controlled, tested for leakage | Documented/controlled, testing incomplete | Present, controls/testing incomplete | Known/likely exposure, no controls |
| Qualitative | Third-party / open-source component integrity | All material components approved, versioned, monitored | Most approved/monitored, non-critical gaps | Material dependencies with incomplete approval | Critical components unapproved/unverified/unsupported |
| Qualitative | Synthetic data quality *(supports N/A)* | Not used, or fully validated | Used, partially validated | Used materially, weak validation | Used materially, no validation/known issues |

### 8. Systemic & Concentration Risk *(new in v3.4)*
**Core Question:** Do risks exist that are not fully visible when assessing one model in isolation, because many models, processes, or controls depend on the same cloud provider, AI platform, foundation model, data provider, or vendor?

| Type | Factor | Low | Medium | High | Critical |
|------|--------|-----|--------|------|----------|
| Qualitative | Infrastructure concentration | Resilient, substitutable, tested | Some concentration, documented recovery plan | Single dependency, untested substitution | Non-substitutable, would stop a critical process |
| Qualitative | Foundation model / vendor concentration | Documented, version-controlled, substitutable | Documented/monitored, incomplete substitution controls | Common vendor, weak substitution/update controls | Critical function, no substitution/version plan |
| Qualitative | Portfolio-level AI estate concentration *(supports Portfolio Review Required)* | No material concentration, or actively mitigated | Some concentration, documented/monitored | Material share of important functions, incomplete mitigation | Material share of critical functions, no mitigation |

`portfolio_level_ai_estate_concentration` requires institution-wide model inventory data that a single project description cannot provide. When that data is unavailable, the factor is **not** defaulted to Medium and does **not** count toward Dimension 8's average - it is excluded from scoring and surfaced in a `follow_up_actions` list (see "Sentinel Values" below), so the rest of the model-level assessment isn't blocked.

## Model Type Classification & Delivery Model (v3.5-v3.8)

A second, orthogonal, **non-scored** layer sits alongside the 8 dimensions above (`model_type_classification.py`, `conditional_modules.py`), orchestrated by a **mandatory five-step workflow** (`osfi_e23_workflow.py`, v3.6) that runs in this exact order and cannot be bypassed:

1. **Model type identification** - classify capability level + delivery model.
2. **Capability Evidence Pack triggers** - evaluated **before** the 47-question assessment runs (not a post-report add-on).
3. **Existing 47-question assessment** - unchanged questions/dimensions/scoring; produces the base risk score/level.
4. **Risk level + conditions** - Capability Evidence Pack findings qualify the base result with conditions/blockers/evidence gaps (never an independent score - `final_risk_level` always equals `base_risk_level`).
5. **Required governance actions** - categorized action list (Documentation, Validation, Security/access controls, Vendor assurance, Monitoring, Human oversight, Approval, Issue remediation, Model inventory update, Workflow/ticket creation) derived from steps 1-4.

Each step guards that all of its prerequisites completed (`AssessmentWorkflowContext.require_all_prior_completed`), raising `WorkflowOrderError` naming the earliest missing step if attempted out of order - e.g. running step 3 with nothing done yet reports `model_type_identification`, not step 2. Rendered in the report per `osfi_e23_report_generators.py`'s current structure (v4.2): model type classification in Section 1.2 / 2.2 / Annex E, Capability Evidence Pack results in Section 2.5, and required governance actions in Section 3.3 - see "OSFI E-23 Report Structure (v4.2)" in `CLAUDE.md` for the full section/annex map.

**Core rule**: classification is based on objective, verifiable **capability gates**, not marketing labels. Product names/labels ("agent", "copilot", "assistant", "autonomous", "workflow", "Agentforce", "ServiceNow") are candidate signals only - Claude extracts factual yes/no/short-text evidence in the same extraction pass as the 47 factors, but deterministic server-side logic (not Claude) decides gate `verified` status and the final level.

**Critical distinction (v3.7, hardened)**: automated execution (a predefined workflow/batch job/rule/schedule/trigger executing a predetermined action) is NOT the same as autonomous agentic decision-making (the AI deciding WHETHER to act, WHAT action to take, and/or WHAT SEQUENCE of actions to pursue toward a goal). A system is never promoted to Level 5 solely because it runs on a schedule, is event-triggered, processes records in batch, auto-approves a predefined decision, applies a threshold rule, executes a fixed workflow, has no human review per transaction, or changes a system of record via predefined logic - those are Action Execution Pack / governance territory, not proof of autonomy.

- **4 promotion gates**, each with `verified` (bool), `evidence` (list of cited fields), `missing_evidence` (list), and `rationale`:
  1. `genai_generation` = `uses_llm_or_generative_ai == yes`.
  2. `runtime_retrieval` = `genai_generation.verified AND uses_runtime_retrieval_for_genai_grounding == yes`. Traditional-ML feature retrieval, DB lookups, or batch ETL (`retrieves_data_for_features_or_batch_processing`) never count, even without GenAI.
  3. `tool_or_action_execution` = `model_output_changes_system_state == yes OR ai_selects_tool_or_action == yes OR predefined_workflow_triggered_by_model_output == yes`. This can verify for a pure traditional-ML model with no GenAI at all (e.g. a credit-line auto-update rule), promoting it straight to Level 4.
  4. `autonomous_operation` = `tool_or_action_execution.verified AND ai_decides_to_act_or_continue == yes AND at least one of` {`ai_selects_tool_or_action`, `ai_selects_next_step`, `has_dynamic_multi_step_planning`, `has_goal_pursuit`, `has_looping_or_retry_based_on_outcomes`, `has_memory_or_state_driven_continuation`, `has_delegation_to_other_agents`, `has_adaptive_plan_revision`} `== yes`. The `ai_decides_to_act_or_continue` conjunct is the key differentiator - `runs_on_schedule_or_event_trigger` and `requires_human_approval_per_action == no` are explicitly insufficient on their own to satisfy it, and the classifier records that reasoning verbatim in the gate's rationale when they're the only signals present.
- **Sequential promotion**: Level 1 (default) -> 2 if `genai_generation` verified -> 3 if `runtime_retrieval` verified -> 4 if `tool_or_action_execution` verified -> **5 only if `autonomous_operation` is verified** (which itself already requires `tool_or_action_execution.verified` as one of its three conjuncts - there is no way to reach Level 5 without verified action execution). A model can jump levels (e.g. GenAI + AI-selected tool execution with no retrieval = Level 4 directly).
- **Confidence** (`high`/`medium`/`low`) is computed per gate and overall: `high` requires the deciding evidence to be both explicit and backed by a concrete/named detail (e.g. a specific vendor product); `low` covers incomplete, ambiguous, or label-only evidence (e.g. a system merely described as an "AI agent" with no capability confirmation never promotes above Level 1, and confidence is `low`).
- **Rationale requirements**: every classification states the final level/label, verified gates, evidence used, missing evidence, and an explicit reason Level 5 was or wasn't reached. Level 5 rationale additionally covers the goal/task pursued, how the AI decides to act/continue, what actions/tools it chooses among, and its sequencing/revision/retry/delegation/escalation capability and guardrails. Non-Level-5 systems with automation get rationale stating what's automated, whether it's predefined, whether the AI has discretion over the next action/continuation, and why the system isn't autonomous.
- **Delivery model** (`internal_build` / `vendor_platform` / `embedded_saas_ai` / `unknown`) is classified independently of capability level - the same vendor product (e.g. Agentforce, ServiceNow) can be Level 2 through 5 depending on what's actually enabled, while delivery model only reflects who hosts/controls the underlying model.
- **Exactly 4 Capability Evidence Packs** (Knowledge Access, Action Execution, Autonomy, Vendor / Platform - **Client/Regulated Impact is intentionally not a 5th pack**; client impact stays within the 47 questions and governance escalation logic) trigger deterministically off the promotion gates' `verified` flags and delivery model, surfacing evidence gaps, blockers, `governance_conditions`, `governance_actions` (with `priority`), and findings mapped to exactly **5 of the 8** dimensions each (a `risk_dimension_mapping_notes` string explains why). They never produce an independent score. Blockers arise from missing supplementary evidence (e.g. Action Execution Pack + no confirmed audit logging = production blocker).
  - **Trigger conditions (v3.8)**: Knowledge Access = `runtime_retrieval.verified`. Action Execution = `tool_or_action_execution.verified` (widened to OR in `system_of_record_write_permission`, `model_output_initiates_external_communication`, `model_output_triggers_transaction_or_approval` alongside the original 3 signals). Autonomy = `autonomous_operation.verified` (can never trigger without Action Execution, per the gate formula). Vendor/Platform = `delivery_model.label in (vendor_platform, embedded_saas_ai)` **OR** any of `vendor_controls_model_runtime`, `vendor_controls_model_updates`, `vendor_hosts_customer_or_sensitive_data`, `vendor_provides_foundation_model_or_agent_platform` == yes (widening the pack's own trigger predicate, not the 4-value delivery-model taxonomy itself).
  - **`key_questions` (v3.8, 12 per pack, 48 total)**: a static reference/follow-up checklist (question, expected evidence/control, condition-if-missing, a stated default `blocker_if_missing`, and full blocker guidance text) rendered under each *triggered* pack. These are **not extracted from the project description or verified by this tool** - external/operational control evidence (vendor contracts, tested kill switches, audit rights, etc.) would never appear in a project description. `evidence_status` is uniformly `not_verified` with a note to confirm with the accountable control owner internally.
  - **Governance action schema (v3.8)**: `{category, action, source_pack, priority (blocker/high/medium/low), owner: "TBD", due_stage}`. Priority is set at the pack level (blocker-linked conditions get `"blocker"`, other pack conditions get `"high"`) and for baseline workflow actions (Approval/Model inventory update/Documentation get `"medium"`; Issue remediation for blockers gets `"blocker"`).
- Rendered in the report (v4.2) as: Section 1.2 Model Classification Summary + Annex E Detailed Model Type Classification Evidence (model type/delivery model - never called "promotion gates" in report text, since that reads as OSFI E-23 lifecycle-stage approval, which this is not), Section 2.5 Capability Evidence Pack Results (incl. the key_questions reference table per triggered pack, rendered as a "Required Action" column rather than exposing the internal blocker/condition fields), and Section 3.3 Required Actions (merged base-risk/pack/evidence-gap actions, sorted by priority - the internal `"blocker"` priority value displays as "Critical", never as "Blocker") - all optional via `include_model_type_section`/`include_conditional_modules_section`, default on. The report never surfaces `final_status`/blocker/condition/readiness as first-class concepts; only evidence gaps, required actions, and required validation (see `osfi_e23_report_generators.py`).

## Sentinel Values

Beyond the four risk levels, the extraction/scoring pipeline recognizes:

| Sentinel | Meaning | Scoring effect | Applies to |
|---|---|---|---|
| `NOT_STATED` | Information not found in the project description | Defaults to Medium risk (score=2); counted in the dimension average; tracked in `not_stated_summary` | Any factor |
| `NOT_APPLICABLE` | The factor genuinely does not apply to this system | Scores as Low (or a factor-specific `na_risk_level`); counted in the dimension average; tracked via `is_not_applicable` | Factors with `allow_na: True` (currently: `confabulation_false_authority`, `genai_output_quality_benchmark`, `adversarial_robustness_testing`, `override_rate`, `synthetic_data_quality`). Note: prior to v3.5, `override_rate` (the only *quantitative* factor with `allow_na`) crashed on `NOT_APPLICABLE` since only the qualitative scorer checked for the sentinel - fixed in `score_factor()` to check centrally for both factor types. |
| `PORTFOLIO_REVIEW_REQUIRED` | Institution-wide inventory data needed to answer is unavailable | Excluded entirely from the dimension average; tracked in `follow_up_actions` | Only `portfolio_level_ai_estate_concentration` (`allow_review_required: True`) |

## Dimension × Lifecycle Matrix

Each dimension has specific requirements at each lifecycle stage:

| Dimension | Design | Review | Deployment | Monitoring | Decommission |
|-----------|--------|--------|------------|------------|--------------|
| Misuse & Harm | Document scope | Validate boundaries | Access controls | Track usage | Verify no residuals |
| Reliability | Define criteria | Test performance | Production validation | Drift monitoring | Retain records |
| Fairness | Assess bias | Test fairness | Appeal mechanisms | Monitor disparate impact | Document outcomes |
| Operations | Identify dependencies | Security review | Implement controls | System health | Secure teardown |
| Complexity | Document methodology | Validate soundness | Version controls | Track drift | Archive artifacts |
| Governance | Assign ownership | Independent review | Activate controls | Track overrides | Close accountabilities |
| Data Provenance & Supply Chain | Document data/component sources | Validate provenance & approvals | Confirm versioning/monitoring | Track vendor changes | Archive provenance records |
| Systemic & Concentration | Identify concentration points | Assess substitution plans | Confirm failover readiness | Monitor vendor/platform health | Verify no orphaned dependencies |

## File Structure

```
osfi_e23_risk_dimensions.py     # Dimension/factor definitions (RISK_DIMENSIONS, DIMENSION_ORDER)
osfi_e23_structure.py           # Lifecycle mapping and risk-scaled requirements
risk_dimension_extraction.py    # Extraction prompt generation + deterministic scoring (live pipeline)
osfi_e23_processor.py           # Governance requirement / compliance recommendation generation
```

## Usage

The live scoring pipeline is a two-phase extraction workflow, not direct factor-value input. See `risk_dimension_extraction.py`:

```python
from risk_dimension_extraction import (
    get_extraction_prompt_for_description,
    process_extraction_response
)

# Phase 1: Generate an extraction prompt for Claude to analyze a project description
extraction_data = get_extraction_prompt_for_description(project_description)
# extraction_data["extraction_prompt"] is sent to Claude, which returns a JSON
# object mapping each of the 47 factor IDs to an extracted value + evidence quote.

# Phase 2: Score the extracted JSON deterministically
result = process_extraction_response(extracted_json)
print(result["overall_assessment"]["overall_risk_level"])
print(result["dimension_scores"]["fairness_customer_impact"])
print(result["follow_up_actions"])  # any PORTFOLIO_REVIEW_REQUIRED factors
```

`server.py`'s `assess_model_risk` MCP tool wraps exactly this two-phase flow (see `_generate_extraction_phase` / `_assess_with_extracted_factors`).

## OSFI E-23 Alignment

This framework aligns with OSFI Guideline E-23 Principle 2.2:

> "The risk rating approach should be supported by clear, measurable criteria for each risk dimension and incorporate both quantitative and qualitative factors"

### Quantitative factors from OSFI E-23:
- Portfolio importance, size, and growth
- Potential operational, security, or financial impacts

### Qualitative factors from OSFI E-23:
- Business use or purpose
- Model complexity or level of autonomy
- Reliability of data inputs
- Customer impacts
- Regulatory risk

## Scoring Pipeline History

The pre-v3.1 direct-factor-value API (`OSFIE23Processor.assess_dimension()`, `.calculate_overall_risk()`, and the original keyword-indicator-based `.assess_model_risk()`) was superseded by the two-phase extraction pipeline in `risk_dimension_extraction.py` (v3.1+) and removed as dead code in v3.4, since the MCP tool dispatch never called them. `OSFIE23Processor` now only generates governance requirements and compliance recommendations from an already-computed risk level; all factor/dimension/overall scoring lives in `risk_dimension_extraction.py`.
