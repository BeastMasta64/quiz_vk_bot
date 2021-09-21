"""added game.user_id

Revision ID: 9f728c6a3b21
Revises: 7e5a9af732e8
Create Date: 2021-09-21 16:35:04.578535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f728c6a3b21'
down_revision = '7e5a9af732e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('user_id', sa.Integer(), nullable=False))
    op.drop_column('games', 'chat_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('chat_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_column('games', 'user_id')
    # ### end Alembic commands ###