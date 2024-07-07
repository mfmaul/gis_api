"""empty message

Revision ID: e01116f99fe1
Revises: 
Create Date: 2024-07-07 15:07:16.738981

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e01116f99fe1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_account',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uid', sa.String(length=36), nullable=True),
    sa.Column('first_name', sa.String(length=256), nullable=False),
    sa.Column('last_name', sa.String(length=256), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('username', sa.String(length=256), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('is_verified', sa.Integer(), nullable=True),
    sa.Column('authenticated', sa.Boolean(), nullable=True),
    sa.Column('api_key', sa.String(length=255), nullable=True),
    sa.Column('api_key_expires', sa.DateTime(), nullable=True),
    sa.Column('rowstatus', sa.Integer(), nullable=True),
    sa.Column('created_by', sa.String(length=100), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('modified_by', sa.String(length=100), nullable=True),
    sa.Column('modified_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('api_key'),
    sa.UniqueConstraint('uid'),
    sa.UniqueConstraint('username')
    )
    with op.batch_alter_table('user_account', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_account_email'), ['email'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_account', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_account_email'))

    op.drop_table('user_account')
    # ### end Alembic commands ###
