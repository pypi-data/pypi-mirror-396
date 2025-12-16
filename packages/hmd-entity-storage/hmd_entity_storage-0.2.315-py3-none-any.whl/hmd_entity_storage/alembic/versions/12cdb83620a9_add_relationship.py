"""empty message

Revision ID: 12cdb83620a9
Revises: affe724897f1
Create Date: 2021-01-04 13:32:55.132727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "12cdb83620a9"
down_revision = "91c9eec02046"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(  # pylint: disable=no-member
        "relationship",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("content", sa.JSON()),
        sa.Column(
            "created_at",
            sa.DateTime,
            server_default=sa.sql.functions.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime),
        sa.Column(
            "is_deleted", sa.Boolean, server_default=sa.text("FALSE"), nullable=False
        ),
        sa.Column("from_id", sa.String(50), nullable=False),
        sa.Column("from_name", sa.String(255), nullable=False),
        sa.Column("to_id", sa.String(50), nullable=False),
        sa.Column("to_name", sa.String(255), nullable=False),
    )

    pass


def downgrade():
    op.drop_table("relationship")  # pylint: disable=no-member
    pass
