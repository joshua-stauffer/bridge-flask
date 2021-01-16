"""added order to Quote

Revision ID: 6de521994213
Revises: f180338cc9e0
Create Date: 2021-01-16 12:34:29.792274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6de521994213'
down_revision = 'f180338cc9e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('quotes', sa.Column('order', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('quotes', 'order')
    # ### end Alembic commands ###
