from __future__ import annotations

from typing import Optional

from medbill_checker.models import AnalysisResult, InsurancePlan
from medbill_checker.services.alternatives import MedicationAlternativeService
from medbill_checker.services.insurance import InsuranceChecker
from medbill_checker.services.ocr import OCRService
from medbill_checker.services.parser import BillParser
from medbill_checker.services.rag import MedicationRAGService
from medbill_checker.services.report import ReportService


class AnalysisPipeline:
    def __init__(self) -> None:
        self.ocr = OCRService()
        self.parser = BillParser()
        self.insurance = InsuranceChecker()
        self.alternatives = MedicationAlternativeService()
        self.rag = MedicationRAGService()
        self.report = ReportService()

    def run(self, filename: str, content_type: str, payload: bytes, plan: Optional[InsurancePlan] = None) -> AnalysisResult:
        text = self.ocr.extract_text(filename=filename, content_type=content_type, payload=payload)
        return self.run_from_text(filename=filename, text=text, plan=plan)

    def run_from_text(self, filename: str, text: str, plan: Optional[InsurancePlan] = None) -> AnalysisResult:
        parse_result = self.parser.parse(text)
        coverage = self.insurance.evaluate(parse_result.line_items, plan=plan)
        alternatives = self.alternatives.suggest(parse_result.line_items)
        medication_reviews = self.rag.review_medications(parse_result.line_items, alternatives)
        savings = round(sum(alt.estimated_monthly_savings for alt in alternatives), 2)

        analysis = AnalysisResult(
            filename=filename,
            extracted_text_chars=len(text),
            parse_result=parse_result,
            coverage_summary=coverage,
            medication_alternatives=alternatives,
            medication_reviews=medication_reviews,
            potential_savings_total=savings,
            whatsapp_summary="",
        )
        analysis.whatsapp_summary = self.report.whatsapp_summary(analysis)
        return analysis
