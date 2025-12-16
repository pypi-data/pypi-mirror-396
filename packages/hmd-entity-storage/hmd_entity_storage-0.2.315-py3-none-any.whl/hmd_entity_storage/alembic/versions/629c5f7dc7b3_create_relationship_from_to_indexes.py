"""create_relationship_from_to_indexes

Revision ID: 629c5f7dc7b3
Revises: ffffc821fb8a
Create Date: 2024-12-11 10:46:41.145088

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "629c5f7dc7b3"
down_revision = "ffffc821fb8a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("relationship_from_id_index", "relationship", ["from_id"])
    op.create_index("relationship_to_id_index", "relationship", ["to_id"])
    pass


def downgrade():
    op.drop_index("relationship_from_id_index", "relationship")
    op.drop_index("relationship_to_id_index", "relationship")
    pass
