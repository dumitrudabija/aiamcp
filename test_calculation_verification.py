#!/usr/bin/env python3
"""
Verification test to show detailed risk calculation breakdown
This demonstrates the math is correct and transparent
"""

from server import MCPServer
import sys

def verify_calculation(project_name, project_description):
    """Perform assessment and show detailed calculation breakdown."""
    print(f"\n{'='*80}")
    print(f"CALCULATING: {project_name}")
    print(f"{'='*80}")

    server = MCPServer()

    # Perform real assessment
    assessment = server.osfi_e23_processor.assess_model_risk(
        project_name=project_name,
        project_description=project_description
    )

    risk_analysis = assessment['risk_analysis']
    quant_indicators = risk_analysis['quantitative_indicators']
    qual_indicators = risk_analysis['qualitative_indicators']

    # Display detected indicators
    print("\n📋 STEP 1: RISK FACTOR DETECTION (Rule-Based Keyword Matching)")
    print("-" * 80)

    print("\nQuantitative Indicators (10 points each):")
    quant_detected = []
    for key, value in quant_indicators.items():
        if value:
            quant_detected.append(key)
            print(f"  ✓ {key.replace('_', ' ').title()}")
    if not quant_detected:
        print("  (none detected)")

    print("\nQualitative Indicators (8 points each):")
    qual_detected = []
    for key, value in qual_indicators.items():
        if value:
            qual_detected.append(key)
            print(f"  ✓ {key.replace('_', ' ').title()}")
    if not qual_detected:
        print("  (none detected)")

    # Calculate scores
    quant_score = risk_analysis['quantitative_score']
    qual_score = risk_analysis['qualitative_score']
    base_score = quant_score + qual_score

    print("\n📊 STEP 2-4: SCORE CALCULATION")
    print("-" * 80)
    print(f"Quantitative Subtotal: {len(quant_detected)} indicators × 10 points = {quant_score} points")
    print(f"Qualitative Subtotal: {len(qual_detected)} indicators × 8 points = {qual_score} points")
    print(f"Base Score: {quant_score} + {qual_score} = {base_score} points")

    # Check amplifications
    print("\n⚡ STEP 5: RISK AMPLIFICATION ANALYSIS")
    print("-" * 80)

    amplifications = []
    multiplier = 1.0

    # Check each amplification condition
    if quant_indicators.get('financial_impact') and qual_indicators.get('ai_ml_usage'):
        amplifications.append(('AI/ML in Financial Decisions', 0.3))
        multiplier += 0.3
        print("✓ AI/ML in Financial Decisions: +30%")
        print(f"  (financial_impact={quant_indicators.get('financial_impact')} AND ai_ml_usage={qual_indicators.get('ai_ml_usage')})")

    if quant_indicators.get('customer_facing') and qual_indicators.get('autonomous_decisions'):
        amplifications.append(('Autonomous Customer Decisions', 0.2))
        multiplier += 0.2
        print("✓ Autonomous Customer Decisions: +20%")
        print(f"  (customer_facing={quant_indicators.get('customer_facing')} AND autonomous_decisions={qual_indicators.get('autonomous_decisions')})")

    if qual_indicators.get('black_box') and quant_indicators.get('regulatory_impact'):
        amplifications.append(('Unexplainable Regulatory Models', 0.25))
        multiplier += 0.25
        print("✓ Unexplainable Regulatory Models: +25%")
        print(f"  (black_box={qual_indicators.get('black_box')} AND regulatory_impact={quant_indicators.get('regulatory_impact')})")

    if qual_indicators.get('third_party') and quant_indicators.get('revenue_critical'):
        amplifications.append(('Critical Third-Party Dependencies', 0.15))
        multiplier += 0.15
        print("✓ Critical Third-Party Dependencies: +15%")
        print(f"  (third_party={qual_indicators.get('third_party')} AND revenue_critical={quant_indicators.get('revenue_critical')})")

    if not amplifications:
        print("(no high-risk combinations detected)")

    print(f"\nTotal Amplification Multiplier: {multiplier:.2f}x")

    # Final calculation
    print("\n🎯 STEP 6: FINAL RISK SCORE AND RATING")
    print("-" * 80)

    if multiplier > 1.0:
        amplified_score = int(base_score * multiplier)
        print(f"Final Score = Base Score × Amplification Multiplier")
        print(f"Final Score = {base_score} × {multiplier:.2f} = {amplified_score} points")
        final_score = min(amplified_score, 100)
        if amplified_score > 100:
            print(f"Capped at 100: {final_score} points")
    else:
        final_score = base_score
        print(f"Final Score = Base Score (no amplification)")
        print(f"Final Score = {base_score} points")

    # Determine rating
    if final_score <= 25:
        rating = "Low"
    elif final_score <= 50:
        rating = "Medium"
    elif final_score <= 75:
        rating = "High"
    else:
        rating = "Critical"

    print(f"\nRisk Rating Thresholds:")
    print(f"  • Low: 0-25 points")
    print(f"  • Medium: 26-50 points")
    print(f"  • High: 51-75 points")
    print(f"  • Critical: 76-100 points")

    print(f"\n✅ ASSIGNED RISK RATING: {rating} ({final_score} points)")

    # Verify against actual assessment
    actual_score = assessment['risk_score']
    actual_rating = assessment['risk_level']

    print(f"\n🔍 VERIFICATION")
    print("-" * 80)
    print(f"Calculated Score: {final_score}")
    print(f"Actual Assessment Score: {actual_score}")
    print(f"Match: {'✅ YES' if final_score == actual_score else '❌ NO - MISMATCH!'}")

    print(f"\nCalculated Rating: {rating}")
    print(f"Actual Assessment Rating: {actual_rating}")
    print(f"Match: {'✅ YES' if rating == actual_rating else '❌ NO - MISMATCH!'}")

    return final_score == actual_score and rating == actual_rating


def main():
    print("\n" + "="*80)
    print("RISK CALCULATION VERIFICATION TEST")
    print("Demonstrates transparent, rule-based scoring methodology")
    print("="*80)

    all_passed = True

    # Test 1: High complexity AI/ML model
    passed = verify_calculation(
        "Commercial Lending AI Model",
        "AI-powered commercial lending model using machine learning for credit risk assessment. "
        "Processes $150-200M annual lending volume. Makes automated lending decisions for loans up to $2M. "
        "Customer-facing system affecting business credit access. Uses ensemble ML models with complex feature engineering."
    )
    all_passed = all_passed and passed

    # Test 2: Simple internal model
    passed = verify_calculation(
        "Internal Risk Dashboard",
        "Internal reporting dashboard for risk metrics aggregation. Simple statistical calculations. "
        "No customer impact. Non-financial decision support. Used only by internal risk team for trend analysis."
    )
    all_passed = all_passed and passed

    # Test 3: Critical regulatory model
    passed = verify_calculation(
        "Basel III Regulatory Capital Model",
        "AI/ML-powered regulatory capital calculation model for Basel III compliance. "
        "Calculates required capital reserves affecting billions in capital allocation. Direct regulatory reporting to OSFI. "
        "Uses advanced machine learning for credit risk weighted assets. Customer portfolio risk assessment impacting lending capacity. "
        "Complex neural network architecture with multiple data sources."
    )
    all_passed = all_passed and passed

    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL CALCULATIONS VERIFIED - Math is correct and transparent")
    else:
        print("❌ VERIFICATION FAILED - Calculation mismatch detected")
    print("="*80)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
