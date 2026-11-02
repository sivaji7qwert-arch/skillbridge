import os
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database_sql import get_db
from app.models.db_models import Certificate, User
from app.services.certificate_service import extract_certificate_text
from app.utils.security import require_role

router = APIRouter(prefix="/api/certificates", tags=["certificates"])
settings = get_settings()


@router.post("/upload")
def upload_certificate(
    file: UploadFile = File(...),
    certificate_type: str = "Degree",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    file_bytes = file.file.read()
    text, initial_status = extract_certificate_text(file.filename, file_bytes)

    upload_dir = os.path.join(settings.UPLOAD_DIR, "certificates")
    os.makedirs(upload_dir, exist_ok=True)
    stored_name = f"{current_user.id}_{uuid.uuid4().hex[:8]}_{file.filename}"
    stored_path = os.path.join(upload_dir, stored_name)
    with open(stored_path, "wb") as f:
        f.write(file_bytes)

    cert = Certificate(
        student_id=current_user.id, file_path=stored_path,
        certificate_type=certificate_type, extracted_text=text, status=initial_status,
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)

    return {
        "certificate_id": cert.id, "status": cert.status.value if hasattr(cert.status, "value") else cert.status,
        "extracted_text_preview": text[:200],
        "note": "Uploaded and OCR-scanned. This does NOT confirm authenticity — a human reviewer "
                "(institution/admin) must verify it before it can be marked Verified.",
    }


@router.get("/mine")
def my_certificates(db: Session = Depends(get_db), current_user: User = Depends(require_role("student"))):
    certs = db.query(Certificate).filter_by(student_id=current_user.id).all()
    return [
        {"certificate_id": c.id, "certificate_type": c.certificate_type,
         "status": c.status.value if hasattr(c.status, "value") else c.status, "uploaded_at": c.uploaded_at}
        for c in certs
    ]


@router.get("/{certificate_id}")
def get_certificate(certificate_id: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("employer", "institution", "admin"))):
    """Employers/institutions/admins can view a certificate's verification
    status when evaluating a candidate — never the raw extracted text by
    default, to limit exposure of personal document contents."""
    cert = db.query(Certificate).filter_by(id=certificate_id).first()
    if cert is None:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return {
        "certificate_id": cert.id, "certificate_type": cert.certificate_type,
        "status": cert.status.value if hasattr(cert.status, "value") else cert.status,
        "uploaded_at": cert.uploaded_at,
    }


class ReviewRequest(BaseModel):
    status: str  # Verified | Rejected | Needs Review
    reviewer_note: Optional[str] = None


@router.patch("/{certificate_id}/review")
def review_certificate(
    certificate_id: str, req: ReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("institution", "admin")),
):
    """Only a human reviewer (institution or admin role) can set a
    certificate to Verified or Rejected — never an automated process."""
    cert = db.query(Certificate).filter_by(id=certificate_id).first()
    if cert is None:
        raise HTTPException(status_code=404, detail="Certificate not found")

    from app.models.db_models import VerificationStatus
    try:
        cert.status = VerificationStatus(req.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status '{req.status}'")

    cert.reviewer_note = req.reviewer_note
    from datetime import datetime
    cert.reviewed_at = datetime.utcnow()
    db.commit()

    return {"message": "Certificate reviewed", "status": cert.status.value}
