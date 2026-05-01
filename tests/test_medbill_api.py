import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from medbill_checker.main import app


client = TestClient(app)


def test_home_page_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "MedBill Checker" in response.text


def test_sample_analysis_endpoint_returns_reviews():
    response = client.get("/api/v1/demo/sample-analysis")
    assert response.status_code == 200

    payload = response.json()
    analysis = payload["analysis"]
    assert analysis["filename"] == "sample_medical_bill.txt"
    assert analysis["coverage_summary"]["total_billed"] > 0
    assert len(analysis["medication_reviews"]) > 0
