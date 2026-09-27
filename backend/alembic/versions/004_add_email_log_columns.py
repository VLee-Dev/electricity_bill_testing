"""Add email log columns

Revision ID: 004_add_email_log_columns
Revises: 003_seed_price_tiers
Create Date: 2026-09-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_add_email_log_columns'
down_revision: str = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    # Add recipient_email and subject columns to email_logs
    op.add_column('email_logs', sa.Column('recipient_email', sa.String(255), nullable=True))
    op.add_column('email_logs', sa.Column('subject', sa.String(500), nullable=True))


def downgrade():
    op.drop_column('email_logs', 'subject')
    op.drop_column('email_logs', 'recipient_email')
