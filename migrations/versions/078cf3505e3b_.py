"""empty message

Revision ID: 078cf3505e3b
Revises: ddc2340e2872
Create Date: 2024-08-11 03:48:57.844061

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '078cf3505e3b'
down_revision = 'ddc2340e2872'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_blocked', sa.Boolean(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_column('is_blocked')

    # ### end Alembic commands ###
