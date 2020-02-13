"""Restructured database

Revision ID: ed508d36fb7f
Revises: 
Create Date: 2020-02-11 14:40:05.079557

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed508d36fb7f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('attributes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userID', sa.Integer(), nullable=True),
    sa.Column('isAdmin', sa.Integer(), nullable=True),
    sa.Column('canFeed', sa.Integer(), nullable=True),
    sa.Column('style', sa.String(length=32), nullable=True),
    sa.Column('scheduleFeed', sa.Integer(), nullable=True),
    sa.Column('feedDays', sa.Integer(), nullable=True),
    sa.Column('feedHour', sa.Integer(), nullable=True),
    sa.Column('feedMinute', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['userID'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('attributes')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###