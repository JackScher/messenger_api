"""empty message

Revision ID: 5eb8b67e1fbe
Revises: e5a23e4ef584
Create Date: 2024-08-03 23:37:44.107698

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5eb8b67e1fbe'
down_revision = 'e5a23e4ef584'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test_user',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(length=80), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='test_user_pkey'),
    sa.UniqueConstraint('username', name='test_user_username_key')
    )
    # ### end Alembic commands ###