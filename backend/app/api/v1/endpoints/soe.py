from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_admin, get_current_user
from app.repositories import subject_repo, soe_repo, question_paper_repo
from app.schemas.soe import SoEResponse, SoEItem, QuestionPaperResponse
from app.utils.pdf_utils import pdf_to_text_direct
from app.utils.question_paper_utils import split_question_paper
from app.utils.soe_utils import parse_question_reference
import openpyxl
import io
import os
import shutil
import uuid

router = APIRouter()

@router.post("/upload/{subject_id}")
def upload_soe(
    subject_id: int,
    file: UploadFile = File(...),
    question_paper: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    """
    Upload the Scheme of Evaluation and question paper for a subject.
    Admin only. Both files are used for evaluating booklets.

    Excel format (columns):
    question_no | criterion_name | max_marks | model_answer
    """
    subject = subject_repo.get_by_id(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    if not (file.filename or "").lower().endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Please upload an Excel file (.xlsx)")
    if not (question_paper.filename or "").lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Please upload the question paper as a PDF")

    items = []
    try:
        wb = openpyxl.load_workbook(io.BytesIO(file.file.read()), data_only=True)
        ws = wb.active
        for row_number, raw_row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            row = list(raw_row[:4]) + [None] * max(0, 4 - len(raw_row))
            if not any(value is not None and str(value).strip() for value in row):
                continue

            question_no, subquestion_label = parse_question_reference(row[0])
            criterion_name = str(row[1] or "").strip()
            if not criterion_name:
                raise ValueError(f"Missing criterion name in Excel row {row_number}")
            try:
                max_marks = float(row[2])
            except (TypeError, ValueError):
                raise ValueError(f"Invalid maximum marks in Excel row {row_number}") from None
            if max_marks <= 0:
                raise ValueError(f"Maximum marks must be greater than zero in Excel row {row_number}")

            if subquestion_label:
                criterion_name = f"Q{question_no}({subquestion_label}) - {criterion_name}"
            items.append({
                'question_no': question_no,
                'criterion_name': criterion_name,
                'max_marks': max_marks,
                'model_answer': str(row[3] or "").strip()
            })
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Could not read the SoE Excel file. Please upload a valid .xlsx workbook."
        ) from exc

    if not items:
        raise HTTPException(status_code=400, detail="Excel file is empty or wrong format")

    upload_dir = "/app/uploads/question_papers"
    os.makedirs(upload_dir, exist_ok=True)
    paper_path = os.path.join(
        upload_dir,
        f"{subject_id}_{uuid.uuid4()}_{os.path.basename(question_paper.filename or 'question-paper.pdf')}"
    )
    with open(paper_path, "wb") as buffer:
        shutil.copyfileobj(question_paper.file, buffer)
    try:
        question_paper_text = pdf_to_text_direct(paper_path).strip()
    except Exception as exc:
        os.remove(paper_path)
        raise HTTPException(status_code=400, detail="Could not read the question paper PDF") from exc
    questions = split_question_paper(question_paper_text)
    if not question_paper_text:
        os.remove(paper_path)
        raise HTTPException(status_code=400, detail="Question paper PDF contains no extractable text")
    if not questions:
        os.remove(paper_path)
        raise HTTPException(status_code=400, detail="Could not detect numbered questions in the question paper")

    soe_repo.save_items(db, subject_id, items)
    question_paper_repo.replace_questions(db, subject_id, questions)
    subject.question_paper_path = paper_path
    subject.question_paper_text = question_paper_text
    db.commit()

    return {
        "message": f"SoE uploaded successfully for {subject.name}",
        "subject_id": subject_id,
        "total_criteria": len(items)
    }

@router.get("/{subject_id}", response_model=SoEResponse)
def get_soe(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Fetch the saved Scheme of Evaluation for a subject."""
    subject = subject_repo.get_by_id(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    items = soe_repo.get_by_subject(db, subject_id)
    if not items:
        raise HTTPException(status_code=404, detail="No SoE uploaded for this subject yet")

    return SoEResponse(
        subject_id=subject_id,
        subject_name=subject.name,
        question_paper_uploaded=subject.question_paper_uploaded,
        items=[SoEItem(
            question_no=i.question_no,
            criterion_name=i.criterion_name,
            max_marks=i.max_marks,
            model_answer=i.model_answer
        ) for i in items]
    )

@router.get("/{subject_id}/questions", response_model=QuestionPaperResponse)
def get_question_paper_questions(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    subject = subject_repo.get_by_id(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    questions = question_paper_repo.get_by_subject(db, subject_id)
    return QuestionPaperResponse(
        subject_id=subject_id,
        subject_name=subject.name,
        question_paper_uploaded=subject.question_paper_uploaded,
        questions=[{
            "question_no": question.question_no,
            "question_text": question.question_text,
        } for question in questions],
    )


@router.get("/{subject_id}/question-paper")
def get_question_paper_file(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    subject = subject_repo.get_by_id(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    if not subject.question_paper_path or not os.path.isfile(subject.question_paper_path):
        raise HTTPException(status_code=404, detail="Question paper not found")
    return FileResponse(
        subject.question_paper_path,
        media_type="application/pdf",
        filename="question-paper.pdf",
    )