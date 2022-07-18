"""empty message

Revision ID: e242ed5b58fd
Revises: 0484755f6866
Create Date: 2018-05-16 20:13:14.882633

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e242ed5b58fd"
down_revision = "0484755f6866"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("activation_code", "activation", ["code"], unique=True)
    op.create_index("patient_id", "user", ["patient_id"], unique=True)


def downgrade():
    op.drop_index("activation_code", table_name="activation")
    op.drop_index("patient_id", table_name="user")
