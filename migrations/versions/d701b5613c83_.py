"""empty message

Revision ID: d701b5613c83
Revises: 72d5e24215a4
Create Date: 2024-08-04 03:43:21.800368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd701b5613c83'
down_revision = '72d5e24215a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.alter_column('uuid',
               existing_type=sa.UUID(),
               type_=sa.String(length=36),
               existing_nullable=False)
        batch_op.drop_constraint('comments_uuid_key', type_='unique')

    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.alter_column('uuid',
               existing_type=sa.UUID(),
               type_=sa.String(length=36),
               existing_nullable=False)
        batch_op.drop_constraint('posts_uuid_key', type_='unique')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('uuid',
               existing_type=sa.UUID(),
               type_=sa.String(length=36),
               existing_nullable=False)
        batch_op.drop_constraint('users_uuid_key', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_unique_constraint('users_uuid_key', ['uuid'])
        batch_op.alter_column('uuid',
               existing_type=sa.String(length=36),
               type_=sa.UUID(),
               existing_nullable=False)

    with op.batch_alter_table('posts', schema=None) as batch_op:
        batch_op.create_unique_constraint('posts_uuid_key', ['uuid'])
        batch_op.alter_column('uuid',
               existing_type=sa.String(length=36),
               type_=sa.UUID(),
               existing_nullable=False)

    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.create_unique_constraint('comments_uuid_key', ['uuid'])
        batch_op.alter_column('uuid',
               existing_type=sa.String(length=36),
               type_=sa.UUID(),
               existing_nullable=False)

    # ### end Alembic commands ###