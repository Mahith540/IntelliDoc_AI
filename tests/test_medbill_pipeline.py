from medbill_checker.models import Category, LineItem
from medbill_checker.services.alternatives import MedicationAlternativeService
from medbill_checker.services.insurance import InsuranceChecker


def test_insurance_checker_returns_totals():
    items = [
        LineItem(description="Room Charge", category=Category.room, total_price=1000),
        LineItem(description="CBC Lab", category=Category.lab, total_price=200),
    ]

    summary = InsuranceChecker().evaluate(items)

    assert summary.total_billed == 1200
    assert summary.estimated_patient_total > 0
    assert len(summary.items) == 2


def test_medication_alternative_detected_from_brand_name():
    items = [
        LineItem(description="Lipitor 20mg", category=Category.medication, total_price=90),
    ]

    alternatives = MedicationAlternativeService().suggest(items)

    assert alternatives
    assert "Atorvastatin" in alternatives[0].alternative
