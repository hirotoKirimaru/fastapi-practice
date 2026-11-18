"""add users.hashed_password

ログイン（POST /login/access-token）用のパスワードのハッシュ。既存のユーザはパスワードを
持たないので NULL を許す（NULL のユーザはログインできない）。

Revision ID: 796c9f237c4d
Revises: dec24641e2ca
Create Date: 2026-11-18 16:10:30.083608

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "796c9f237c4d"
down_revision: str | None = "dec24641e2ca"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("hashed_password", sa.VARCHAR(length=255), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("users", "hashed_password")
