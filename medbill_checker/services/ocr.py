from __future__ import annotations

import io
from typing import List

from pypdf import PdfReader


class OCRService:
    """Best-effort text extraction from PDF/image uploads."""

    def extract_text(self, filename: str, content_type: str, payload: bytes) -> str:
        lowered_name = filename.lower()
        lowered_type = (content_type or "").lower()

        if lowered_name.endswith(".pdf") or "pdf" in lowered_type:
            text = self._extract_pdf_text(payload)
            if text.strip():
                return text
            return self._ocr_pdf_pages(payload)

        if any(ext in lowered_name for ext in (".png", ".jpg", ".jpeg", ".webp")) or "image" in lowered_type:
            return self._ocr_image(payload)

        raise ValueError("Unsupported file type. Upload a PDF or image.")

    def _extract_pdf_text(self, payload: bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(payload))
        except Exception as exc:  # pragma: no cover
            raise ValueError("Unable to read PDF file.") from exc

        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages)

    def _ocr_pdf_pages(self, payload: bytes) -> str:
        try:
            import pytesseract
            from pdf2image import convert_from_bytes
        except Exception as exc:
            raise ValueError(
                "PDF had no extractable text and OCR fallback is unavailable. "
                "Install pytesseract + pdf2image + tesseract."
            ) from exc

        images = convert_from_bytes(payload)
        texts: List[str] = []
        for image in images:
            texts.append(pytesseract.image_to_string(image))
        return "\n".join(texts)

    def _ocr_image(self, payload: bytes) -> str:
        try:
            from PIL import Image
            import pytesseract
        except Exception as exc:
            raise ValueError(
                "Image OCR is unavailable. Install pillow + pytesseract + tesseract."
            ) from exc

        try:
            image = Image.open(io.BytesIO(payload))
            return pytesseract.image_to_string(image)
        except Exception as exc:  # pragma: no cover
            raise ValueError("Unable to OCR image file.") from exc
