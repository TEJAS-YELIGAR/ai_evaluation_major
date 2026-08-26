from sqlalchemy.orm import Session
from app.models.question_paper import QuestionPaperQuestion


def replace_questions(db: Session, subject_id: int, questions: list[dict]):
    db.query(QuestionPaperQuestion).filter(
        QuestionPaperQuestion.subject_id == subject_id
    ).delete(synchronize_session=False)
    for question in questions:
        db.add(QuestionPaperQuestion(subject_id=subject_id, **question))


def get_by_subject(db: Session, subject_id: int):
    return db.query(QuestionPaperQuestion).filter(
        QuestionPaperQuestion.subject_id == subject_id
    ).order_by(QuestionPaperQuestion.question_no).all()