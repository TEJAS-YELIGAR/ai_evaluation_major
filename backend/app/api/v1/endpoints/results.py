from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_evaluator, get_current_staff
from app.repositories import booklet_repo, evaluation_repo, subject_repo, soe_repo
from app.repositories import question_paper_repo
from app.schemas.booklet import (
    FullEvaluationResponse, QuestionResult,
    CriterionScore, OverrideRequest, FinalizeRequest
)

router = APIRouter()

@router.get("/{booklet_id}", response_model=FullEvaluationResponse)
def get_results(
    booklet_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_staff)
):
    booklet = booklet_repo.get(db, booklet_id)
    if not booklet:
        raise HTTPException(status_code=404, detail="Booklet not found")

    subject = subject_repo.get_by_id(db, booklet.subject_id)
    evaluations = evaluation_repo.get_by_booklet(db, booklet_id)
    soe_items = soe_repo.get_by_subject(db, booklet.subject_id)

    questions_map = {}
    for ev in evaluations:
        if ev.question_no not in questions_map:
            questions_map[ev.question_no] = []
        questions_map[ev.question_no].append(ev)

    question_nos = sorted(set(question.question_no for question in soe_items) | set(questions_map))
    paper_questions = {
        question.question_no: question.question_text
        for question in question_paper_repo.get_by_subject(db, booklet.subject_id)
    }

    questions = []
    paper_questions = {
        question.question_no: question.question_text
        for question in question_paper_repo.get_by_subject(db, booklet.subject_id)
    }
    total_awarded = 0
    total_max = 0

    for q_no in question_nos:
        scores = questions_map.get(q_no, [])
        q_awarded = sum(s.awarded for s in scores)
        q_max = sum(s.max_marks for s in soe_items if s.question_no == q_no)
        if not q_max:
            q_max = sum(s.max_marks for s in scores)
        total_awarded += q_awarded
        total_max += q_max

        questions.append(QuestionResult(
            question_no=q_no,
            question_text=paper_questions.get(q_no),
            scores=[CriterionScore(
                id=s.id,
                criterion=s.criterion,
                awarded=s.awarded,
                max_marks=s.max_marks,
                reason=s.reason,
                overridden=s.overridden
            ) for s in scores],
            question_total=q_awarded,
            question_max=q_max,
            feedback=scores[0].feedback if scores else None
        ))

    return FullEvaluationResponse(
        booklet_id=booklet_id,
        subject_id=booklet.subject_id,
        student_name=booklet.student_name,
        usn=booklet.usn,
        subject_name=subject.name if subject else "Unknown",
        subject_code=subject.subject_code if subject else "",
        status=booklet.status,
        is_finalized=booklet.is_finalized,
        total_awarded=total_awarded,
        total_max=total_max,
        questions=questions
    )

@router.put("/override")
def override_mark(
    request: OverrideRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_evaluator)
):
    if request.new_mark < 0:
        raise HTTPException(
            status_code=400, detail="Mark cannot be negative"
        )
    result = evaluation_repo.override_mark(
        db, request.evaluation_id, request.new_mark
    )
    if not result:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Mark overridden", "new_mark": request.new_mark}

@router.post("/finalize")
def finalize_evaluation(
    request: FinalizeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_evaluator)
):
    """
    Evaluator clicks Done → marks booklet as finalized.
    Shows ✅ beside student in the list.
    """
    booklet = booklet_repo.get(db, request.booklet_id)
    if not booklet:
        raise HTTPException(status_code=404, detail="Booklet not found")

    if booklet.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Can only finalize completed evaluations"
        )

    booklet_repo.finalize(db, request.booklet_id, current_user.id)
    return {"message": "Evaluation finalized", "booklet_id": request.booklet_id}