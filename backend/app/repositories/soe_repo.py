from sqlalchemy.orm import Session
from app.models.soe import SchemeOfEvaluation

def save_items(db: Session, subject_id: int, items: list):
    # Delete existing SoE for this subject first (in case of re-upload)
    db.query(SchemeOfEvaluation).filter(
        SchemeOfEvaluation.subject_id == subject_id
    ).delete()

    # Save all new items
    for item in items:
        soe = SchemeOfEvaluation(
            subject_id=subject_id,
            question_no=item['question_no'],
            criterion_name=item['criterion_name'],
            max_marks=item['max_marks'],
            model_answer=item['model_answer']
        )
        db.add(soe)

    db.commit()

def get_by_subject(db: Session, subject_id: int):
    return db.query(SchemeOfEvaluation).filter(
        SchemeOfEvaluation.subject_id == subject_id
    ).order_by(SchemeOfEvaluation.question_no).all()

def exists(db: Session, subject_id: int) -> bool:
    return db.query(SchemeOfEvaluation).filter(
        SchemeOfEvaluation.subject_id == subject_id
    ).first() is not None