"""empty message

Revision ID: 0f1c8ecf6351
Revises: 1f916524d61c
Create Date: 2018-04-18 16:03:22.189960

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0f1c8ecf6351"
down_revision = "1f916524d61c"
branch_labels = None
depends_on = None


def upgrade():

    op.add_column("activation", sa.Column("created_by_", sa.String(), nullable=False))
    op.add_column("activation", sa.Column("modified_by_", sa.String(), nullable=False))
    op.add_column("user", sa.Column("created_by_", sa.String(), nullable=False))
    op.add_column("user", sa.Column("modified_by_", sa.String(), nullable=False))


def downgrade():

    op.drop_column("user", "modified_by_")
    op.drop_column("user", "created_by_")
    op.drop_column("activation", "modified_by_")
    op.drop_column("activation", "created_by_")
