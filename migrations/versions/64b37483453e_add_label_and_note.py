"""add label and note

Revision ID: 64b37483453e
Revises: 235f88d6e648
Create Date: 2026-11-24 23:18:50.526673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64b37483453e'
down_revision: Union[str, Sequence[str], None] = '235f88d6e648'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("targets", sa.Column("label", sa.String(50), nullable=True))
    op.add_column("targets", sa.Column("note", sa.String(200), nullable=True))


def downgrade() -> None:
    op.drop_column("targets", "note")
    op.drop_column("targets", "label")
