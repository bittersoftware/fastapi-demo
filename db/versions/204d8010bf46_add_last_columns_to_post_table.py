"""add last columns to post table

Revision ID: 204d8010bf46
Revises: dabda1be2a8f
Create Date: 2022-01-13 00:38:41.414510

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "204d8010bf46"
down_revision = "dabda1be2a8f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "posts",
        sa.Column("published", sa.Boolean(), nullable=False, server_default="TRUE"),
    )
    op.add_column(
        "posts",
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )


def downgrade():
    op.drop_column("posts", "published")
    op.drop_column("posts", "created_at")
