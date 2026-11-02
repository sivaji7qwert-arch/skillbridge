"""
certificate_service.py
-------------------------
Handles uploaded degree/certificate documents. Performs OCR text
extraction (Tesseract, via pytesseract) so a human reviewer has the
extracted text to work from quickly — but this module does NOT
claim to verify authenticity. It cannot check a certificate against
an issuing authority's database, detect forgeries, or confirm a
document is genuine. It only extracts readable text and stores the
document for a human (institution/admin) reviewer to act on.

Verification status is ALWAYS one of:
    Pending       — uploaded, not yet reviewed
    Needs Review  — OCR text extracted, but flagged ambiguous/low-confidence
    Verified      — a human reviewer has confirmed it (manual action only)
    Rejected      — a human reviewer has rejected it (manual action only)

Nothing in this module ever sets status to Verified automatically.
"""
import io
import os
from typing import Tuple

import pytesseract
from PIL import Image

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}

# Below this character count, OCR output is too sparse to be useful —
# flag for manual review rather than pretending we extracted something
# meaningful.
MIN_USEFUL_TEXT_LENGTH = 20


def ocr_image(file_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(image)


def ocr_pdf(file_bytes: bytes) -> str:
    """Extracts text from a PDF certificate. Tries direct text extraction
    first (fast, accurate for digitally-generated PDFs); falls back to
    a clear 'needs manual review' signal for scanned/image-only PDFs
    rather than attempting a heavier pdf2image+OCR pipeline that isn't
    guaranteed to be installed in every deployment environment."""
    import pdfplumber

    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_certificate_text(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """Returns (extracted_text, initial_status)."""
    ext = os.path.splitext(filename)[1].lower()

    if ext in SUPPORTED_IMAGE_EXTENSIONS:
        text = ocr_image(file_bytes)
    elif ext in SUPPORTED_PDF_EXTENSIONS:
        text = ocr_pdf(file_bytes)
    else:
        return "", "Needs Review"  # unsupported type — still stored, flagged for manual handling

    text = text.strip()
    initial_status = "Pending" if len(text) >= MIN_USEFUL_TEXT_LENGTH else "Needs Review"
    return text, initial_status
