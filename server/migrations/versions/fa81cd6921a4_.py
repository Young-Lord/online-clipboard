"""empty message

Revision ID: fa81cd6921a4
Revises: 43d84101f808
Create Date: 2024-01-29 16:54:51.272266

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa81cd6921a4'
down_revision = '43d84101f808'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('illegal_count', sa.Integer(), server_default=sa.text('0'), nullable=False))
        batch_op.add_column(sa.Column('ban_unitl', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.drop_column('ban_unitl')
        batch_op.drop_column('illegal_count')

    # ### end Alembic commands ###