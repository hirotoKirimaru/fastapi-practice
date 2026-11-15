"""description of changes

Revision ID: 1874673658a2
Revises:
Create Date: 2024-04-21 22:36:45.663282

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import ForeignKey

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1874673658a2"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(1024)),
        sa.Column("email", sa.String(1024)),
        sa.Column("organization_id", sa.Integer),
        sa.Column("soft_destroyed_at", sa.DateTime),
        # sa.Column("user_name", sa.String(50), nullable=False),
    )
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer, nullable=False),
        sa.Column("title", sa.String(1024), nullable=True),
        sa.Column("user_id", sa.Integer, nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer, primary_key=True),
    )

    op.create_foreign_key(
        "fk_users_organization_id_organizations",
        "users",
        "organizations",
        ["organization_id"],
        ["id"],
    )

    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(1024)),
    )

    op.create_table(
        "dones",
        sa.Column("id", sa.Integer, ForeignKey("tasks.id"), primary_key=True),
    )

    op.create_table(
        "relation_timelines",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id_1", sa.Integer, ForeignKey("users.id")),
        sa.Column("user_id_2", sa.Integer, ForeignKey("users.id")),
        sa.Column("start_at", sa.DateTime),
        sa.Column("end_at", sa.DateTime),
        sa.UniqueConstraint(
            "user_id_1", "user_id_2", "start_at", "end_at", name="uq_user_ids_start_end"
        ),
    )

    # 「同じ2人の、終わっていない（end_at が NULL の）関係は1つだけ」を保証する。
    # MySQL には部分インデックスが無いので、以前は end_at_flag という仮想カラム
    # （end_at が NULL なら 1、そうでなければ NULL）を作ってそこにユニークインデックスを張っていた。
    # PostgreSQL は WHERE 付きのユニークインデックスで同じことが直接書ける。
    op.create_index(
        "uq_user_ids_start_end_flag",
        "relation_timelines",
        ["user_id_1", "user_id_2"],
        unique=True,
        postgresql_where=sa.text("end_at IS NULL"),
    )


def downgrade() -> None:
    # 外部キーで参照される側を後に消す（以前は posts / relation_timelines を消し忘れ、
    # users を posts より先に消そうとしていたため、PostgreSQL では downgrade が通らなかった）
    op.drop_table("relation_timelines")
    op.drop_table("dones")
    op.drop_table("tasks")
    op.drop_table("posts")
    op.drop_constraint(
        "fk_users_organization_id_organizations", "users", type_="foreignkey"
    )
    op.drop_table("organizations")
    op.drop_table("users")
