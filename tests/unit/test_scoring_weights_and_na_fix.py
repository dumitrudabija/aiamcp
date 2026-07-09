#!/usr/bin/env python3
"""
Tests for the OSFI E-23 scoring engine changes:
1. The override_rate / NOT_APPLICABLE crash fix in score_factor().
2. The use_weights toggle in score_dimension()/calculate_overall_risk() -
   default (off) behavior must exactly match the pre-existing unweighted
   average; explicit weights must change the result when turned on.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from risk_dimension_extraction import score_factor, score_dimension, calculate_overall_risk
from osfi_e23_risk_dimensions import get_factor_by_id


def test_override_rate_not_applicable_does_not_raise():
    """Regression test for the override_rate NOT_APPLICABLE crash."""
    factor_def = get_factor_by_id("governance_oversight", "override_rate")
    assert factor_def is not None
    assert factor_def.get("allow_na") is True

    result = score_factor(
        factor_id="override_rate",
        factor_type="quantitative",
        value="NOT_APPLICABLE",
        factor_def=factor_def,
        is_not_stated=False,
    )

    assert result["is_not_applicable"] is True
    assert result["risk_level"] == "low"
    assert result["numeric_score"] == 1
    print("PASS: override_rate NOT_APPLICABLE scores as Low without raising")


def test_score_dimension_use_weights_false_matches_legacy_output():
    """Default (unweighted) path must be numerically identical to a plain average."""
    factor_scores = [
        {"factor_id": "a", "numeric_score": 1, "is_not_stated": False, "weight": 1.0},
        {"factor_id": "b", "numeric_score": 3, "is_not_stated": False, "weight": 1.0},
        {"factor_id": "c", "numeric_score": 4, "is_not_stated": False, "weight": 1.0},
    ]
    result = score_dimension("test_dim", factor_scores, use_weights=False)
    assert result["scoring_method"] == "simple_average"
    assert result["numeric_score"] == round((1 + 3 + 4) / 3, 2)
    print("PASS: use_weights=False reproduces the plain average")


def test_score_dimension_use_weights_true_with_custom_weights():
    """Weighted path must differ from the simple average when weights differ."""
    factor_scores = [
        {"factor_id": "a", "numeric_score": 1, "is_not_stated": False, "weight": 3.0},
        {"factor_id": "b", "numeric_score": 4, "is_not_stated": False, "weight": 1.0},
    ]
    simple = score_dimension("test_dim", factor_scores, use_weights=False)
    weighted = score_dimension("test_dim", factor_scores, use_weights=True)

    assert simple["scoring_method"] == "simple_average"
    assert weighted["scoring_method"] == "weighted_average"
    assert simple["numeric_score"] == round((1 + 4) / 2, 2)
    assert weighted["numeric_score"] == round((1 * 3 + 4 * 1) / 4, 2)
    assert weighted["numeric_score"] != simple["numeric_score"]
    print("PASS: use_weights=True produces a genuinely weighted average")


def test_calculate_overall_risk_default_matches_legacy():
    dimension_scores = {
        "dim1": {"numeric_score": 2, "not_stated_count": 0},
        "dim2": {"numeric_score": 3, "not_stated_count": 0},
    }
    result = calculate_overall_risk(dimension_scores)
    assert result["overall_numeric_score"] == round((2 + 3) / 2, 2)
    assert result["scoring_method"] == "dimension_average"
    print("PASS: calculate_overall_risk default path unchanged")


if __name__ == "__main__":
    tests = [
        test_override_rate_not_applicable_does_not_raise,
        test_score_dimension_use_weights_false_matches_legacy_output,
        test_score_dimension_use_weights_true_with_custom_weights,
        test_calculate_overall_risk_default_matches_legacy,
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
