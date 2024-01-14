"""empty message

Revision ID: 86ce6a126c32
Revises: a1f0499a631d
Create Date: 2024-01-13 16:20:08.999842

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '86ce6a126c32'
down_revision = 'a1f0499a631d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_property', sa.String(), server_default='{}', nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notes', schema=None) as batch_op:
        batch_op.drop_column('user_property')

    # ### end Alembic commands ###