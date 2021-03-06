"""empty message

Revision ID: c5c27dac9ce5
Revises: b5d17ad46869
Create Date: 2019-09-09 17:32:28.320105

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c5c27dac9ce5'
down_revision = 'b5d17ad46869'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('phone', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone'),
    sa.UniqueConstraint('username')
    )
    op.drop_table('stations')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stations',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('lat', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('lng', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=u'stations_pkey')
    )
    op.drop_table('users')
    # ### end Alembic commands ###
