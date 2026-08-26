from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubjectCreate(BaseModel):
    name: str
    subject_code: str      # e.g. BCS305
    semester: str          # e.g. 5
    scheme_year: str       # e.g. 2022
    department: str

class SubjectResponse(BaseModel):
    id: int
    name: str
    subject_code: str
    semester: str
    scheme_year: str
    department: str
    question_paper_uploaded: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class SubjectFilter(BaseModel):
    scheme_year: Optional[str] = None
    semester: Optional[str] = None