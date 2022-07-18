"""empty message

Revision ID: 3e15f4bba5a8
Revises: 39e1eea5842d
Create Date: 2018-10-02 17:13:33.397291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3e15f4bba5a8"
down_revision = "39e1eea5842d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "clinician",
        sa.Column("send_entry_identifier", sa.String(length=50), nullable=True),
    )


def downgrade():
    op.drop_column("clinician", "send_entry_identifier")
