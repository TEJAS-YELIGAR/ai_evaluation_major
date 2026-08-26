from sqlalchemy.orm import Session
from app.models.evaluation import Evaluation

def save(db: Session, booklet_id: int, question_no: int, result: dict):
    """Save Claude's evaluation result for one question."""
    feedback = result.get("feedback", "")

    for score in result.get("scores", []):
        evaluation = Evaluation(
            booklet_id=booklet_id,
            question_no=question_no,
            criterion=score.get("criterion", ""),
            awarded=float(score.get("awarded", 0)),
            max_marks=float(score.get("max", 0)),
            reason=score.get("reason", ""),
            feedback=feedback,
            overridden=False
        )
        db.add(evaluation)

    db.commit()

def get_by_booklet(db: Session, booklet_id: int):
    """Fetch all evaluation results for a booklet."""
    return db.query(Evaluation).filter(
        Evaluation.booklet_id == booklet_id
    ).order_by(Evaluation.question_no).all()

def override_mark(db: Session, eval_id: int, new_mark: float):
    """Evaluator overrides an AI mark."""
    evaluation = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
    if evaluation:
        evaluation.awarded = new_mark
        evaluation.overridden = True
        db.commit()
    return evaluation