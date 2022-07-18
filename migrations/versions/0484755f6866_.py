"""empty message

Revision ID: 0484755f6866
Revises: e5c976cf8a64
Create Date: 2018-04-27 23:51:47.960679

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0484755f6866"
down_revision = "e5c976cf8a64"
branch_labels = None
depends_on = None


def upgrade():

    op.add_column(
        "activation", sa.Column("hashed_otp", sa.LargeBinary(), nullable=False)
    )
    op.add_column("activation", sa.Column("otp_salt", sa.String(), nullable=True))
    op.drop_column("activation", "otp")


def downgrade():

    op.drop_column("activation", "hashed_otp")
    op.drop_column("activation", "otp_salt")
    op.add_column(
        "activation",
        sa.Column("otp", sa.VARCHAR(length=10), autoincrement=False, nullable=True),
    )
