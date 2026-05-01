const uploadForm = document.getElementById("upload-form");
const sampleButton = document.getElementById("sample-btn");
const analyzeButton = document.getElementById("analyze-btn");
const fileInput = document.getElementById("bill-file");
const processingBlock = document.getElementById("processing");
const resultPanel = document.getElementById("result-panel");
const selectedFileEl = document.getElementById("selected-file");
const statusMessageEl = document.getElementById("status-message");
const successOverlay = document.getElementById("success-overlay");

const totalBilledEl = document.getElementById("total-billed");
const insurancePaysEl = document.getElementById("insurance-pays");
const patientPaysEl = document.getElementById("patient-pays");
const savingsEl = document.getElementById("savings");
const reviewCountEl = document.getElementById("review-count");
const medicationStatusList = document.getElementById("medication-status-list");
const alternativeList = document.getElementById("alternative-list");
const whatsappSummaryEl = document.getElementById("whatsapp-summary");

function money(value) {
  const num = Number(value || 0);
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setStatusMessage(text, isError = false) {
  if (!statusMessageEl) return;
  statusMessageEl.textContent = text || "";
  statusMessageEl.classList.toggle("error", Boolean(isError));
}

function setBusy(state) {
  if (state) {
    processingBlock.classList.remove("hidden");
    setStatusMessage("Analysis in progress...");
  } else {
    processingBlock.classList.add("hidden");
  }
  analyzeButton.disabled = state;
  sampleButton.disabled = state;
  if (fileInput) {
    fileInput.disabled = state;
  }
}

function showCompletionOverlay() {
  if (!successOverlay) return;
  successOverlay.classList.remove("hidden");
  requestAnimationFrame(() => successOverlay.classList.add("show"));
  window.setTimeout(() => {
    successOverlay.classList.remove("show");
    window.setTimeout(() => successOverlay.classList.add("hidden"), 260);
  }, 1400);
}

function animateNumber(el, value) {
  const target = Number(value || 0);
  const durationMs = 700;
  const startTs = performance.now();

  function tick(now) {
    const progress = Math.min((now - startTs) / durationMs, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = money(target * eased);
    if (progress < 1) {
      requestAnimationFrame(tick);
    }
  }

  requestAnimationFrame(tick);
}

function buildAlternativeRows(analysis) {
  const fromResponse = Array.isArray(analysis.medication_alternatives)
    ? analysis.medication_alternatives
    : [];

  if (fromResponse.length > 0) {
    return fromResponse;
  }

  const fromReviews = [];
  const seen = new Set();
  const reviews = Array.isArray(analysis.medication_reviews) ? analysis.medication_reviews : [];
  reviews.forEach((review) => {
    if (!review.suggested_alternative) return;
    const key = `${String(review.medication_name || "").toLowerCase()}|${String(
      review.suggested_alternative || "",
    ).toLowerCase()}`;
    if (seen.has(key)) return;
    seen.add(key);
    fromReviews.push({
      original_medication: review.medication_name,
      alternative: review.suggested_alternative,
      estimated_monthly_savings: Number(review.estimated_monthly_savings || 0),
      rationale: review.reason || "Lower-cost same-formula option was detected.",
    });
  });
  return fromReviews;
}

function renderAlternatives(analysis) {
  alternativeList.innerHTML = "";
  const alternatives = buildAlternativeRows(analysis);

  if (alternatives.length === 0) {
    const empty = document.createElement("article");
    empty.className = "alternative-card";
    empty.innerHTML = `
      <p class="alt-title">No strong alternative signal</p>
      <p class="alt-route">No same-formula lower-cost replacement was confidently detected for this bill.</p>
    `;
    alternativeList.appendChild(empty);
    return;
  }

  alternatives.forEach((alt, index) => {
    const card = document.createElement("article");
    card.className = "alternative-card";
    card.style.animationDelay = `${index * 70}ms`;
    card.innerHTML = `
      <div class="alt-top">
        <p class="alt-title">${escapeHtml(alt.original_medication || "Medication")}</p>
        <p class="alt-savings">${money(Number(alt.estimated_monthly_savings || 0))} saving</p>
      </div>
      <p class="alt-route">Suggested replacement: <strong>${escapeHtml(alt.alternative || "N/A")}</strong></p>
      <p class="alt-rationale">${escapeHtml(alt.rationale || "Lower-cost same-formula candidate detected.")}</p>
    `;
    alternativeList.appendChild(card);
  });
}

function renderMedicationReviews(reviews) {
  medicationStatusList.innerHTML = "";

  if (!reviews || reviews.length === 0) {
    const empty = document.createElement("article");
    empty.className = "status-card";
    empty.innerHTML = "<p class='status-name'>No medication line items detected.</p>";
    medicationStatusList.appendChild(empty);
    return;
  }

  let approvedCount = 0;
  let reviewCount = 0;

  reviews.forEach((review, index) => {
    const isApproved = review.status === "ok";
    if (isApproved) {
      approvedCount += 1;
    } else {
      reviewCount += 1;
    }

    const card = document.createElement("article");
    card.className = `status-card ${isApproved ? "status-ok" : "status-review"}`;
    card.style.animationDelay = `${index * 70}ms`;

    const badgeClass = isApproved ? "badge badge-approved" : "badge badge-review";
    const badgeText = isApproved ? "Approved" : "Needs Review";
    const altText = review.suggested_alternative
      ? `<p class="status-alt">Alternative: ${escapeHtml(review.suggested_alternative)} (${money(
          review.estimated_monthly_savings,
        )} potential saving)</p>`
      : "";

    const sources = Array.isArray(review.decision_sources) ? review.decision_sources.slice(0, 3) : [];
    const sourceChips = sources.map((source) => `<span class="meta-chip">${escapeHtml(source)}</span>`).join("");
    const confidenceChip = Number.isFinite(Number(review.confidence))
      ? `<span class="meta-chip">confidence ${Number(review.confidence).toFixed(2)}</span>`
      : "";

    card.innerHTML = `
      <div class="status-top">
        <p class="status-name">${escapeHtml(review.medication_name)}</p>
        <span class="${badgeClass}">${badgeText}</span>
      </div>
      <p class="status-reason">${escapeHtml(review.reason || "")}</p>
      ${altText}
      <div class="status-meta">
        ${confidenceChip}
        ${sourceChips}
      </div>
    `;

    medicationStatusList.appendChild(card);
  });

  reviewCountEl.textContent = `${approvedCount} approved | ${reviewCount} needs review`;
}

function renderAnalysis(analysis) {
  animateNumber(totalBilledEl, analysis.coverage_summary.total_billed);
  animateNumber(insurancePaysEl, analysis.coverage_summary.estimated_insurance_total);
  animateNumber(patientPaysEl, analysis.coverage_summary.estimated_patient_total);
  animateNumber(savingsEl, analysis.potential_savings_total);
  whatsappSummaryEl.textContent = analysis.whatsapp_summary || "No summary generated.";

  renderMedicationReviews(analysis.medication_reviews);
  renderAlternatives(analysis);
  resultPanel.classList.remove("hidden");
  showCompletionOverlay();
  resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function parseError(response) {
  try {
    const payload = await response.json();
    return payload.detail || "Request failed.";
  } catch (err) {
    return "Request failed.";
  }
}

uploadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!fileInput.files || fileInput.files.length === 0) {
    setStatusMessage("Please select a bill file first.", true);
    return;
  }

  const formData = new FormData();
  formData.append("bill_file", fileInput.files[0]);

  setBusy(true);
  try {
    const response = await fetch("/api/v1/bills/analyze", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const message = await parseError(response);
      throw new Error(message);
    }

    const payload = await response.json();
    renderAnalysis(payload.analysis);
    setStatusMessage("Analysis complete.");
  } catch (error) {
    setStatusMessage(error.message || "Upload failed.", true);
  } finally {
    setBusy(false);
  }
});

sampleButton.addEventListener("click", async () => {
  setBusy(true);
  try {
    const response = await fetch("/api/v1/demo/sample-analysis", { method: "GET" });
    if (!response.ok) {
      const message = await parseError(response);
      throw new Error(message);
    }
    const payload = await response.json();
    renderAnalysis(payload.analysis);
    setStatusMessage("Sample analysis complete.");
  } catch (error) {
    setStatusMessage(error.message || "Sample pipeline failed.", true);
  } finally {
    setBusy(false);
  }
});

fileInput.addEventListener("change", () => {
  if (!fileInput.files || fileInput.files.length === 0) {
    selectedFileEl.textContent = "No file selected yet.";
    return;
  }
  selectedFileEl.textContent = `Selected: ${fileInput.files[0].name}`;
});
