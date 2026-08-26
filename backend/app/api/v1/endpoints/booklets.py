import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_admin, get_current_evaluator, get_current_staff
from app.repositories import booklet_repo, subject_repo, soe_repo
from app.schemas.booklet import BookletResponse
from app.services import evaluation_service
from typing import List
import uuid

router = APIRouter()

@router.post("/upload", response_model=BookletResponse)
def upload_booklet(
    background_tasks: BackgroundTasks,
    student_name: str = Form(...),
    usn: str = Form(...),
    subject_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    """Upload a student answer booklet for later evaluator processing."""
    subject = subject_repo.get_by_id(db, subject_id)
    if not subject:

        raise HTTPException(status_code=404, detail="Subject not found")

    # Validate SoE exists for this subject
    if not soe_repo.exists(db, subject_id):
        raise HTTPException(
            status_code=400,
            detail=f"No Scheme of Evaluation uploaded for {subject.name}. Upload SoE first."
        )

    # Validate file is PDF
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Please upload a PDF file")

    # Save PDF to uploads folder
    upload_dir = "/app/uploads"
    os.makedirs(upload_dir, exist_ok=True)

    # Unique filename to avoid conflicts
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    pdf_path = os.path.join(upload_dir, unique_name)

    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create booklet record in DB
    booklet = booklet_repo.create(
        db=db,
        student_name=student_name,
        usn=usn,
        subject_id=subject_id,
        pdf_path=pdf_path,
        uploaded_by=current_user.id
    )

    return booklet


@router.post("/{booklet_id}/evaluate")
def start_evaluation(
    booklet_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_evaluator)
):
    """Start AI evaluation when an evaluator chooses a pending booklet."""
    booklet = booklet_repo.get(db, booklet_id)
    if not booklet:
        raise HTTPException(status_code=404, detail="Booklet not found")
    if booklet.status == "completed":
        return {"booklet_id": booklet_id, "status": booklet.status}
    if booklet.status == "processing":
        return {"booklet_id": booklet_id, "status": booklet.status}
    if booklet.status not in ("pending", "failed"):
        raise HTTPException(status_code=400, detail="Booklet cannot be evaluated")

    booklet_repo.set_status(db, booklet_id, "pending")
    background_tasks.add_task(evaluation_service.run, booklet_id, db)
    return {"booklet_id": booklet_id, "status": "pending"}


@router.get("/{booklet_id}/status")
def get_status(
    booklet_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_staff)
):
    """
    Poll this endpoint every 5 seconds to check evaluation progress.
    Status: pending → processing → completed / failed
    """
    booklet = booklet_repo.get(db, booklet_id)
    if not booklet:
        raise HTTPException(status_code=404, detail="Booklet not found")

    return {
        "booklet_id": booklet_id,
        "status": booklet.status,
        "student_name": booklet.student_name,
        "usn": booklet.usn
    }


@router.get("", response_model=List[BookletResponse])
def list_booklets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_staff)
):
    """List all uploaded booklets with their status."""
    return booklet_repo.get_all(db)