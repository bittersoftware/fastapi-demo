"""add content column to post table

Revision ID: dabda1be2a8f
Revises: f8fa1f040b13
Create Date: 2022-01-13 00:36:27.578341

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dabda1be2a8f"
down_revision = "f8fa1f040b13"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))


def downgrade():
    op.drop_column("posts", "content")
