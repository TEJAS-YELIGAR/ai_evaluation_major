"""add question paper questions

Revision ID: d7e4f1a2b3c4
Revises: c6a1d9e4f2b0
Create Date: 2026-08-26
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "d7e4f1a2b3c4"
down_revision: Union[str, None] = "c6a1d9e4f2b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("subjects", sa.Column("question_paper_text", sa.Text(), nullable=True))
    op.create_table(
        "question_paper_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_no", sa.Integer(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.UniqueConstraint("subject_id", "question_no", name="uq_question_paper_subject_question"),
    )
    op.create_index("ix_question_paper_questions_subject_id", "question_paper_questions", ["subject_id"])


def downgrade() -> None:
    op.drop_index("ix_question_paper_questions_subject_id", table_name="question_paper_questions")
    op.drop_table("question_paper_questions")
    op.drop_column("subjects", "question_paper_text")