from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from app.db.base import Base

class Evaluation(Base):
    __tablename__ = "evaluations"

    id          = Column(Integer, primary_key=True, index=True)
    booklet_id  = Column(Integer, ForeignKey("booklets.id"), nullable=False)
    question_no = Column(Integer, nullable=False)
    criterion   = Column(String, nullable=False)
    awarded     = Column(Float, nullable=False)
    max_marks   = Column(Float, nullable=False)
    reason      = Column(Text)
    feedback    = Column(Text)
    overridden  = Column(Boolean, default=False)