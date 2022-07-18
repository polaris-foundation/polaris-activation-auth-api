"""empty message

Revision ID: 569b95c34f29
Revises: 82e4ae6c4644
Create Date: 2018-11-12 09:27:49.026016

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "569b95c34f29"
down_revision = "82e4ae6c4644"
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table("user", "patient")


def downgrade():
    op.rename_table("patient", "user")
