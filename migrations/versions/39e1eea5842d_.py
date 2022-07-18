"""empty message

Revision ID: 39e1eea5842d
Revises: 6b865cef2dff
Create Date: 2018-10-01 14:16:37.552556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "39e1eea5842d"
down_revision = "6b865cef2dff"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "group",
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("created_by_", sa.String(), nullable=False),
        sa.Column("modified", sa.DateTime(), nullable=False),
        sa.Column("modified_by_", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "product",
        sa.Column("uuid", sa.String(length=36), nullable=False),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("created_by_", sa.String(), nullable=False),
        sa.Column("modified", sa.DateTime(), nullable=False),
        sa.Column("modified_by_", sa.String(), nullable=False),
        sa.Column("name", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "clinician_group",
        sa.Column("group_id", sa.String(), nullable=False),
        sa.Column("clinician_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["clinician_id"], ["clinician.uuid"]),
        sa.ForeignKeyConstraint(["group_id"], ["group.uuid"]),
        sa.PrimaryKeyConstraint("group_id", "clinician_id"),
    )

    op.create_table(
        "clinician_product",
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("clinician_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(["clinician_id"], ["clinician.uuid"]),
        sa.ForeignKeyConstraint(["product_id"], ["product.uuid"]),
        sa.PrimaryKeyConstraint("product_id", "clinician_id"),
    )


def downgrade():
    op.drop_table("clinician_product")
    op.drop_table("clinician_group")
    op.drop_table("product")
    op.drop_table("group")
