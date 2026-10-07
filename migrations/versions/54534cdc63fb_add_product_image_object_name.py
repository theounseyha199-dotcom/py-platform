"""add product image object name

Revision ID: 54534cdc63fb
Revises: 31380d6b6802
Create Date: 2026-10-07 16:58:21.007354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54534cdc63fb'
down_revision: Union[str, Sequence[str], None] = '31380d6b6802'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("products", sa.Column("image_object_name", sa.String(length=500), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("products", "image_object_name")
