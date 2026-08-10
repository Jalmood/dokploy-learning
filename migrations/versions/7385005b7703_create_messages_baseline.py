"""Create messages baseline

Revision ID: 7385005b7703
Revises:
Create Date: 2026-08-10 14:30:17.775585
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.

revision = "7385005b7703"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "messages",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "message",
            sa.Text(),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=True
        ),
        sa.PrimaryKeyConstraint("id")
    )


def downgrade():
    op.drop_table("messages")