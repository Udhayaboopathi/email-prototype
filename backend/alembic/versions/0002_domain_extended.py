"""add domain storage quota cloudflare fields

Revision ID: 0002_domain_extended
Revises: 0001_initial
Create Date: 2026-05-04 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0002_domain_extended"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to the domains table (safe – all nullable or have defaults)
    with op.batch_alter_table("domains") as batch_op:
        batch_op.add_column(
            sa.Column("is_suspended", sa.Boolean(), nullable=False, server_default="false")
        )
        batch_op.add_column(
            sa.Column("storage_quota_mb", sa.BigInteger(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("cloudflare_zone_id", sa.String(64), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("domains") as batch_op:
        batch_op.drop_column("cloudflare_zone_id")
        batch_op.drop_column("storage_quota_mb")
        batch_op.drop_column("is_suspended")
