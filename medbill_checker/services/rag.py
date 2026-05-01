from __future__ import annotations

import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List

from medbill_checker.models import (
    Category,
    LineItem,
    MedicationAlternative,
    MedicationReview,
    MedicationStatus,
    RetrievalEvidence,
)

TOKEN_RE = re.compile(r"[a-z0-9]+")


class MedicationRAGService:
    """Lightweight local retrieval over curated medication knowledge."""

    def __init__(self) -> None:
        path = Path(__file__).resolve().parent.parent / "data" / "medical_knowledge_base.json"
        self.documents: List[dict[str, object]] = json.loads(path.read_text())
        self.doc_vectors: List[Dict[str, float]] = []
        self.idf: Dict[str, float] = {}
        self._build_index()

    def retrieve(self, query: str, top_k: int = 3) -> List[RetrievalEvidence]:
        qvec = self._vectorize_text(query)
        scored: List[tuple[float, dict[str, object]]] = []
        for vector, document in zip(self.doc_vectors, self.documents):
            score = self._cosine(qvec, vector)
            scored.append((score, document))

        scored.sort(key=lambda item: item[0], reverse=True)
        evidence: List[RetrievalEvidence] = []
        for score, document in scored[:top_k]:
            snippet = str(document["content"])[:170].strip()
            evidence.append(
                RetrievalEvidence(
                    title=str(document["title"]),
                    snippet=snippet,
                    score=round(score, 3),
                )
            )
        return evidence

    def review_medications(
        self,
        line_items: List[LineItem],
        alternatives: List[MedicationAlternative],
    ) -> List[MedicationReview]:
        med_items = [item for item in line_items if item.category == Category.medication]
        if not med_items:
            return []

        alt_by_item = self._map_alternatives(alternatives)
        duplicates = self._duplicate_names(med_items)
        reviews: List[MedicationReview] = []

        for item in med_items:
            lower_desc = item.description.lower()
            evidence = self.retrieve(f"{item.description} generic formulary cost", top_k=2)
            alt = alt_by_item.get(lower_desc)
            high_cost = item.total_price >= 150
            duplicate_charge = lower_desc in duplicates

            if alt is not None:
                reviews.append(
                    MedicationReview(
                        medication_name=item.description,
                        status=MedicationStatus.review,
                        reason="Cost-reduction alternative found. Ask provider if substitution is clinically safe.",
                        suggested_alternative=alt.alternative,
                        estimated_monthly_savings=alt.estimated_monthly_savings,
                        evidence=evidence,
                    )
                )
                continue

            if duplicate_charge:
                reviews.append(
                    MedicationReview(
                        medication_name=item.description,
                        status=MedicationStatus.review,
                        reason="Possible duplicate medication charge detected. Validate against MAR/admin records.",
                        estimated_monthly_savings=0.0,
                        evidence=evidence,
                    )
                )
                continue

            if high_cost:
                reviews.append(
                    MedicationReview(
                        medication_name=item.description,
                        status=MedicationStatus.review,
                        reason="High-cost medication line item. Review formulary tier and 90-day/mail-order options.",
                        estimated_monthly_savings=0.0,
                        evidence=evidence,
                    )
                )
                continue

            reviews.append(
                MedicationReview(
                    medication_name=item.description,
                    status=MedicationStatus.ok,
                    reason="No immediate cost anomaly detected in current rule set.",
                    estimated_monthly_savings=0.0,
                    evidence=evidence,
                )
            )

        return reviews

    def _build_index(self) -> None:
        documents_tokens: List[List[str]] = []
        df_counter: Counter[str] = Counter()

        for document in self.documents:
            text = self._document_text(document)
            tokens = self._tokenize(text)
            documents_tokens.append(tokens)
            for token in set(tokens):
                df_counter[token] += 1

        total_docs = max(len(self.documents), 1)
        self.idf = {
            token: math.log((total_docs + 1) / (doc_freq + 1)) + 1.0
            for token, doc_freq in df_counter.items()
        }

        for tokens in documents_tokens:
            self.doc_vectors.append(self._vectorize_tokens(tokens))

    def _vectorize_text(self, text: str) -> Dict[str, float]:
        return self._vectorize_tokens(self._tokenize(text))

    def _vectorize_tokens(self, tokens: List[str]) -> Dict[str, float]:
        if not tokens:
            return {}
        tf = Counter(tokens)
        vector: Dict[str, float] = {}
        for token, count in tf.items():
            if token not in self.idf:
                continue
            vector[token] = (count / len(tokens)) * self.idf[token]
        return vector

    def _document_text(self, document: dict[str, object]) -> str:
        text_parts = [str(document.get("title", "")), str(document.get("content", ""))]
        keywords = document.get("keywords", [])
        if isinstance(keywords, list):
            text_parts.extend(str(keyword) for keyword in keywords)
        return " ".join(text_parts)

    def _tokenize(self, text: str) -> List[str]:
        return TOKEN_RE.findall(text.lower())

    def _cosine(self, left: Dict[str, float], right: Dict[str, float]) -> float:
        if not left or not right:
            return 0.0
        numerator = 0.0
        for token, weight in left.items():
            numerator += weight * right.get(token, 0.0)
        left_norm = math.sqrt(sum(weight * weight for weight in left.values()))
        right_norm = math.sqrt(sum(weight * weight for weight in right.values()))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    def _map_alternatives(
        self, alternatives: List[MedicationAlternative]
    ) -> Dict[str, MedicationAlternative]:
        mapped: Dict[str, MedicationAlternative] = {}
        for alternative in alternatives:
            mapped[alternative.original_medication.lower()] = alternative
        return mapped

    def _duplicate_names(self, meds: List[LineItem]) -> set[str]:
        duplicates: set[str] = set()
        counts = Counter(item.description.lower() for item in meds)
        for name, count in counts.items():
            if count > 1:
                duplicates.add(name)
        return duplicates
