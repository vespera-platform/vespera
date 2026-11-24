"""drop label

Revision ID: ab974da87927
Revises: 64b37483453e
Create Date: 2026-11-25 00:01:14.093752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab974da87927'
down_revision: Union[str, Sequence[str], None] = '64b37483453e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("targets", "label")


def downgrade() -> None:
    op.add_column("targets", sa.Column("label", sa.String(50), nullable=True))