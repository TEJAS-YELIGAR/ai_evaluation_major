# This file imports all models so Alembic can detect them
# Import this ONLY in alembic/env.py — nowhere else

from app.models.user import User
from app.models.subject import Subject
from app.models.soe import SchemeOfEvaluation
from app.models.booklet import Booklet
from app.models.evaluation import Evaluation