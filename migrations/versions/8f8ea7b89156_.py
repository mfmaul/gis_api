"""empty message

Revision ID: 8f8ea7b89156
Revises: e01116f99fe1
Create Date: 2024-07-07 23:15:35.909948

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f8ea7b89156'
down_revision = 'e01116f99fe1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_account', schema=None) as batch_op:
        batch_op.add_column(sa.Column('register_key', sa.String(length=255), nullable=True))
        batch_op.create_index(batch_op.f('ix_user_account_register_key'), ['register_key'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_account', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_account_register_key'))
        batch_op.drop_column('register_key')

    # ### end Alembic commands ###
