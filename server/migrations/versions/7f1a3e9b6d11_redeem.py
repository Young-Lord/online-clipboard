"""add redeem codes and records

Revision ID: 7f1a3e9b6d11
Revises: c3026b515bcc
Create Date: 2026-05-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f1a3e9b6d11'
down_revision = 'c3026b515bcc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'redeem_codes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('note', sa.String(), server_default='', nullable=False),
        sa.Column('benefits', sa.String(), server_default='{}', nullable=False),
        sa.Column('max_uses', sa.Integer(), server_default=sa.text('-1'), nullable=False),
        sa.Column('used_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('valid_until', sa.DateTime(), nullable=True),
        sa.Column('effect_duration_seconds', sa.Integer(), server_default=sa.text('-1'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('1'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('id'),
    )
    op.create_table(
        'redeem_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('note_id', sa.Integer(), nullable=False),
        sa.Column('redeem_code_id', sa.Integer(), nullable=False),
        sa.Column('benefits_snapshot', sa.String(), server_default='{}', nullable=False),
        sa.Column('activated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['note_id'], ['notes.id']),
        sa.ForeignKeyConstraint(['redeem_code_id'], ['redeem_codes.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id'),
    )


def downgrade():
    op.drop_table('redeem_records')
    op.drop_table('redeem_codes')
