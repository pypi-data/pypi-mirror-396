"""add_name_index

Revision ID: bdf0a12db196
Revises: 12cdb83620a9
Create Date: 2022-04-07 15:06:16.461174

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bdf0a12db196"
down_revision = "12cdb83620a9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("name_index", "entity", ["name"])
    pass


def downgrade():
    op.drop_index("name_index", "entity")
    pass
