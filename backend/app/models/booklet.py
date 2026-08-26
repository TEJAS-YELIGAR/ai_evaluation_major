# from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
# from sqlalchemy.sql import func
# from app.db.base import Base

# class Booklet(Base):
#     __tablename__ = "booklets"

#     id           = Column(Integer, primary_key=True, index=True)
#     student_name = Column(String, nullable=False)
#     usn          = Column(String, nullable=False)
#     subject_id   = Column(Integer, ForeignKey("subjects.id"), nullable=False)
#     pdf_path     = Column(String, nullable=False)
#     status       = Column(String, default="pending")  # pending/processing/completed/failed
#     uploaded_by  = Column(Integer, ForeignKey("users.id"))
#     created_at   = Column(DateTime(timezone=True), server_default=func.now())



from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class Booklet(Base):
    __tablename__ = "booklets"

    id             = Column(Integer, primary_key=True, index=True)
    student_name   = Column(String, nullable=False)
    usn            = Column(String, nullable=False)
    subject_id     = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    pdf_path       = Column(String, nullable=False)
    status         = Column(String, default="pending")
    uploaded_by    = Column(Integer, ForeignKey("users.id"))
    evaluated_by   = Column(Integer, ForeignKey("users.id"), nullable=True)
    evaluated_at   = Column(DateTime(timezone=True), nullable=True)
    is_finalized   = Column(Boolean, default=False)
    created_at     = Column(DateTime(timezone=True), server_default=func.now())



