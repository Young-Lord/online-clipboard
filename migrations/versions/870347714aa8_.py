"""empty message

Revision ID: 870347714aa8
Revises: 
Create Date: 2023-12-23 16:53:53.950678

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '870347714aa8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('note',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('clip_version', sa.Integer(), nullable=False),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('readonly_name', sa.String(), nullable=False),
    sa.Column('timeout_seconds', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('readonly_name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('note')
    # ### end Alembic commands ###