from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.db.base import Base

class Subject(Base):
    __tablename__ = "subjects"

    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String, nullable=False)
    subject_code = Column(String, nullable=False)  # e.g. BCS305
    semester     = Column(String, nullable=False)  # e.g. 5
    scheme_year  = Column(String, nullable=False)  # e.g. 2022
    department   = Column(String, nullable=False)
    question_paper_path = Column(String, nullable=True)
    question_paper_text = Column(Text, nullable=True)
    created_by   = Column(Integer, ForeignKey("users.id"))
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    @property
    def question_paper_uploaded(self):
        return bool(self.question_paper_path)