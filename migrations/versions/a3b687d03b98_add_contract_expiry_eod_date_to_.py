"""add contract_expiry_eod_date to clinician model

Revision ID: a3b687d03b98
Revises: 261fd1ed1d70
Create Date: 2019-03-05 16:36:18.938721

"""
from alembic import op
import sqlalchemy as sa

revision = 'a3b687d03b98'
down_revision = '261fd1ed1d70'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('clinician', sa.Column('contract_expiry_eod_date', sa.Date(), nullable=True))


def downgrade():
    op.drop_column('clinician', 'contract_expiry_eod_date')
