from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from medbill_checker.models import Category, LineItem, MedicationAlternative


class MedicationAlternativeService:
    def __init__(self) -> None:
        path = Path(__file__).resolve().parent.parent / "data" / "med_alternatives.json"
        self.catalog: Dict[str, Dict[str, object]] = json.loads(path.read_text())

    def suggest(self, line_items: List[LineItem]) -> List[MedicationAlternative]:
        alternatives: List[MedicationAlternative] = []

        for item in line_items:
            if item.category != Category.medication:
                continue

            lowered = item.description.lower()
            for key, payload in self.catalog.items():
                if key in lowered:
                    alternatives.append(
                        MedicationAlternative(
                            original_medication=item.description,
                            alternative=str(payload["alternative"]),
                            estimated_monthly_savings=float(payload["estimated_monthly_savings"]),
                            rationale=str(payload["rationale"]),
                            confidence=0.8,
                        )
                    )
                    break

        if not alternatives and any(item.category == Category.medication for item in line_items):
            alternatives.append(
                MedicationAlternative(
                    original_medication="Medication line items detected",
                    alternative="Ask for generic substitution + therapeutic interchange review",
                    estimated_monthly_savings=35.0,
                    rationale="Generic and formulary-aligned options usually reduce out-of-pocket costs",
                    confidence=0.55,
                )
            )

        return alternatives
