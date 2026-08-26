"""add question paper path to subjects

Revision ID: c6a1d9e4f2b0
Revises: b3f8db0671dd
Create Date: 2026-08-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c6a1d9e4f2b0"
down_revision: Union[str, None] = "b3f8db0671dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("subjects", sa.Column("question_paper_path", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("subjects", "question_paper_path")