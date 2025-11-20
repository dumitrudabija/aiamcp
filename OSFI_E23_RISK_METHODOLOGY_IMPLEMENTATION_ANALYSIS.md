# OSFI E-23 Risk Rating Methodology: Implementation Analysis

**Document Purpose**: This document analyzes the risk rating methodology implemented in this proof-of-concept tool, clearly distinguishing between OSFI E-23 regulatory requirements and our interpretive implementation choices.

**Target Audience**: Compliance officers, risk management professionals, and institutional decision-makers evaluating this approach.

**Key Message**: This implementation represents ONE valid interpretation of OSFI E-23's principles-based guidance. Other approaches are equally valid. The choices documented here should be evaluated and customized for your institution's specific context.

---

## Executive Summary

OSFI Guideline E-23 is **principles-based**, not prescriptive. It requires institutions to establish a risk rating methodology but intentionally does not mandate specific approaches. This tool makes concrete implementation choices to demonstrate feasibility. **These choices are interpretations, not requirements.**

---

## Part 1: What OSFI E-23 REQUIRES (Mandatory)

Source: OSFI E-23, Section C.2 "Model risk rating", Pages 10-11

### 1.1 High-Level Requirements

| OSFI Requirement | Guideline Quote |
|-----------------|-----------------|
| **Must have a risk rating approach** | "A risk rating approach should be implemented based on inherent model risk" |
| **Must use clear, measurable criteria** | "The risk rating approach should be supported by clear, measurable criteria for each risk dimension" |
| **Must include quantitative AND qualitative factors** | "incorporate both quantitative and qualitative factors" |
| **Must assign each model a risk rating** | "Each model should be assigned a model risk rating" |
| **Must be based on inherent risk** | "reflecting model vulnerabilities and materiality of model impacts" |

### 1.2 Factor Categories (Examples Provided, Not Prescriptive)

**OSFI provides EXAMPLES only:**

**Quantitative factors** (OSFI examples):
- "importance, size and growth of the portfolio that the model covers"
- "potential operational, security or financial impacts"

**Qualitative factors** (OSFI examples):
- "business use or purpose"
- "model complexity or level of autonomy"
- "reliability of data inputs"
- "customer impacts"
- "regulatory risk"

### 1.3 Explicit Flexibility

> "Institutions may organize risk factors according to **other risk dimensions relevant to the institution's context and practice** (for example, "vulnerability and materiality" or "uncertainty and impact")."

**KEY POINT**: OSFI explicitly encourages institutional customization.

---

## Part 2: What WE CHOSE TO IMPLEMENT (Our Interpretation)

### 2.1 Factor Structure (Our Choice)

| Element | OSFI Requirement | Our Implementation | Status |
|---------|------------------|-------------------|---------|
| **Number of quantitative factors** | Not specified | **5 factors** | INTERPRETIVE CHOICE |
| **Number of qualitative factors** | Not specified | **8 factors** | INTERPRETIVE CHOICE |
| **Total factor count** | Not specified | **13 factors** | INTERPRETIVE CHOICE |
| **Factor grouping** | "quantitative and qualitative" OR "other dimensions" | **Quantitative/Qualitative** | CHOICE (one of multiple valid options) |

### 2.2 Specific Risk Factors (Our Selection)

#### Quantitative Factors (Our 5 Choices)
1. `high_volume` - Scale of operations
2. `financial_impact` - Financial decision-making involvement
3. `customer_facing` - Customer interaction level
4. `revenue_critical` - Business criticality
5. `regulatory_impact` - Regulatory compliance implications

**OSFI Basis**: These align with OSFI examples of "size", "financial impacts", "customer impacts", "regulatory risk" but the **specific categorization is ours**.

#### Qualitative Factors (Our 8 Choices)
1. `ai_ml_usage` - Use of AI/ML technology
2. `high_complexity` - Model sophistication
3. `autonomous_decisions` - Level of autonomy
4. `black_box` - Explainability limitations
5. `third_party` - External dependencies
6. `data_sensitive` - Data privacy/sensitivity
7. `real_time` - Real-time operation requirements
8. `customer_impact` - Individual customer outcome effects

**OSFI Basis**: These align with OSFI examples of "complexity", "autonomy", "data inputs", "customer impacts" but the **specific factors and definitions are ours**.

### 2.3 Detection Methodology (Our Choice)

| Element | OSFI Requirement | Our Implementation | Status |
|---------|------------------|-------------------|---------|
| **Detection method** | "clear, measurable criteria" | **Keyword matching** | INTERPRETIVE CHOICE |
| **Keyword lists** | Not specified | **Specific terms per factor** | OUR DESIGN |
| **Detection logic** | Not specified | **Boolean detection (present/absent)** | OUR DESIGN |

**Example**: We detect `financial_impact` by searching for keywords: ['loan', 'credit', 'pricing', 'capital', 'risk management', 'trading', 'investment']

**Alternative approaches** (equally valid):
- Questionnaire-based assessment
- Expert judgment scoring
- Quantitative metrics (e.g., actual dollar amounts, transaction volumes)
- Hybrid approaches

### 2.4 Scoring System (Our Choice)

| Element | OSFI Requirement | Our Implementation | Status |
|---------|------------------|-------------------|---------|
| **Scoring scale** | Not specified | **100-point scale** | INTERPRETIVE CHOICE |
| **Quantitative weight** | Not specified | **10 points per factor** | INTERPRETIVE CHOICE |
| **Qualitative weight** | Not specified | **8 points per factor** | INTERPRETIVE CHOICE |
| **Base score range** | Not specified | **0-130 possible** | DERIVED FROM WEIGHTS |

**Calculation**:
- Base score = (# quantitative factors detected × 10) + (# qualitative factors detected × 8)
- Maximum base score = (5 × 10) + (8 × 8) = 50 + 64 = 114 points

### 2.5 Risk Amplification Logic (Our Innovation)

| Element | OSFI Requirement | Our Implementation | Status |
|---------|------------------|-------------------|---------|
| **Amplification concept** | Not mentioned | **4 dangerous combinations** | OUR INNOVATION |
| **Amplification percentages** | Not specified | **15-30% multipliers** | OUR DESIGN |

**Our Amplification Rules**:
1. **AI/ML + Financial Impact**: +30% (recognizing heightened risk when AI makes financial decisions)
2. **Customer-Facing + Autonomous Decisions**: +20% (recognizing risk of automated customer impacts)
3. **Black Box + Regulatory Impact**: +25% (recognizing compliance challenges with unexplainable models)
4. **Third-Party + Revenue-Critical**: +15% (recognizing dependency risk)

**OSFI Basis**: None. This is our value-add to capture interaction effects between risk factors.

**Alternative approaches**:
- No amplification (simple additive scoring)
- Different combinations and percentages
- Non-linear scoring functions
- Machine learning-based risk prediction

### 2.6 Risk Level Thresholds (Our Choice)

| Risk Level | Score Range | OSFI Requirement | Our Implementation | Status |
|------------|-------------|------------------|-------------------|---------|
| **Low** | 0-25 | Not specified | Our cutoff | INTERPRETIVE CHOICE |
| **Medium** | 26-50 | Not specified | Our cutoff | INTERPRETIVE CHOICE |
| **High** | 51-75 | Not specified | Our cutoff | INTERPRETIVE CHOICE |
| **Critical** | 76-100 | Not specified | Our cutoff | INTERPRETIVE CHOICE |

**Number of levels**: OSFI does not specify. We chose 4 levels. Institutions could use:
- 3 levels (Low/Medium/High)
- 5 levels (Very Low/Low/Medium/High/Critical)
- Continuous scale without discrete levels

---

## Part 3: Key Design Decisions & Rationale

### 3.1 Why Keyword Detection?

**Our Reasoning**:
- ✅ Transparent and auditable
- ✅ Deterministic (same input = same output)
- ✅ Fast and scalable
- ✅ No AI "black box" in the assessment tool itself
- ❌ May miss context and nuance
- ❌ Requires well-written project descriptions

**Alternatives institutions might prefer**:
- Structured questionnaires with dropdown menus
- Numeric input fields (e.g., "Enter annual transaction volume")
- Expert panel scoring
- Historical model performance data

### 3.2 Why 10/8 Point Weighting?

**Our Reasoning**:
- Quantitative factors (10 pts) weighted slightly higher than qualitative (8 pts)
- Reflects traditional view that measurable impacts (financial, volume) are more concrete
- But close weighting (10 vs 8) recognizes qualitative factors are nearly as important

**Explicitly documented as tunable** because:
- Different institutions may value qualitative factors more heavily (e.g., 12/10)
- Some may weight equally (10/10)
- Weights should reflect institutional risk appetite

### 3.3 Why Risk Amplification?

**Our Reasoning**:
- Risk is not purely additive
- Certain combinations create disproportionate risk (e.g., AI + Financial decisions)
- Captures "gestalt" risk that factor counts alone miss

**This is our innovation**, not an OSFI requirement. Institutions could:
- Use simple additive scoring
- Use different combinations
- Use different amplification logic
- Use machine learning to detect patterns

### 3.4 Why These Specific Thresholds?

**Our Reasoning**:
- Quartile-based distribution (0-25, 26-50, 51-75, 76-100)
- Creates roughly equal ranges
- Aligns risk levels with governance requirements in our compliance framework

**Institutions should calibrate** based on:
- Their model portfolio distribution
- Internal risk appetite
- Existing governance structures
- Regulatory expectations specific to their jurisdiction

---

## Part 4: What This Means for Institutions

### 4.1 Using This Tool As-Is

If you use this implementation without modification:
- ✅ You ARE complying with OSFI E-23's requirement to have a risk rating methodology
- ✅ You ARE using quantitative and qualitative factors as required
- ⚠️ You ARE accepting OUR interpretation of how to implement these requirements
- ⚠️ You SHOULD validate these choices align with your institution's context

### 4.2 Customizing This Tool

**You SHOULD customize** if:
- Your institution has different risk priorities (e.g., insurance vs. banking)
- Your existing governance uses different risk categories
- Your risk appetite suggests different weights or thresholds
- You have additional risk factors to consider (e.g., climate risk, geopolitical risk)

**You CAN customize**:
- The 13 risk factors (add, remove, rename)
- The keyword lists for detection
- The scoring weights (10/8 points)
- The amplification logic
- The risk level thresholds
- The detection methodology entirely

### 4.3 Building Your Own Methodology

OSFI E-23 allows institutions to build completely different approaches:
- **Questionnaire-based**: Structured questions with point values
- **Expert panel**: Committee scoring with rubrics
- **Quantitative models**: Using actual metrics (transaction volumes, error rates)
- **Hybrid approaches**: Combining multiple methods

**The only requirements**:
1. Must be based on clear, measurable criteria
2. Must include quantitative AND qualitative factors
3. Must cover the risk dimensions OSFI identifies (financial impact, complexity, autonomy, etc.)
4. Must be documented and consistently applied
5. Must assign each model a risk rating

---

## Part 5: Regulatory Positioning

### 5.1 What We Claim

✅ This implementation:
- Satisfies OSFI E-23's requirement for a risk rating methodology
- Uses quantitative and qualitative factors as required
- Provides clear, measurable criteria (keyword detection)
- Demonstrates one valid approach to compliance

### 5.2 What We DO NOT Claim

❌ This implementation:
- Is NOT the only way to comply with OSFI E-23
- Is NOT endorsed or prescribed by OSFI
- Should NOT be used without validation by qualified professionals
- Is NOT a substitute for institutional expertise and judgment

### 5.3 Professional Validation Required

Before relying on this methodology, institutions must:
1. **Validate alignment** with their specific risk profile and business model
2. **Review by qualified professionals** in model risk management
3. **Customize** factors, weights, and thresholds to institutional context
4. **Test and calibrate** against existing model portfolio
5. **Document rationale** for all choices
6. **Obtain governance approval** at appropriate levels

---

## Part 6: Comparison Table

| Aspect | OSFI E-23 Requirement | Our Implementation | Flexibility |
|--------|----------------------|-------------------|-------------|
| **Risk rating required?** | ✅ Yes (mandatory) | ✅ Implemented | No choice |
| **Use quant + qual factors?** | ✅ Yes (mandatory) | ✅ Implemented | No choice |
| **Number of factors** | ❌ Not specified | 13 factors (5+8) | FULLY CUSTOMIZABLE |
| **Specific factors** | 📋 Examples only | Our 13 selections | FULLY CUSTOMIZABLE |
| **Detection method** | ⚙️ "Clear, measurable criteria" | Keyword detection | FULLY CUSTOMIZABLE |
| **Scoring weights** | ❌ Not specified | 10/8 points | FULLY CUSTOMIZABLE |
| **Amplification logic** | ❌ Not mentioned | 4 dangerous combinations | OUR INNOVATION |
| **Risk level count** | ❌ Not specified | 4 levels | FULLY CUSTOMIZABLE |
| **Risk thresholds** | ❌ Not specified | 0-25, 26-50, 51-75, 76-100 | FULLY CUSTOMIZABLE |
| **Overall approach** | 📘 Principles-based guidance | Concrete implementation | INTERPRETIVE |

**Legend**:
- ✅ = Mandatory requirement
- ❌ = Not specified by OSFI
- 📋 = Examples provided, not prescriptive
- ⚙️ = High-level requirement, method not specified
- 📘 = Framework guidance

---

## Conclusion

### Key Takeaways

1. **OSFI E-23 is deliberately principles-based** - It requires risk rating but does not prescribe HOW to rate risk

2. **This tool makes concrete choices** - We selected specific factors, weights, and methods to demonstrate feasibility

3. **These choices are interpretations, not mandates** - Other approaches are equally valid

4. **Customization is expected** - OSFI explicitly encourages institutions to adapt to their context

5. **Professional validation is essential** - This is a starting point, not a finished solution

### Questions for Your Institution

Before adopting or adapting this methodology, ask:

1. **Do these 13 factors capture our most material model risks?**
2. **Is keyword detection appropriate for our model documentation practices?**
3. **Do the 10/8 weights align with our risk appetite?**
4. **Should we use the amplification logic or simpler additive scoring?**
5. **Do the risk level thresholds align with our governance structure?**
6. **What factors are missing that are relevant to our business model?**
7. **Have we validated this approach with our model risk management team?**

### Final Note

This proof-of-concept demonstrates that OSFI E-23 compliance is achievable through automated tooling, but it also demonstrates the significant interpretive choices required. **Your institution's choices may and should differ** based on your specific context, risk appetite, and governance practices.

The value of this tool is not that it provides "the answer" but that it shows "an answer" - one that can be examined, debated, customized, and improved based on institutional expertise and regulatory expectations.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-20
**Related Documents**:
- OSFI_E23_TUNABLE_PARAMETERS.md (detailed customization guide)
- OSFI E-23 Guideline (official regulatory source)
