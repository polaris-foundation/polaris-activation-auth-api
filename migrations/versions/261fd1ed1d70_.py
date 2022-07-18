"""empty message

Revision ID: 261fd1ed1d70
Revises: f630f7951d5e
Create Date: 2018-12-07 15:57:32.796691

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '261fd1ed1d70'
down_revision = 'f630f7951d5e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('device', sa.Column('active', sa.Boolean(), nullable=False, server_default='1'))


def downgrade():
    op.drop_column('device', 'active')
