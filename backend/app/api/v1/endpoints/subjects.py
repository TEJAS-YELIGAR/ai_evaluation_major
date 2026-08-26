from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_admin, get_current_user
from app.repositories import subject_repo
from app.schemas.subject import SubjectCreate, SubjectResponse
from typing import List

router = APIRouter()

@router.post("", response_model=SubjectResponse)
def create_subject(
    request: SubjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    """Create subject. Admin only."""
    return subject_repo.create(
        db=db,
        name=request.name,
        subject_code=request.subject_code,
        semester=request.semester,
        scheme_year=request.scheme_year,
        department=request.department,
        created_by=current_user.id
    )

@router.get("", response_model=List[SubjectResponse])
def list_subjects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return subject_repo.get_all(db)

@router.get("/scheme-years")
def get_scheme_years(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get all available scheme years. e.g. [2022, 2021, 2019]"""
    return subject_repo.get_scheme_years(db)

@router.get("/semesters/{scheme_year}")
def get_semesters(
    scheme_year: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get semesters for a scheme year. e.g. [5, 6, 7]"""
    return subject_repo.get_semesters_by_year(db, scheme_year)

@router.get("/filter/{scheme_year}/{semester}",
            response_model=List[SubjectResponse])
def get_subjects_filtered(
    scheme_year: str,
    semester: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get subjects for specific year + semester."""
    return subject_repo.get_subjects_by_year_sem(db, scheme_year, semester)

@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    subject = subject_repo.get_by_id(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.get("/{subject_id}/students")
def get_students(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Get all students with booklets for a subject."""
    subject = subject_repo.get_by_id(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    from app.repositories import booklet_repo
    return booklet_repo.get_students_by_subject(db, subject_id)