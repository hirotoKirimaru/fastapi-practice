"""description of changes

Revision ID: 1874673658a2
Revises:
Create Date: 2024-04-21 22:36:45.663282

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy import ForeignKey

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1874673658a2"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(1024)),
        sa.Column("email", sa.String(1024)),
        sa.Column("organization_id", sa.Integer),
        sa.Column("soft_destroyed_at", sa.DATETIME),
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
        sa.Column("start_at", sa.DATETIME),
        sa.Column("end_at", sa.DATETIME),
        sa.UniqueConstraint(
            "user_id_1", "user_id_2", "start_at", "end_at", name="uq_user_ids_start_end"
        ),
    )
    # 仮想カラムを追加
    op.execute(
        """
    ALTER TABLE relation_timelines 
    ADD COLUMN end_at_flag TINYINT AS (IF(end_at IS NULL, 1, null)) VIRTUAL
    """
    )

    # ユニークインデックスを追加
    op.create_index(
        "uq_user_ids_start_end_flag",
        "relation_timelines",
        ["user_id_1", "user_id_2", "end_at_flag"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("organizations")
    op.drop_table("tasks")
    op.drop_table("dones")
