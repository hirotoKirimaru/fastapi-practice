"""sync schema with models

モデルに追加されたのにマイグレーションが無かった差分を埋める（alembic check で検出したもの）。
- user_profiles テーブル / users.birth_day / users.salt の追加
- dones の外部キーに ON DELETE CASCADE
- posts.title / posts.user_id / tasks.title を NOT NULL に

Revision ID: dec24641e2ca
Revises: 1874673658a2
Create Date: 2026-11-15 07:59:05.206525

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "dec24641e2ca"
down_revision: str | None = "1874673658a2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_constraint(op.f("dones_id_fkey"), "dones", type_="foreignkey")
    # 名前を明示しておく（None だと downgrade で消す対象を指定できない）
    op.create_foreign_key(
        "dones_id_fkey", "dones", "tasks", ["id"], ["id"], ondelete="CASCADE"
    )
    op.alter_column(
        "posts", "title", existing_type=sa.VARCHAR(length=1024), nullable=False
    )
    op.alter_column("posts", "user_id", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column(
        "tasks", "title", existing_type=sa.VARCHAR(length=1024), nullable=False
    )
    op.add_column("users", sa.Column("birth_day", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("salt", sa.VARCHAR(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "salt")
    op.drop_column("users", "birth_day")
    op.alter_column(
        "tasks", "title", existing_type=sa.VARCHAR(length=1024), nullable=True
    )
    op.alter_column("posts", "user_id", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column(
        "posts", "title", existing_type=sa.VARCHAR(length=1024), nullable=True
    )
    op.drop_constraint("dones_id_fkey", "dones", type_="foreignkey")
    op.create_foreign_key(op.f("dones_id_fkey"), "dones", "tasks", ["id"], ["id"])
    op.drop_table("user_profiles")
