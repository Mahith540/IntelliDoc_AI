from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from medbill_checker.models import AnalyzeResponse, CoverageRequest, InsurancePlan, ReportRequest
from medbill_checker.services.insurance import InsuranceChecker
from medbill_checker.services.pipeline import AnalysisPipeline
from medbill_checker.services.report import ReportService

app = FastAPI(title="MedBill Checker API", version="0.1.0")
pipeline = AnalysisPipeline()
insurance_checker = InsuranceChecker()
report_service = ReportService()
BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
DATA_DIR = BASE_DIR / "data"

app.mount("/web", StaticFiles(directory=str(WEB_DIR)), name="web")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.post("/api/v1/bills/analyze", response_model=AnalyzeResponse)
async def analyze_bill(
    bill_file: UploadFile = File(...),
    insurance_plan_json: Optional[str] = Form(default=None),
) -> AnalyzeResponse:
    payload = await bill_file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    plan = None
    if insurance_plan_json:
        try:
            plan = InsurancePlan.model_validate(json.loads(insurance_plan_json))
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid insurance_plan_json: {exc}") from exc

    try:
        analysis = pipeline.run(
            filename=bill_file.filename or "uploaded_bill",
            content_type=bill_file.content_type or "",
            payload=payload,
            plan=plan,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return AnalyzeResponse(analysis=analysis)


@app.post("/api/v1/coverage/check")
def check_coverage(request: CoverageRequest):
    summary = insurance_checker.evaluate(request.line_items, request.insurance_plan)
    return {"coverage_summary": summary}


@app.post("/api/v1/report/whatsapp")
def generate_whatsapp_report(request: ReportRequest):
    report = report_service.whatsapp_summary(request.analysis)
    return {"whatsapp_summary": report}


@app.get("/api/v1/demo/sample-analysis", response_model=AnalyzeResponse)
def sample_analysis() -> AnalyzeResponse:
    sample_path = DATA_DIR / "sample_medical_bill.txt"
    if not sample_path.exists():
        raise HTTPException(status_code=500, detail="Sample bill file not found.")

    text = sample_path.read_text()
    analysis = pipeline.run_from_text(filename=sample_path.name, text=text)
    return AnalyzeResponse(analysis=analysis)
