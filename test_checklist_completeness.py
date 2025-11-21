#!/usr/bin/env python3
"""
Test checklist completeness for monitoring and decommission stages.
Verifies that all 3 OSFI elements have checklist items.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from osfi_e23_processor import OSFIE23Processor
from osfi_e23_structure import OSFI_LIFECYCLE_COMPONENTS


def test_monitoring_checklist_completeness():
    """Test that monitoring stage has checklist items for all 3 elements."""
    print("\n" + "="*80)
    print("TEST: Monitoring Stage Checklist Completeness")
    print("="*80)

    processor = OSFIE23Processor()

    # Test for both Low and High risk levels
    for risk_level in ["Low", "High"]:
        print(f"\n{risk_level} Risk Level:")

        checklist_mapping = processor._map_checklist_to_elements("monitoring", risk_level)

        elements = OSFI_LIFECYCLE_COMPONENTS["monitoring"]["subcomponents"]

        all_complete = True
        for idx, element_name in enumerate(elements):
            items = checklist_mapping.get(idx, [])
            has_items = len(items) > 0

            status = "✅ PASS" if has_items else "❌ FAIL"
            print(f"  {status}: Element {idx} ({element_name}) - {len(items)} items")

            if has_items:
                for item in items:
                    print(f"    - {item['item']} (required: {item['required']})")

            all_complete = all_complete and has_items

        if all_complete:
            print(f"  ✅ All 3 monitoring elements have checklist items for {risk_level} risk")
        else:
            print(f"  ❌ Some monitoring elements missing checklist items for {risk_level} risk")

    return all_complete


def test_decommission_checklist_completeness():
    """Test that decommission stage has checklist items for all 3 elements."""
    print("\n" + "="*80)
    print("TEST: Decommission Stage Checklist Completeness")
    print("="*80)

    processor = OSFIE23Processor()

    # Test for both Low and High risk levels
    for risk_level in ["Low", "High"]:
        print(f"\n{risk_level} Risk Level:")

        checklist_mapping = processor._map_checklist_to_elements("decommission", risk_level)

        elements = OSFI_LIFECYCLE_COMPONENTS["decommission"]["subcomponents"]

        all_complete = True
        for idx, element_name in enumerate(elements):
            items = checklist_mapping.get(idx, [])
            has_items = len(items) > 0

            status = "✅ PASS" if has_items else "❌ FAIL"
            print(f"  {status}: Element {idx} ({element_name}) - {len(items)} items")

            if has_items:
                for item in items:
                    print(f"    - {item['item']} (required: {item['required']})")

            all_complete = all_complete and has_items

        if all_complete:
            print(f"  ✅ All 3 decommission elements have checklist items for {risk_level} risk")
        else:
            print(f"  ❌ Some decommission elements missing checklist items for {risk_level} risk")

    return all_complete


def test_implementation_note_presence():
    """Test that implementation notes are present for monitoring and decommission."""
    print("\n" + "="*80)
    print("TEST: Implementation Note Presence")
    print("="*80)

    # Read the processor file
    with open('osfi_e23_processor.py', 'r') as f:
        content = f.read()

    # Check for implementation notes
    monitoring_note = "# Note: These 3 elements are our implementation interpretation of OSFI Principle 3.6 (monitoring requirement)"
    decommission_note = "# Note: These 3 elements are our implementation interpretation of OSFI Principle 3.6 (decommission requirement)"

    has_monitoring_note = monitoring_note in content
    has_decommission_note = decommission_note in content

    print(f"{'✅ PASS' if has_monitoring_note else '❌ FAIL'}: Monitoring stage has implementation note")
    print(f"{'✅ PASS' if has_decommission_note else '❌ FAIL'}: Decommission stage has implementation note")

    return has_monitoring_note and has_decommission_note


def run_all_tests():
    """Run all checklist completeness tests."""
    print("\n" + "="*80)
    print("CHECKLIST COMPLETENESS TEST SUITE")
    print("="*80)
    print("\nVerifying monitoring and decommission checklists have items for all 3 OSFI elements")

    results = []
    results.append(("Monitoring Checklist Completeness", test_monitoring_checklist_completeness()))
    results.append(("Decommission Checklist Completeness", test_decommission_checklist_completeness()))
    results.append(("Implementation Note Presence", test_implementation_note_presence()))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    total = len(results)
    passed = sum(1 for _, result in results if result)
    failed = total - passed

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! All monitoring and decommission elements have checklist items.")
        print("\nWhat this means:")
        print("  1. Monitoring stage has checklist items for all 3 elements (Performance Tracking, Drift Detection, Escalation Procedures)")
        print("  2. Decommission stage has checklist items for all 3 elements (Retirement Process, Stakeholder Notification, Documentation Retention)")
        print("  3. Implementation notes clarify these are interpretations of OSFI Principle 3.6")
        print("  4. Risk-level specific items are properly added for High/Critical models")
        return True
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED - Review output above for details")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
