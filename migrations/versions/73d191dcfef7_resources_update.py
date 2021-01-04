"""resources update

Revision ID: 73d191dcfef7
Revises: bda2667b8244
Create Date: 2021-01-02 11:42:14.018399

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73d191dcfef7'
down_revision = 'bda2667b8244'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('resources', schema=None) as batch_op:
        batch_op.add_column(sa.Column('text', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('resources', schema=None) as batch_op:
        batch_op.drop_column('text')

    # ### end Alembic commands ###
