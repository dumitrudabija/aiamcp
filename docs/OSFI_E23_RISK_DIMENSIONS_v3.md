# OSFI E-23 Risk Dimensions Framework v3.4

## Overview

This document describes the risk assessment framework for OSFI E-23 Model Risk Management: 8 Risk Dimensions containing 47 factors, introduced as 6 dimensions/31 factors in v3.0 and expanded to 8 dimensions/47 factors in v3.4 (Data Provenance & Supply Chain Risk, Systemic & Concentration Risk, and 9 new factors folded into the original six).

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
| Qualitative | Model type | Linear/rules | Ensemble | Neural network | Deep learning/LLM |
| Qualitative | Autonomy level | None | Recommends | Auto w/override | Fully autonomous |
| Qualitative | Self-learning | Static | Periodic retrain | Continuous | Autonomous adaptation |
| Qualitative | AI system classification (routing gate) | Traditional ML, non-generative | Narrow-purpose GenAI | Broad-purpose GenAI | Autonomous/agentic AI |
| Qualitative | GenAI scope constraint *(supports N/A)* | Tightly constrained, or non-generative | Some constraints, gaps | Limited constraints | No constraints (open-ended) |
| Qualitative | Automation bias / cognitive dependency | Low reliance, critical evaluation | Some reliance | Significant reliance | Routine deference, no verification |

The **AI system classification** factor is a "routing gate": its value gives context for whether the GenAI-conditional factors above (confabulation risk, GenAI output benchmark, adversarial robustness testing, GenAI scope constraint) are applicable to a given model. There is no automatic code-side gating - the LLM extraction step uses this classification as context to decide whether to answer those factors normally or mark them `NOT_APPLICABLE`; the deterministic scorer just needs to accept that sentinel on factors that declare `allow_na: True`.

### 6. Governance & Oversight
**Core Question:** How robust are the controls and accountability structures?

| Type | Factor | Low | Medium | High | Critical |
|------|--------|-----|--------|------|----------|
| Quantitative | Override rate | N/A | <5% | 5-20% | >20% |
| Quantitative | Time since validation | <6 mo | 6-12 mo | 12-24 mo | >24 mo |
| Qualitative | Human review | All reviewed | Sample | Exception-based | None |
| Qualitative | Regulatory scrutiny | None | Low | Moderate | High (SR 11-7) |
| Qualitative | Model ownership | Clear single | Shared | Unclear | None assigned |
| Qualitative | AI-specific incident response | Documented, tested, current | Exists, not AI-specific/tested | Informal/incomplete | None |
| Qualitative | Kill switch / circuit breaker | Tested capability exists | Exists, untested/partial | Limited ability | None |

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

## Sentinel Values

Beyond the four risk levels, the extraction/scoring pipeline recognizes:

| Sentinel | Meaning | Scoring effect | Applies to |
|---|---|---|---|
| `NOT_STATED` | Information not found in the project description | Defaults to Medium risk (score=2); counted in the dimension average; tracked in `not_stated_summary` | Any factor |
| `NOT_APPLICABLE` | The factor genuinely does not apply to this system | Scores as Low (or a factor-specific `na_risk_level`); counted in the dimension average; tracked via `is_not_applicable` | Factors with `allow_na: True` (currently: `synthetic_data_quality`, `confabulation_false_authority`, `genai_output_quality_benchmark`, `adversarial_robustness_testing`, `genai_scope_constraint`) |
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
