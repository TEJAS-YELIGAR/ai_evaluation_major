from sqlalchemy.orm import Session
from app.models.subject import Subject
from typing import Optional

def create(db: Session, name: str, subject_code: str,
           semester: str, scheme_year: str,
           department: str, created_by: int):
    subject = Subject(
        name=name,
        subject_code=subject_code,
        semester=semester,
        scheme_year=scheme_year,
        department=department,
        created_by=created_by
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

def get_by_id(db: Session, subject_id: int):
    return db.query(Subject).filter(Subject.id == subject_id).first()

def get_all(db: Session):
    return db.query(Subject).all()

def get_by_name(db: Session, name: str):
    return db.query(Subject).filter(Subject.name == name).first()

def get_scheme_years(db: Session):
    """Get all unique scheme years."""
    results = db.query(Subject.scheme_year).distinct().all()
    return sorted([r[0] for r in results], reverse=True)

def get_semesters_by_year(db: Session, scheme_year: str):
    """Get all semesters for a scheme year."""
    results = db.query(Subject.semester).filter(
        Subject.scheme_year == scheme_year
    ).distinct().all()
    return sorted([r[0] for r in results])

def get_subjects_by_year_sem(db: Session, scheme_year: str, semester: str):
    """Get subjects for a specific year and semester."""
    return db.query(Subject).filter(
        Subject.scheme_year == scheme_year,
        Subject.semester == semester
    ).all()