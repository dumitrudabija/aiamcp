# OSFI E-23 Tunable Parameters for Institutional Customization

This document identifies all interpretable/tunable elements in the OSFI E-23 implementation that can be adjusted to match specific institutional requirements.

## 1. Risk Scoring Weights

**Location:** `osfi_e23_processor.py:286-287`

```python
quantitative_score = sum(...) * 10  # Current: 10 points per factor
qualitative_score = sum(...) * 8    # Current: 8 points per factor
```

**Tunable:**
- Quantitative factor weight (currently 10 points each)
- Qualitative factor weight (currently 8 points each)
- Can be adjusted to institutional risk appetite (e.g., 12/6, 15/5, etc.)

**Impact:** Changes base risk scoring before amplification

---

## 2. Risk Amplification Factors

**Location:** `osfi_e23_processor.py:308-318` and `osfi_e23_processor.py:661-668`

```python
# AI/ML in financial decisions
if financial_impact + ai_ml_usage: +30%

# Autonomous customer-facing decisions
if customer_facing + autonomous_decisions: +20%

# Unexplainable models with regulatory impact
if black_box + regulatory_impact: +25%

# Third-party dependency in critical systems
if third_party + revenue_critical: +15%
```

**Tunable:**
- Each amplification percentage (currently 0.3, 0.2, 0.25, 0.15)
- Risk combination triggers (which factors trigger amplification)
- Can add new dangerous combinations

**Impact:** Adjusts final risk score for specific institutional concerns

---

## 3. Risk Level Thresholds

**Location:** `osfi_e23_processor.py:91-95`

```python
"risk_rating_levels": [
    {"level": "Low", "score_range": [0, 25]},
    {"level": "Medium", "score_range": [26, 50]},
    {"level": "High", "score_range": [51, 75]},
    {"level": "Critical", "score_range": [76, 100]}
]
```

**Tunable:**
- Score range boundaries for each risk level
- Number of risk levels (can add "Moderate", "Severe", etc.)
- Risk level names and descriptions

**Impact:** Changes governance requirements triggered by scores

---

## 4. Risk Factor Categories (Structure)

**Location:** `osfi_e23_processor.py:265-283`

### Current Implementation
- **5 Quantitative Factors**: `high_volume`, `financial_impact`, `customer_facing`, `revenue_critical`, `regulatory_impact`
- **8 Qualitative Factors**: `ai_ml_usage`, `high_complexity`, `autonomous_decisions`, `black_box`, `third_party`, `data_sensitive`, `real_time`, `customer_impact`
- **Total**: 13 risk factor categories

### Regulatory Basis

**From OSFI E-23 Guideline (Section C.2, Page 10):**

> "The risk rating approach should be supported by clear, measurable criteria for each risk dimension and incorporate both quantitative and qualitative factors:
>
> - **Quantitative factors** include the importance, size and growth of the portfolio that the model covers (as applicable), or potential operational, security or financial impacts.
> - **Qualitative factors** include business use or purpose, model complexity or level of autonomy, reliability of data inputs, customer impacts, or regulatory risk.
>
> Institutions may organize risk factors according to **other risk dimensions relevant to the institution's context and practice**."

**Key Finding:** The guideline provides **examples only**, not prescriptive requirements. The specific 13 factor categories are an implementation interpretation.

### Tunable

- **Number of factors** (currently 5 quantitative + 8 qualitative = 13 total)
- **Factor category names and definitions** (e.g., rename `revenue_critical` to `business_materiality`)
- **Factor groupings** (currently quantitative/qualitative, could use "vulnerability/materiality" or "uncertainty/impact" as guideline suggests)
- **Can add institution-specific factors** based on business model:
  - **Insurance**: `actuarial_assumptions`, `longevity_risk`, `underwriting_complexity`
  - **Investment**: `market_volatility_exposure`, `systemic_risk`, `cross_border_transactions`
  - **Banking**: `credit_concentration`, `liquidity_risk`, `interest_rate_sensitivity`
  - **Fintech**: `api_dependencies`, `high_frequency_trading`, `cryptocurrency_exposure`
- **Can remove factors** not relevant to institution type
- **Can split or merge factors** (e.g., split `customer_facing` into `retail_customer` and `institutional_client`)

### Impact

Changes which dimensions are assessed for model risk rating, fundamentally altering risk assessment structure.

### Example Customization

```python
# Insurance company customization
quantitative_indicators = {
    'high_volume': [...],
    'financial_impact': [...],
    'regulatory_impact': [...],
    'longevity_risk': ['mortality', 'life expectancy', 'demographic shifts', 'longevity assumptions'],
    'catastrophe_exposure': ['natural disaster', 'catastrophic event', 'extreme weather', 'pandemic']
}

qualitative_indicators = {
    'ai_ml_usage': [...],
    'high_complexity': [...],
    'autonomous_decisions': [...],
    'actuarial_judgment': ['actuarial assumptions', 'expert judgment', 'subjective parameters'],
    'reinsurance_dependency': ['reinsurance', 'risk transfer', 'third-party coverage'],
    'data_sensitive': [...],
    'policyholder_impact': ['policyholder decision', 'benefit determination', 'claims assessment']
}
```

---

## 5. Risk Detection Keywords (Factor Detection)

**Location:** `osfi_e23_processor.py:265-283`

### Quantitative Indicators (5 factors)
```python
'high_volume': ['millions', 'thousands', 'large scale', 'high volume', 'enterprise-wide']
'financial_impact': ['loan', 'credit', 'pricing', 'capital', 'risk management', 'trading', 'investment']
'customer_facing': ['customer', 'client', 'retail', 'commercial', 'public']
'revenue_critical': ['revenue', 'profit', 'income', 'business critical', 'core business']
'regulatory_impact': ['regulatory', 'compliance', 'capital adequacy', 'stress testing', 'reporting']
```

### Qualitative Indicators (8 factors)
```python
'ai_ml_usage': ['ai', 'artificial intelligence', 'machine learning', 'neural network', 'deep learning']
'high_complexity': ['complex', 'sophisticated', 'advanced', 'ensemble', 'multi-model']
'autonomous_decisions': ['autonomous', 'automated decision', 'without human review', 'real-time decision']
'black_box': ['black box', 'unexplainable', 'opaque', 'proprietary algorithm']
'third_party': ['third party', 'vendor', 'external', 'outsourced', 'cloud-based']
'data_sensitive': ['personal data', 'sensitive', 'confidential', 'private information']
'real_time': ['real-time', 'real time', 'immediate', 'instant', 'live']
'customer_impact': ['customer decision', 'client impact', 'individual outcome', 'personal finance']
```

**Tunable:**
- Keyword lists for each indicator (add industry-specific terms)
- Can add new indicators (e.g., 'cross_border', 'high_frequency')
- Indicator definitions to match institutional taxonomy

**Impact:** Changes which models get flagged for each risk factor

---

## 6. Approval Authority Mapping

**Location:** `osfi_e23_processor.py:753-761`

```python
{
    "Low": "Model Owner or Designated Manager",
    "Medium": "Senior Management or Risk Committee",
    "High": "Executive Committee or CRO",
    "Critical": "Board of Directors or CEO"
}
```

**Tunable:**
- Approval authority titles (match org chart)
- Authority levels per risk rating
- Can add multi-level approvals

**Impact:** Changes governance workflow requirements

---

## 7. Monitoring Frequency

**Location:** `osfi_e23_processor.py:763-771`

```python
{
    "Low": "Quarterly monitoring with annual deep-dive",
    "Medium": "Monthly monitoring with quarterly reviews",
    "High": "Weekly monitoring with monthly reviews",
    "Critical": "Daily monitoring with weekly reviews"
}
```

**Tunable:**
- Monitoring intervals per risk level
- Review frequency requirements
- Can align with existing model governance calendar

**Impact:** Changes ongoing monitoring requirements

---

## 8. Documentation Requirements

**Location:** `osfi_e23_processor.py:773-799`

### Base Requirements (All Levels)
- Model rationale and business purpose
- Data sources and quality documentation
- Model methodology and assumptions
- Performance metrics and validation results

### High/Critical Additional Requirements
- Detailed explainability documentation
- Bias testing and mitigation measures
- Comprehensive audit trail and change log
- Risk assessment and mitigation strategies
- Contingency and rollback procedures

### Critical-Only Additional Requirements
- Board presentation and approval documentation
- External validation reports
- Regulatory compliance attestations
- Continuous monitoring dashboards and alerts

**Tunable:**
- Document list per risk level
- Document templates and standards
- Deliverable formats

**Impact:** Changes compliance documentation burden

---

## 9. Governance Structure Requirements

**Location:** `osfi_e23_processor.py:859-884`

### Base Structure (All Levels)
- Model Owner
- Model Developer
- Model Reviewer
- Model Approver (varies by risk level)

### High/Critical Additional Roles
- Model Risk Committee
- Compliance Officer
- Legal Ethics Advisor

### Critical-Only Additional Roles
- Board Oversight
- External Validator
- Regulatory Liaison

**Tunable:**
- Role names and responsibilities
- Organizational structure per risk level
- Can add institution-specific roles (e.g., "Data Governance Officer")

**Impact:** Changes governance committee composition

---

## 10. Lifecycle Requirements

**Location:** `osfi_e23_processor.py:886-916`

### Enhanced Requirements by Risk Level

**Design Stage (High/Critical):**
- Comprehensive bias and fairness assessment
- Detailed explainability analysis
- Regulatory compliance review

**Review Stage (High/Critical):**
- External validation (Critical models)
- Regulatory pre-approval consultation
- Comprehensive stress testing

**Monitoring Stage (High/Critical):**
- Real-time performance dashboards
- Automated alert systems
- Monthly governance reporting

**Tunable:**
- Requirements per lifecycle stage
- Risk-based requirement escalation
- Stage-specific deliverables

**Impact:** Changes work required at each lifecycle stage

---

## 11. Report Structure and Content

**Location:** `osfi_e23_report_generators.py`

### Current 7-Chapter Structure (v2.2.9)
1. Executive Summary (150-200 words)
2. Risk Rating Methodology (detailed scoring tables)
3. Lifecycle Coverage Assessment (coverage percentage by stage)
4. Stage-Specific Compliance Checklist (actionable items, title dynamically changes)
5. Governance Structure (v2.2.9 expanded):
   - 5.1 Governance Roles and Responsibilities
   - 5.2 Documentation Requirements
   - 5.3 Review and Approval Procedures
6. Monitoring Framework (ongoing monitoring requirements)
7. Annex: OSFI E-23 Principles (full principle text)

**Tunable:**
- Report sections and order
- Executive summary length/style
- Table formats and detail level
- Branding and formatting
- Can add sections (e.g., "Regulatory Attestation", "Third-Party Validation")

**Impact:** Changes regulatory deliverable format

---

## Implementation Notes

### To Customize for Your Institution:

1. **Create institution-specific configuration file** (e.g., `config_yourbank.json`)
2. **Override default parameters** in initialization
3. **Maintain backward compatibility** by keeping default values
4. **Document rationale** for each customization
5. **Version control** configuration changes

### Example Customization Pattern:

```python
class CustomOSFIE23Processor(OSFIE23Processor):
    def __init__(self, config_path: str = "config_yourbank.json"):
        super().__init__()
        self._load_custom_config(config_path)

    def _load_custom_config(self, config_path: str):
        # Override scoring weights
        self.quant_weight = 12  # More conservative
        self.qual_weight = 6

        # Override thresholds
        self.risk_thresholds = {
            "Low": [0, 20],      # Tighter thresholds
            "Medium": [21, 45],
            "High": [46, 70],
            "Critical": [71, 100]
        }

        # Add institution-specific keywords
        self.quantitative_indicators['high_volume'].extend([
            'billions', 'global scale', 'cross-border'
        ])
```

---

## Validation After Customization

After modifying any tunable parameters, run:

```bash
# Test scoring consistency
python3 test_risk_score_consistency.py

# Validate full functionality
python3 validate_functionality.py

# Test with sample models
python3 test_mcp_comprehensive.py
```

---

## Transparency Note

All scoring weights, amplification factors, and thresholds are **explicitly labeled as exemplification** in generated reports. The reports include:

> "Note: Scoring weights (10 pts quantitative, 8 pts qualitative) are exemplification and can be tuned to institutional specifications."

This ensures institutions understand these are configurable parameters, not regulatory mandates.
