"""
Test MPCOM description coverage across ALL lifecycle stages.
This will help identify if the user was looking at the wrong stage.
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

def test_all_stages():
    """Test coverage for MPCOM across all 5 lifecycle stages."""
    processor = OSFIE23Processor()

    stages = ["design", "review", "deployment", "monitoring", "decommission"]

    print("=" * 100)
    print("TESTING MPCOM COVERAGE ACROSS ALL 5 LIFECYCLE STAGES")
    print("=" * 100)

    for stage in stages:
        print(f"\n{'=' * 100}")
        print(f"STAGE: {stage.upper()}")
        print('=' * 100)

        compliance_analysis = processor._analyze_lifecycle_compliance(mpcom_description, stage)

        print(f"\n📋 {stage.capitalize()} Stage Indicators:")
        for indicator_name, indicator_value in compliance_analysis["stage_indicators"].items():
            status = "✅ COVERED" if indicator_value else "❌ NOT COVERED"
            print(f"   {indicator_name}: {status}")

        print(f"\n📊 Coverage Score: {compliance_analysis['compliance_score']}/{compliance_analysis['total_indicators']}")
        print(f"📊 Coverage Percentage: {compliance_analysis['compliance_percentage']}%")

        if compliance_analysis['gaps_identified']:
            print(f"\n🔍 Gaps Identified:")
            for gap in compliance_analysis['gaps_identified']:
                print(f"   - {gap}")

    # Summary table
    print("\n" + "=" * 100)
    print("SUMMARY: Coverage Across All Stages")
    print("=" * 100)
    print(f"\n{'Stage':<20} {'Coverage':<15} {'Score':<15} {'Indicators'}")
    print("-" * 100)

    for stage in stages:
        compliance_analysis = processor._analyze_lifecycle_compliance(mpcom_description, stage)
        coverage_pct = compliance_analysis['compliance_percentage']
        score = compliance_analysis['compliance_score']
        total = compliance_analysis['total_indicators']
        indicators = ', '.join([k.replace('_covered', '') for k, v in compliance_analysis['stage_indicators'].items() if v])
        if not indicators:
            indicators = "NONE"

        print(f"{stage.capitalize():<20} {coverage_pct}%{'':<12} {score}/{total}{'':<12} {indicators}")

    print("\n" + "=" * 100)
    print("POTENTIAL ISSUE DIAGNOSIS")
    print("=" * 100)

    # Check if ANY stage has 0% coverage
    zero_coverage_stages = []
    for stage in stages:
        compliance_analysis = processor._analyze_lifecycle_compliance(mpcom_description, stage)
        if compliance_analysis['compliance_percentage'] == 0:
            zero_coverage_stages.append(stage)

    if zero_coverage_stages:
        print(f"\n⚠️ Found {len(zero_coverage_stages)} stage(s) with 0% coverage:")
        for stage in zero_coverage_stages:
            print(f"   - {stage.capitalize()}")
        print("\n💡 HYPOTHESIS: User may have been looking at one of these stages, not Design stage.")
    else:
        print("\n✅ NO stages have 0% coverage.")
        print("💡 HYPOTHESIS: Issue may be with:")
        print("   1. Description was truncated when passed to MCP")
        print("   2. Wrong stage parameter was used")
        print("   3. Display/formatting issue in Claude's response")
        print("   4. User was looking at a different metric")

if __name__ == "__main__":
    test_all_stages()
