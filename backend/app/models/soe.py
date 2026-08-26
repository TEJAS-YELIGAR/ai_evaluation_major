from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from app.db.base import Base

class SchemeOfEvaluation(Base):
    __tablename__ = "scheme_of_evaluation"

    id             = Column(Integer, primary_key=True, index=True)
    subject_id     = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    question_no    = Column(Integer, nullable=False)
    criterion_name = Column(String, nullable=False)
    max_marks      = Column(Float, nullable=False)
    model_answer   = Column(Text, nullable=False)