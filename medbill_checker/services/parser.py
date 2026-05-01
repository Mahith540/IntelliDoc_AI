from __future__ import annotations

import re
from typing import List

from medbill_checker.models import BillParseResult, Category, LineItem


PRICE_RE = re.compile(r"\$?([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})|[0-9]+(?:\.[0-9]{2}))")
QTY_RE = re.compile(r"(?:qty|quantity|x)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE)
TOTAL_HINT_RE = re.compile(r"(?:total|amount due|balance due)\s*[:\-]?\s*\$?([0-9,]+(?:\.[0-9]{2})?)", re.IGNORECASE)


CATEGORY_KEYWORDS = {
    Category.medication: ["tablet", "capsule", "mg", "ml", "drug", "med", "injection", "pharmacy"],
    Category.procedure: ["procedure", "surgery", "consult", "therapy", "operation", "visit"],
    Category.lab: ["lab", "blood", "cbc", "panel", "test", "diagnostic", "scan", "x-ray", "mri"],
    Category.room: ["room", "bed", "icu", "ward", "admission", "facility"],
}


class BillParser:
    def parse(self, text: str) -> BillParseResult:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        items: List[LineItem] = []
        warnings: List[str] = []
        parsed_total = self._extract_bill_total(text)

        for line in lines:
            item = self._parse_line_item(line)
            if item:
                items.append(item)

        if not items:
            warnings.append("No structured line items detected. OCR quality may be low.")

        return BillParseResult(line_items=items, parsed_total=parsed_total, extraction_warnings=warnings)

    def _extract_bill_total(self, text: str) -> float:
        matches = TOTAL_HINT_RE.findall(text)
        if not matches:
            return 0.0
        return self._to_float(matches[-1])

    def _parse_line_item(self, line: str) -> LineItem | None:
        if TOTAL_HINT_RE.search(line):
            return None

        price_matches = PRICE_RE.findall(line)
        if not price_matches:
            return None

        values = [self._to_float(v) for v in price_matches]
        total_price = max(values)
        qty = self._extract_quantity(line)
        unit_price = round(total_price / qty, 2) if qty > 0 else total_price

        description = PRICE_RE.sub("", line).strip(" -:")
        if not description:
            description = "Unlabeled hospital charge"

        category = self._infer_category(description)
        return LineItem(
            description=description,
            quantity=qty,
            unit_price=unit_price,
            total_price=round(total_price, 2),
            category=category,
        )

    def _extract_quantity(self, line: str) -> float:
        match = QTY_RE.search(line)
        if match:
            return max(float(match.group(1)), 1.0)

        loose_x = re.search(r"\b([0-9]+(?:\.[0-9]+)?)\s*x\b", line, flags=re.IGNORECASE)
        if loose_x:
            return max(float(loose_x.group(1)), 1.0)
        return 1.0

    def _infer_category(self, description: str) -> Category:
        lowered = description.lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                return category
        return Category.misc

    @staticmethod
    def _to_float(value: str) -> float:
        return float(value.replace(",", ""))
