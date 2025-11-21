"""
Test script to verify MPCOM description Design stage coverage calculation.
"""

from osfi_e23_processor import OSFIE23Processor

# MPCOM project description from user
mpcom_description = """Marketing Propensity and Campaign Optimization Model (MPCOM)

Business Purpose:
MPCOM is an AI-powered marketing solution deployed by the bank's Marketing Analytics team to predict customer propensity for product uptake and optimize personalized campaign delivery across digital and traditional channels. The model supports customer acquisition, cross-sell, and retention initiatives across retail banking products including credit cards, personal loans, mortgages, and investment accounts.

Technical Architecture:
The solution employs a gradient boosting ensemble (XGBoost) combined with a neural network layer for customer segmentation. The model processes approximately 2.3 million customer records monthly and generates propensity scores across 12 product categories. Predictions are refreshed weekly with real-time scoring available for triggered campaigns.

Data Inputs:
The model ingests demographic data, transaction history (24 months), digital engagement signals (web/app behavior), prior campaign response patterns, credit bureau attributes, and life-event indicators derived from account activity patterns. External data includes postal code-level economic indicators and competitive market intelligence.

Decision Scope:
MPCOM outputs directly determine which customers receive marketing communications, through which channels, at what frequency, and with what product offers. The system autonomously manages campaign suppression rules and budget allocation across channels. Monthly marketing spend influenced by MPCOM outputs averages $1.8M CAD.

Affected Populations:
All retail banking customers (approximately 1.9 million individuals) and prospective customers from purchased prospect lists are scored by the model. Outputs influence offer terms presented to customers, including promotional rates and credit limit pre-approvals."""

def test_design_coverage():
    """Test Design stage coverage for MPCOM description."""
    processor = OSFIE23Processor()

    # Test the internal _analyze_lifecycle_compliance function directly
    print("=" * 80)
    print("TESTING: _analyze_lifecycle_compliance() with MPCOM Description")
    print("=" * 80)

    compliance_analysis = processor._analyze_lifecycle_compliance(mpcom_description, "design")

    print("\n📋 Design Stage Indicators:")
    for indicator_name, indicator_value in compliance_analysis["stage_indicators"].items():
        status = "✅ COVERED" if indicator_value else "❌ NOT COVERED"
        print(f"  {indicator_name}: {status}")

    print(f"\n📊 Coverage Score: {compliance_analysis['compliance_score']}/{compliance_analysis['total_indicators']}")
    print(f"📊 Coverage Percentage: {compliance_analysis['compliance_percentage']}%")

    if compliance_analysis['gaps_identified']:
        print(f"\n🔍 Gaps Identified:")
        for gap in compliance_analysis['gaps_identified']:
            print(f"  - {gap}")

    # Now test the full evaluate_lifecycle_compliance function
    print("\n" + "=" * 80)
    print("TESTING: evaluate_lifecycle_compliance() Full Function")
    print("=" * 80)

    result = processor.evaluate_lifecycle_compliance(
        project_name="MPCOM",
        project_description=mpcom_description,
        current_stage="design"
    )

    print(f"\n🎯 Current Stage: {result['current_stage']}")
    print(f"📊 Coverage from Full Result: {result['compliance_analysis']['compliance_percentage']}%")
    print(f"\n📝 Coverage Explanation:\n{result['coverage_explanation']}")

    # Manual keyword testing
    print("\n" + "=" * 80)
    print("MANUAL KEYWORD TESTING")
    print("=" * 80)

    description_lower = mpcom_description.lower()

    # Test each indicator manually
    rationale_keywords = ['purpose', 'objective', 'rationale', 'business case', 'business need', 'justification']
    data_keywords = ['data quality', 'data governance', 'data standards', 'data source', 'data lineage']
    development_keywords = ['methodology', 'approach', 'algorithm', 'technique', 'development', 'performance', 'accuracy', 'metrics']

    print("\n1️⃣ Model Rationale Keywords:")
    print(f"   Keywords: {rationale_keywords}")
    rationale_matches = [kw for kw in rationale_keywords if kw in description_lower]
    print(f"   Matches Found: {rationale_matches if rationale_matches else 'NONE'}")
    print(f"   Result: {'✅ COVERED' if rationale_matches else '❌ NOT COVERED'}")

    print("\n2️⃣ Model Data Keywords:")
    print(f"   Keywords: {data_keywords}")
    data_matches = [kw for kw in data_keywords if kw in description_lower]
    print(f"   Matches Found: {data_matches if data_matches else 'NONE'}")
    print(f"   Result: {'✅ COVERED' if data_matches else '❌ NOT COVERED'}")

    print("\n3️⃣ Model Development Keywords:")
    print(f"   Keywords: {development_keywords}")
    development_matches = [kw for kw in development_keywords if kw in description_lower]
    print(f"   Matches Found: {development_matches if development_matches else 'NONE'}")
    print(f"   Result: {'✅ COVERED' if development_matches else '❌ NOT COVERED'}")

    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)

    expected_coverage = (len([m for m in [rationale_matches, data_matches, development_matches] if m]) / 3) * 100
    actual_coverage = compliance_analysis['compliance_percentage']

    print(f"\n✅ Expected Coverage: {expected_coverage:.1f}% (based on manual testing)")
    print(f"🔧 Actual Coverage: {actual_coverage}% (from MCP function)")

    if expected_coverage == actual_coverage:
        print("\n✅ SUCCESS: Coverage calculation is CORRECT")
    else:
        print(f"\n❌ DISCREPANCY: Expected {expected_coverage:.1f}% but got {actual_coverage}%")
        print("   This indicates a potential bug in the coverage calculation logic.")

    return result

if __name__ == "__main__":
    test_design_coverage()
