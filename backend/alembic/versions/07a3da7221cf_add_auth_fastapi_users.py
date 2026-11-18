"""add auth (fastapi-users)

認証・ユーザ管理（src/auth/）用。
- users にパスワードのハッシュと is_active / is_superuser / is_verified を足す。
  既存のユーザはパスワードを持たない（空文字＝ログインできない）。フラグは既定値で埋める
- access_tokens: ログイン中のトークン（DB に持つのでログアウト等で即座に無効にできる）

Revision ID: 07a3da7221cf
Revises: dec24641e2ca
Create Date: 2026-11-18 16:23:48.012731

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "07a3da7221cf"
down_revision: str | None = "dec24641e2ca"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "access_tokens",
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("token"),
    )
    op.create_index(
        op.f("ix_access_tokens_created_at"),
        "access_tokens",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_access_tokens_user_id"), "access_tokens", ["user_id"], unique=False
    )
    op.add_column(
        "users",
        sa.Column(
            "hashed_password",
            sa.VARCHAR(length=255),
            server_default="",
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "is_superuser",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "is_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "is_verified")
    op.drop_column("users", "is_superuser")
    op.drop_column("users", "is_active")
    op.drop_column("users", "hashed_password")
    op.drop_index(op.f("ix_access_tokens_user_id"), table_name="access_tokens")
    op.drop_index(op.f("ix_access_tokens_created_at"), table_name="access_tokens")
    op.drop_table("access_tokens")
