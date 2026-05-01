from __future__ import annotations

from medbill_checker.models import AnalysisResult


class ReportService:
    def whatsapp_summary(self, analysis: AnalysisResult) -> str:
        coverage = analysis.coverage_summary
        top_items = sorted(coverage.items, key=lambda i: i.billed_amount, reverse=True)[:3]

        lines = [
            "MedBill Checker - Quick Summary",
            f"File: {analysis.filename}",
            f"Line items found: {len(analysis.parse_result.line_items)}",
            f"Total billed: ${coverage.total_billed:,.2f}",
            f"Estimated insurance: ${coverage.estimated_insurance_total:,.2f}",
            f"Estimated patient cost: ${coverage.estimated_patient_total:,.2f}",
            f"Potential savings: ${analysis.potential_savings_total:,.2f}",
            "",
            "Top charges:",
        ]

        for item in top_items:
            lines.append(f"- {item.description}: ${item.billed_amount:,.2f}")

        if analysis.medication_alternatives:
            lines.append("")
            lines.append("Medication cost-reduction alternatives:")
            for alt in analysis.medication_alternatives[:3]:
                lines.append(
                    f"- {alt.original_medication} -> {alt.alternative} "
                    f"(~${alt.estimated_monthly_savings:,.0f}/month)")

        if analysis.medication_reviews:
            lines.append("")
            lines.append("Medication status:")
            for review in analysis.medication_reviews[:4]:
                marker = "OK" if review.status.value == "ok" else "REVIEW"
                lines.append(f"- [{marker}] {review.medication_name}: {review.reason}")

        if coverage.potential_flags:
            lines.append("")
            lines.append("Billing flags to review:")
            for flag in coverage.potential_flags[:3]:
                lines.append(f"- {flag}")

        lines.append("")
        lines.append("Action: ask hospital billing for itemized CPT/HCPCS + insurer pre-approval check.")
        return "\n".join(lines)
