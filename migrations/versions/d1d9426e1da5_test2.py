"""test2

Revision ID: d1d9426e1da5
Revises: dd0b637da609
Create Date: 2024-08-01 01:15:20.038837

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1d9426e1da5'
down_revision = 'dd0b637da609'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('test_user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('usernamee', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('usernamee')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('test_user')
    # ### end Alembic commands ###
