"""Store product images in PostgreSQL.

Revision ID: 879cf27c1c0e
Revises: 54534cdc63fb
"""

from alembic import op
import sqlalchemy as sa


revision = "879cf27c1c0e"
down_revision = "54534cdc63fb"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "product_images",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("image_data", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.drop_column("products", "image_object_name")
    op.drop_column("products", "image_url")


def downgrade() -> None:
    op.add_column("products", sa.Column("image_url", sa.String(500), nullable=True))
    op.add_column("products", sa.Column("image_object_name", sa.String(500), nullable=True))
    op.drop_table("product_images")
