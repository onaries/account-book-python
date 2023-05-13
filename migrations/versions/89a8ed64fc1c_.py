"""empty message

Revision ID: 89a8ed64fc1c
Revises: ef7ddecbb86f
Create Date: 2023-05-07 17:32:10.980171

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "89a8ed64fc1c"
down_revision = "ef7ddecbb86f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "statements", sa.Column("account_card_id", sa.Integer(), nullable=True)
    )
    op.add_column("statements", sa.Column("asset_id", sa.Integer(), nullable=True))
    op.add_column("statements", sa.Column("loan_id", sa.Integer(), nullable=True))
    op.alter_column(
        "statements", "name", existing_type=sa.VARCHAR(length=255), nullable=False
    )
    op.alter_column(
        "statements", "date", existing_type=postgresql.TIMESTAMP(), nullable=False
    )
    op.create_foreign_key(None, "statements", "loans", ["loan_id"], ["id"])
    op.create_foreign_key(None, "statements", "assets", ["asset_id"], ["id"])
    op.create_foreign_key(
        None, "statements", "account_cards", ["account_card_id"], ["id"]
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "statements", type_="foreignkey")
    op.drop_constraint(None, "statements", type_="foreignkey")
    op.drop_constraint(None, "statements", type_="foreignkey")
    op.alter_column(
        "statements", "date", existing_type=postgresql.TIMESTAMP(), nullable=True
    )
    op.alter_column(
        "statements", "name", existing_type=sa.VARCHAR(length=255), nullable=True
    )
    op.drop_column("statements", "loan_id")
    op.drop_column("statements", "asset_id")
    op.drop_column("statements", "account_card_id")
    # ### end Alembic commands ###
