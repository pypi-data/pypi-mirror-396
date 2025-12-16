"""create_is_deleted_indexes

Revision ID: ffffc821fb8a
Revises: bdf0a12db196
Create Date: 2024-12-11 10:42:26.220975

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ffffc821fb8a"
down_revision = "bdf0a12db196"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    CREATE INDEX entity_is_deleted_index
    ON entity (is_deleted)
    WHERE is_deleted = FALSE
    """
    )
    op.execute(
        """
    CREATE INDEX relationship_is_deleted_index
    ON relationship (is_deleted)
    WHERE is_deleted = FALSE
    """
    )
    pass


def downgrade():
    op.execute(
        """
    DROP INDEX entity_is_deleted_index
    """
    )
    op.execute(
        """
    DROP INDEX relationship_is_deleted_index
    """
    )
    pass
