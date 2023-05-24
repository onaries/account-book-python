"""empty message

Revision ID: d0f374378b03
Revises: 662a01341658
Create Date: 2023-05-16 14:16:57.530213

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d0f374378b03"
down_revision = "662a01341658"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "memos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_memos_id"), "memos", ["id"], unique=False)
    op.add_column("statements", sa.Column("is_fixed", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("statements", "is_fixed")
    op.drop_index(op.f("ix_memos_id"), table_name="memos")
    op.drop_table("memos")
    # ### end Alembic commands ###
