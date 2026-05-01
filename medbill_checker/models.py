from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Category(str, Enum):
    medication = "medication"
    procedure = "procedure"
    lab = "lab"
    room = "room"
    misc = "misc"


class MedicationStatus(str, Enum):
    ok = "ok"
    review = "review"


class LineItem(BaseModel):
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0
    total_price: float = 0.0
    category: Category = Category.misc


class BillParseResult(BaseModel):
    line_items: List[LineItem]
    parsed_total: float = 0.0
    extraction_warnings: List[str] = Field(default_factory=list)


class InsurancePlan(BaseModel):
    provider_name: str = "Sample Insurance"
    in_network: bool = True
    deductible_remaining: float = 500.0
    oop_remaining: float = 3000.0
    coverage_percent_by_category: Dict[Category, float] = Field(
        default_factory=lambda: {
            Category.medication: 0.70,
            Category.procedure: 0.80,
            Category.lab: 0.75,
            Category.room: 0.60,
            Category.misc: 0.50,
        }
    )


class CoverageItem(BaseModel):
    description: str
    category: Category
    billed_amount: float
    estimated_allowed_amount: float
    estimated_insurance_pays: float
    estimated_patient_pays: float
    notes: List[str] = Field(default_factory=list)


class CoverageSummary(BaseModel):
    total_billed: float
    estimated_allowed_total: float
    estimated_insurance_total: float
    estimated_patient_total: float
    deductible_applied: float
    potential_flags: List[str] = Field(default_factory=list)
    items: List[CoverageItem]


class MedicationAlternative(BaseModel):
    original_medication: str
    alternative: str
    estimated_monthly_savings: float
    rationale: str
    confidence: float = 0.6


class RetrievalEvidence(BaseModel):
    title: str
    snippet: str
    score: float


class MedicationReview(BaseModel):
    medication_name: str
    status: MedicationStatus
    reason: str
    suggested_alternative: Optional[str] = None
    estimated_monthly_savings: float = 0.0
    evidence: List[RetrievalEvidence] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    filename: str
    extracted_text_chars: int
    parse_result: BillParseResult
    coverage_summary: CoverageSummary
    medication_alternatives: List[MedicationAlternative]
    medication_reviews: List[MedicationReview]
    potential_savings_total: float
    whatsapp_summary: str


class AnalyzeResponse(BaseModel):
    analysis: AnalysisResult


class CoverageRequest(BaseModel):
    line_items: List[LineItem]
    insurance_plan: Optional[InsurancePlan] = None


class ReportRequest(BaseModel):
    analysis: AnalysisResult
