from sqlalchemy import Column, Integer, ForeignKey, Text, UniqueConstraint
from app.db.base import Base


class QuestionPaperQuestion(Base):
    __tablename__ = "question_paper_questions"
    __table_args__ = (
        UniqueConstraint("subject_id", "question_no", name="uq_question_paper_subject_question"),
    )

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    question_no = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)