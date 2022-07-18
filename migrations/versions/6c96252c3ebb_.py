"""empty message

Revision ID: 6c96252c3ebb
Revises: 3e15f4bba5a8
Create Date: 2018-10-02 17:14:52.848727

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6c96252c3ebb"
down_revision = "3e15f4bba5a8"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("clinician", "smartcard_number")


def downgrade():
    op.add_column(
        "clinician",
        sa.Column(
            "smartcard_number",
            sa.VARCHAR(length=50),
            autoincrement=False,
            nullable=False,
        ),
    )
