from medbill_checker.models import Category, LineItem
from medbill_checker.services.alternatives import MedicationAlternativeService
from medbill_checker.services.rag import MedicationRAGService


def test_rag_reviews_mark_alternative_as_review():
    items = [
        LineItem(description="Lipitor 20mg", category=Category.medication, total_price=95.0),
        LineItem(description="Generic Vitamin D", category=Category.medication, total_price=12.0),
    ]
    alternatives = MedicationAlternativeService().suggest(items)
    reviews = MedicationRAGService().review_medications(items, alternatives)

    lipitor_review = next(review for review in reviews if "lipitor" in review.medication_name.lower())
    assert lipitor_review.status.value == "review"
    assert lipitor_review.suggested_alternative
    assert lipitor_review.evidence


def test_rag_retrieve_returns_ranked_evidence():
    evidence = MedicationRAGService().retrieve("Humalog generic cost options", top_k=2)
    assert len(evidence) == 2
    assert evidence[0].score >= evidence[1].score
