from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BookletResponse(BaseModel):
    id: int
    student_name: str
    usn: str
    subject_id: int
    status: str
    is_finalized: bool
    evaluated_by: Optional[int]
    evaluated_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class StudentListItem(BaseModel):
    booklet_id: int
    student_name: str
    usn: str
    status: str
    is_finalized: bool
    total_marks: Optional[float]
    total_max: Optional[float]
    evaluated_by_name: Optional[str]

class CriterionScore(BaseModel):
    id: int
    criterion: str
    awarded: float
    max_marks: float
    reason: Optional[str]
    overridden: bool

    class Config:
        from_attributes = True

class QuestionResult(BaseModel):
    question_no: int
    question_text: Optional[str] = None
    module_no: int
    selected_for_module: bool
    selection_status: str
    scores: List[CriterionScore]
    question_total: float
    question_max: float
    feedback: Optional[str]

class ModuleResult(BaseModel):
    module_no: int
    question_nos: List[int]
    question_scores: List[float]
    selected_questions: List[int]
    selection_status: str
    final_marks: float
    max_marks: float

class FullEvaluationResponse(BaseModel):
    booklet_id: int
    subject_id: int
    student_name: str
    usn: str
    subject_name: str
    subject_code: str
    status: str
    is_finalized: bool
    total_awarded: float
    total_max: float
    questions: List[QuestionResult]
    modules: List[ModuleResult]
    selected_questions: List[int]
    not_selected_questions: List[int]

class OverrideRequest(BaseModel):
    evaluation_id: int
    new_mark: float

class FinalizeRequest(BaseModel):
    booklet_id: int