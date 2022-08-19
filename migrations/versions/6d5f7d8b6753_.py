"""empty message

Revision ID: 6d5f7d8b6753
Revises: 1482bf1bd1ff
Create Date: 2022-08-19 08:59:56.391437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d5f7d8b6753'
down_revision = '1482bf1bd1ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('seizure', 'aura_location')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('seizure', sa.Column('aura_location', sa.VARCHAR(length=256), autoincrement=False, nullable=True))
    # ### end Alembic commands ###