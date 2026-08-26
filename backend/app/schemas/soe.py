from pydantic import BaseModel
from typing import List

class SoEItem(BaseModel):
    question_no: int
    criterion_name: str
    max_marks: float
    model_answer: str

    model_config = {"protected_namespaces": ()}
class SoEResponse(BaseModel):
    subject_id: int
    subject_name: str
    question_paper_uploaded: bool = False
    items: List[SoEItem]

class QuestionPaperQuestion(BaseModel):
    question_no: int
    question_text: str

class QuestionPaperResponse(BaseModel):
    subject_id: int
    subject_name: str
    question_paper_uploaded: bool
    questions: List[QuestionPaperQuestion]