"""name_to_entity

Revision ID: 91c9eec02046
Revises: 12cdb83620a9
Create Date: 2021-01-04 13:42:09.321756

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "91c9eec02046"
down_revision = "affe724897f1"
branch_labels = None
depends_on = None


def upgrade():
    # pylint: disable=no-member
    with op.batch_alter_table("entity", schema=None) as batch_op:
        batch_op.add_column(sa.Column("name", sa.String(255), nullable=False))
        batch_op.drop_constraint("fk_entity_entity_definition")
    op.drop_table("entity_definition")
    pass


def downgrade():
    # pylint: disable=no-member
    op.create_table(
        "entity_definition",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("name", sa.String(75), nullable=False),
        sa.Column("qualified_name", sa.String(255)),
        sa.Column("definition", sa.JSON()),
    )
    op.create_foreign_key(
        "fk_entity_entity_definition",
        "entity",
        "entity_definition",
        ["entity_definition_id"],
        ["id"],
    )
    op.drop_column("entity", "name")
    pass
