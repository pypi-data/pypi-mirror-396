"""initial tables

Revision ID: affe724897f1
Revises: 
Create Date: 2020-11-20 09:27:07.984935

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "affe724897f1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # pylint: disable=no-member
    op.create_table(
        "entity_definition",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(75), nullable=False),
        sa.Column("qualified_name", sa.String(255)),
        sa.Column("definition", sa.JSON()),
    )
    op.create_table(
        "entity",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("entity_definition_id", sa.String),
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
    )

    with op.batch_alter_table("entity", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_entity_entity_definition",
            "entity_definition",
            ["entity_definition_id"],
            ["id"],
        )


def downgrade():
    # pylint: disable=no-member
    op.drop_table("entity_definition")
    op.drop_table("entity")
