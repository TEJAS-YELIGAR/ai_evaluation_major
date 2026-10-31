from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.booklet import Booklet
from app.models.evaluation import Evaluation
from app.utils.evaluation_utils import build_module_results
from datetime import datetime, timezone
from typing import Optional

def create(db: Session, student_name: Optional[str], usn: str,
           subject_id: int, pdf_path: str, uploaded_by: int):
    booklet = Booklet(
        student_name=student_name or usn,
        usn=usn,
        subject_id=subject_id,
        pdf_path=pdf_path,
        status="pending",
        uploaded_by=uploaded_by
    )
    db.add(booklet)
    db.commit()
    db.refresh(booklet)
    return booklet

def get(db: Session, booklet_id: int):
    return db.query(Booklet).filter(Booklet.id == booklet_id).first()

def set_status(db: Session, booklet_id: int, status: str):
    booklet = db.query(Booklet).filter(Booklet.id == booklet_id).first()
    if booklet:
        booklet.status = status
        db.commit()
    return booklet

def get_all(db: Session):
    return db.query(Booklet).order_by(Booklet.created_at.desc()).all()

def get_students_by_subject(db: Session, subject_id: int):
    """Get all students (booklets) for a subject with their marks."""
    booklets = db.query(Booklet).filter(
        Booklet.subject_id == subject_id
    ).order_by(Booklet.student_name).all()

    result = []
    for b in booklets:
        # Get total marks if evaluated
        total_awarded = None
        total_max = None
        if b.status == "completed":
            question_scores = db.query(
                Evaluation.question_no,
                func.sum(Evaluation.awarded)
            ).filter(Evaluation.booklet_id == b.id).group_by(
                Evaluation.question_no
            ).all()
            if question_scores:
                modules = build_module_results({
                    question_no: float(awarded)
                    for question_no, awarded in question_scores
                })
                total_awarded = sum(module["final_marks"] for module in modules)
                total_max = 100.0

        result.append({
            "booklet_id": b.id,
            "student_name": b.student_name,
            "usn": b.usn,
            "status": b.status,
            "is_finalized": b.is_finalized,
            "total_marks": total_awarded,
            "total_max": total_max,
            "evaluated_by_name": None
        })
    return result

def finalize(db: Session, booklet_id: int, evaluator_id: int):
    """Mark booklet as finalized by evaluator."""
    booklet = db.query(Booklet).filter(Booklet.id == booklet_id).first()
    if booklet:
        booklet.is_finalized = True
        booklet.status = "completed"
        booklet.evaluated_by = evaluator_id
        booklet.evaluated_at = datetime.now(timezone.utc)
        db.commit()
    return booklet