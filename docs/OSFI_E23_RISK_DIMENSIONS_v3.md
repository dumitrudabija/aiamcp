# OSFI E-23 Risk Dimensions Framework v3.0

## Overview

This document describes the new 6-dimension risk assessment framework for OSFI E-23 Model Risk Management, introduced in version 3.0.

**Key Changes from v2.x:**
- Replaced 13 binary indicators (5 quantitative + 8 qualitative) with 6 comprehensive Risk Dimensions
- Each dimension contains multiple factors with 4-level scales (Low/Medium/High/Critical)
- 31 total factors across 6 dimensions provide more granular assessment
- Dimensions map directly to lifecycle stage requirements

## The 6 Risk Dimensions

### 1. Misuse & Unintended Harm Potential
**Core Question:** Can the model be used in ways that cause harm beyond its intended purpose?

| Type | Factor | Low | Medium | High | Critical |
|------|--------|-----|--------|------|----------|
| Quantitative | Financial exposure if misused | <$1M | $1-10M | $10-100M | >$100M |
| Quantitative | Decisions influenced annually | <1,000 | 1K-50K | 50K-500K | >500K |
| Qualitative | Scope expansion potential | Tightly constrained | Limited secondary | Multiple uses | Broad applicability |
| Qualitative | Reversibility of decisions | Easily reversed | Reversible w/effort | Difficult | Irreversible |

### 2. Output Reliability & Integrity
**Core Question:** How trustworthy and consistent are the model's outputs?

| Type | Factor | Low | Medium | High | Critical |
|------|--------|-----|--------|------|----------|
| Quantitative | Error rate | <1% | 1-5% | 5-10% | >10% |
| Quantitative | Output consistency | >99% | 95-99% | 90-95% | <90% |
| Quantitative | Monthly drift | <2% | 2-5% | 5-10% | >10% |
| Qualitative | Explainability | Fully | Mostly | Partially | Black box |
| Qualitative | Edge cases documented | Comprehensive | Most identified | Some gaps | Significant unknowns |

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

### 5. Model Complexity & Opacity
**Core Question:** How complex is the model and how well can it be understood?

| Type | Factor | Low | Medium | High | Critical |
|------|--------|-----|--------|------|----------|
| Quantitative | Features/parameters | <50 | 50-500 | 500-10K | >10K |
| Quantitative | Training data volume | <100K | 100K-1M | 1M-100M | >100M |
| Qualitative | Model type | Linear/rules | Ensemble | Neural network | Deep learning/LLM |
| Qualitative | Autonomy level | None | Recommends | Auto w/override | Fully autonomous |
| Qualitative | Self-learning | Static | Periodic retrain | Continuous | Autonomous adaptation |

### 6. Governance & Oversight
**Core Question:** How robust are the controls and accountability structures?

| Type | Factor | Low | Medium | High | Critical |
|------|--------|-----|--------|------|----------|
| Quantitative | Override rate | N/A | <5% | 5-20% | >20% |
| Quantitative | Time since validation | <6 mo | 6-12 mo | 12-24 mo | >24 mo |
| Qualitative | Human review | All reviewed | Sample | Exception-based | None |
| Qualitative | Regulatory scrutiny | None | Low | Moderate | High (SR 11-7) |
| Qualitative | Model ownership | Clear single | Shared | Unclear | None assigned |

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

## File Structure

```
osfi_e23_risk_dimensions.py     # Core dimension definitions and helpers
osfi_e23_structure.py           # Lifecycle mapping and requirements
osfi_e23_processor.py           # Assessment logic (legacy + v3.0)
```

## Usage

### Getting Dimension Information
```python
from osfi_e23_processor import OSFIE23Processor

processor = OSFIE23Processor()

# Get all dimensions
dims = processor.get_risk_dimensions()

# Get specific dimension
dim = processor.get_dimension_info("fairness_customer_impact")
print(dim["core_question"])
```

### Creating an Assessment
```python
# Create empty assessment structure
assessment = processor.create_dimension_assessment()

# Assess a dimension with factor values
factor_values = {
    "financial_exposure": 5_000_000,  # $5M
    "decision_volume": 100_000,       # 100K decisions
    "scope_expansion": "medium",
    "reversibility": "high"
}
result = processor.assess_dimension("misuse_unintended_harm", factor_values)
print(f"Dimension risk: {result['risk_level']}")
```

### Getting Lifecycle Requirements
```python
# Get requirements for a dimension at a stage
reqs = processor.get_dimension_lifecycle_requirements("fairness_customer_impact", "design")
print(reqs["requirements"])

# Get all dimension requirements for a stage
all_reqs = processor.get_all_lifecycle_requirements_for_stage("deployment")
```

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

## Migration from v2.x

The v2.x indicator-based assessment (`_analyze_risk_factors`) is preserved for backward compatibility. The new dimension-based methods can be used alongside or as a replacement:

| v2.x Method | v3.0 Equivalent |
|-------------|-----------------|
| `_analyze_risk_factors()` | `assess_dimension()` per dimension |
| `_calculate_risk_score()` | `calculate_overall_risk()` |
| 13 boolean indicators | 31 leveled factors |

## Detection Logic (TODO)

The current implementation requires explicit factor values. Intelligent detection from project descriptions will be implemented as a separate enhancement to address:

1. **Context-aware detection** - Understanding negation ("not millions" vs "millions")
2. **Numeric extraction** - Parsing actual values from text
3. **Semantic matching** - Mapping descriptions to qualitative levels

See discussion in project documentation for detection strategy.
