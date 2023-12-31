"""empty message

Revision ID: a6ceb33ee507
Revises: 
Create Date: 2023-07-22 02:02:53.216141

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6ceb33ee507'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fitbit_user_id', sa.String(length=100), nullable=False),
    sa.Column('logical_id', sa.String(length=100), nullable=True),
    sa.Column('access_token', sa.String(length=500), nullable=False),
    sa.Column('refresh_token', sa.String(length=500), nullable=False),
    sa.Column('expires_in', sa.String(length=50), nullable=False),
    sa.Column('scope', sa.String(length=15), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    # ### end Alembic commands ###
