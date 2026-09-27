"""Initial schema - new feature-based structure

Revision ID: 001_initial
Revises:
Create Date: 2026-09-25 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create admins table
    op.create_table(
        'admins',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # Create households table
    op.create_table(
        'households',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('customer_code', sa.String(50), nullable=False, unique=True, index=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('address', sa.String(500), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('meter_number', sa.String(50), nullable=False, unique=True),
        sa.Column('registered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
    )

    # Create customers table
    op.create_table(
        'customers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('household_id', sa.String(36), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('must_change_password', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['household_id'], ['households.id']),
    )

    # Create meter_readings table
    op.create_table(
        'meter_readings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('household_id', sa.String(36), nullable=False, index=True),
        sa.Column('period', sa.String(7), nullable=False),
        sa.Column('old_reading', sa.Integer, nullable=False),
        sa.Column('new_reading', sa.Integer, nullable=False),
        sa.Column('consumption', sa.Integer, nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('recorded_by', sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(['household_id'], ['households.id']),
        sa.ForeignKeyConstraint(['recorded_by'], ['admins.id']),
        sa.UniqueConstraint('household_id', 'period', name='uq_household_period'),
        sa.CheckConstraint('new_reading >= old_reading', name='ck_reading_valid'),
    )

    # Create price_tiers table
    op.create_table(
        'price_tiers',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('tier_no', sa.Integer, nullable=False),
        sa.Column('kwh_from', sa.Integer, nullable=False),
        sa.Column('kwh_to', sa.Integer, nullable=True),
        sa.Column('unit_price', sa.Integer, nullable=False),
        sa.Column('effective_from', sa.Date, nullable=False),
        sa.Column('effective_to', sa.Date, nullable=True),
    )

    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('household_id', sa.String(36), nullable=False, index=True),
        sa.Column('meter_reading_id', sa.String(36), nullable=False, unique=True),
        sa.Column('subtotal', sa.BigInteger, nullable=False),
        sa.Column('vat_amount', sa.BigInteger, nullable=False),
        sa.Column('total_amount', sa.BigInteger, nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='unpaid'),
        sa.Column('issued_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('due_date', sa.Date, nullable=False),
        sa.ForeignKeyConstraint(['household_id'], ['households.id']),
        sa.ForeignKeyConstraint(['meter_reading_id'], ['meter_readings.id']),
    )

    # Create invoice_tier_details table
    op.create_table(
        'invoice_tier_details',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('invoice_id', sa.String(36), nullable=False, index=True),
        sa.Column('tier_no', sa.Integer, nullable=False),
        sa.Column('kwh_applied', sa.Integer, nullable=False),
        sa.Column('unit_price', sa.Integer, nullable=False),
        sa.Column('amount', sa.BigInteger, nullable=False),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
    )

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('invoice_id', sa.String(36), nullable=False, index=True),
        sa.Column('amount', sa.BigInteger, nullable=False),
        sa.Column('method', sa.String(50), nullable=False),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('confirmed_by', sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id']),
        sa.ForeignKeyConstraint(['confirmed_by'], ['admins.id']),
    )

    # Create email_logs table
    op.create_table(
        'email_logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('invoice_id', sa.String(36), nullable=True, index=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id']),
    )

    # Create system_config table
    op.create_table(
        'system_config',
        sa.Column('key', sa.String(100), primary_key=True),
        sa.Column('value', sa.Text, nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('email_logs')
    op.drop_table('system_config')
    op.drop_table('payments')
    op.drop_table('invoice_tier_details')
    op.drop_table('invoices')
    op.drop_table('price_tiers')
    op.drop_table('meter_readings')
    op.drop_table('customers')
    op.drop_table('households')
    op.drop_table('admins')
