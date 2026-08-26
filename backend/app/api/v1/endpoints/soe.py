from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_admin, get_current_user
from app.repositories import subject_repo, soe_repo
from app.schemas.soe import SoEResponse, SoEItem
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

    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Please upload an Excel file (.xlsx)")
    if not question_paper.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Please upload the question paper as a PDF")

    # Read Excel file
    contents = file.file.read()
    wb = openpyxl.load_workbook(io.BytesIO(contents))
    ws = wb.active

    items = []
    for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True)):
        # Skip empty rows
        if not row[0]:
            continue
        items.append({
            'question_no':   int(row[0]),
            'criterion_name': str(row[1]),
            'max_marks':     float(row[2]),
            'model_answer':  str(row[3])
        })

    if not items:
        raise HTTPException(status_code=400, detail="Excel file is empty or wrong format")

    soe_repo.save_items(db, subject_id, items)

    upload_dir = "/app/uploads/question_papers"
    os.makedirs(upload_dir, exist_ok=True)
    paper_path = os.path.join(upload_dir, f"{subject_id}_{uuid.uuid4()}_{question_paper.filename}")
    with open(paper_path, "wb") as buffer:
        shutil.copyfileobj(question_paper.file, buffer)
    subject.question_paper_path = paper_path
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