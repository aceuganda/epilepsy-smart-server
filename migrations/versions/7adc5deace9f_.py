"""empty message

Revision ID: 7adc5deace9f
Revises: e5cf426cbc4d
Create Date: 2023-02-22 15:09:29.386926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7adc5deace9f'
down_revision = 'e5cf426cbc4d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('dob', sa.String(), nullable=True))
    op.drop_column('user', 'age')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('user', 'dob')
    # ### end Alembic commands ###