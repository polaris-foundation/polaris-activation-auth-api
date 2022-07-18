"""empty message

Revision ID: e5c976cf8a64
Revises: 0f1c8ecf6351
Create Date: 2018-04-24 23:19:52.074317

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e5c976cf8a64"
down_revision = "0f1c8ecf6351"
branch_labels = None
depends_on = None


def upgrade():

    op.add_column(
        "activation",
        sa.Column(
            "attempts_count", sa.SmallInteger(), nullable=False, server_default="0"
        ),
    )


def downgrade():

    op.drop_column("activation", "attempts_count")
