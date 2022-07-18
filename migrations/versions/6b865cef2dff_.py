"""empty message

Revision ID: 6b865cef2dff
Revises: cf267146d799
Create Date: 2018-10-01 13:59:26.924828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6b865cef2dff"
down_revision = "cf267146d799"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "clinician",
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("created_by_", sa.String(), nullable=False),
        sa.Column("modified", sa.DateTime(), nullable=False),
        sa.Column("modified_by_", sa.String(), nullable=False),
        sa.Column("clinician_id", sa.String(length=36), nullable=False),
        sa.Column("login_active", sa.Boolean(), nullable=False),
        sa.Column("smartcard_number", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("clinician_id"),
    )

    op.create_index("clinician_id", "clinician", ["clinician_id"], unique=True)


def downgrade():
    op.drop_index("clinician_id", table_name="clinician")
    op.drop_table("clinician")
