"""drop note

Revision ID: d8781ab03b8d
Revises: ab974da87927
Create Date: 2026-11-25 00:19:02.993108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8781ab03b8d'
down_revision: Union[str, Sequence[str], None] = 'ab974da87927'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("targets", "note")


def downgrade() -> None:
    op.add_column("targets", sa.Column("note", sa.String(200), nullable=True))