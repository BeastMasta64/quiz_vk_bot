"""changed game.used_questions to game.questions_id

Revision ID: 93e11b443217
Revises: 8dc828c0b364
Create Date: 2021-09-21 20:47:18.308280

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '93e11b443217'
down_revision = '8dc828c0b364'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('questions_id', postgresql.ARRAY(sa.Integer()), nullable=False))
    op.drop_column('games', 'used_questions')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column('used_questions', postgresql.ARRAY(sa.INTEGER()), autoincrement=False, nullable=False))
    op.drop_column('games', 'questions_id')
    # ### end Alembic commands ###
