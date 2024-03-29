"""empty message

Revision ID: e64f31246a4c
Revises: fd280dbb8b78
Create Date: 2024-01-29 16:19:41.846771

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e64f31246a4c'
down_revision = 'fd280dbb8b78'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('loans', 'interest_rate',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True)
    op.add_column('main_categories', sa.Column('asset_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'main_categories', 'assets', ['asset_id'], ['id'])
    op.add_column('main_categories_version', sa.Column('asset_id', sa.Integer(), autoincrement=False, nullable=True))
    op.alter_column('statements_version', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=True,
               autoincrement=False)
    op.alter_column('statements_version', 'date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True,
               autoincrement=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('statements_version', 'date',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False,
               autoincrement=False)
    op.alter_column('statements_version', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=False,
               autoincrement=False)
    op.drop_column('main_categories_version', 'asset_id')
    op.drop_constraint(None, 'main_categories', type_='foreignkey')
    op.drop_column('main_categories', 'asset_id')
    op.alter_column('loans', 'interest_rate',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True)
    # ### end Alembic commands ###
