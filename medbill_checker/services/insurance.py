from __future__ import annotations

from collections import Counter
from difflib import SequenceMatcher
from typing import List

from medbill_checker.models import Category, CoverageItem, CoverageSummary, InsurancePlan, LineItem


class InsuranceChecker:
    def evaluate(self, line_items: List[LineItem], plan: InsurancePlan | None = None) -> CoverageSummary:
        if plan is None:
            plan = InsurancePlan()

        deductible_remaining = plan.deductible_remaining
        insurance_total = 0.0
        patient_total = 0.0
        allowed_total = 0.0
        deductible_applied = 0.0
        result_items: List[CoverageItem] = []

        for item in line_items:
            coverage_pct = plan.coverage_percent_by_category.get(item.category, 0.50)
            allowed_amount = round(item.total_price * (0.85 if not plan.in_network else 1.0), 2)

            deductible_take = min(deductible_remaining, allowed_amount)
            deductible_remaining -= deductible_take
            deductible_applied += deductible_take

            post_deductible = max(allowed_amount - deductible_take, 0.0)
            insurance_pays = round(post_deductible * coverage_pct, 2)
            patient_pays = round(allowed_amount - insurance_pays, 2)

            notes: List[str] = []
            if deductible_take > 0:
                notes.append("Deductible applied")
            if not plan.in_network:
                notes.append("Out-of-network adjustment used")
            if item.category == Category.misc:
                notes.append("Uncategorized charge; verify billing code")

            insurance_total += insurance_pays
            patient_total += patient_pays
            allowed_total += allowed_amount

            result_items.append(
                CoverageItem(
                    description=item.description,
                    category=item.category,
                    billed_amount=item.total_price,
                    estimated_allowed_amount=allowed_amount,
                    estimated_insurance_pays=insurance_pays,
                    estimated_patient_pays=patient_pays,
                    notes=notes,
                )
            )

        billed_total = round(sum(item.total_price for item in line_items), 2)
        flags = self._detect_flags(line_items)

        return CoverageSummary(
            total_billed=billed_total,
            estimated_allowed_total=round(allowed_total, 2),
            estimated_insurance_total=round(insurance_total, 2),
            estimated_patient_total=round(patient_total, 2),
            deductible_applied=round(deductible_applied, 2),
            potential_flags=flags,
            items=result_items,
        )

    def _detect_flags(self, items: List[LineItem]) -> List[str]:
        flags: List[str] = []
        if not items:
            return flags

        expensive = [item for item in items if item.total_price >= 1000]
        if expensive:
            flags.append(f"{len(expensive)} high-cost line item(s) above $1,000 detected")

        category_counts = Counter(item.category for item in items)
        if category_counts[Category.misc] / max(len(items), 1) > 0.35:
            flags.append("Many line items are uncategorized; request itemized CPT/HCPCS details")

        duplicates = self._find_possible_duplicates(items)
        if duplicates:
            flags.append(f"Possible duplicate charges: {', '.join(duplicates[:3])}")

        return flags

    def _find_possible_duplicates(self, items: List[LineItem]) -> List[str]:
        duplicates: List[str] = []
        for i, left in enumerate(items):
            for right in items[i + 1 :]:
                if self._similar(left.description, right.description) > 0.88:
                    duplicates.append(left.description)
                    break
        return duplicates

    @staticmethod
    def _similar(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
