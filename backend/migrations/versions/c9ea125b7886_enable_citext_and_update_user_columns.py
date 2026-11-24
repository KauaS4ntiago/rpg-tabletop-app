"""enable citext and update user columns

Revision ID: c9ea125b7886
Revises: ec42e5f452a8
Create Date: 2026-11-17 18:56:34.516996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c9ea125b7886'
down_revision: Union[str, Sequence[str], None] = 'ec42e5f452a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Habilita a extensão antes de utilizar o tipo CITEXT.
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")

    op.alter_column(
        "users",
        "username",
        existing_type=sa.VARCHAR(length=30),
        type_=postgresql.CITEXT(),
        existing_nullable=False,
    )

    op.alter_column(
        "users",
        "email",
        existing_type=sa.VARCHAR(length=254),
        type_=postgresql.CITEXT(),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "users",
        "email",
        existing_type=postgresql.CITEXT(),
        type_=sa.VARCHAR(length=254),
        existing_nullable=False,
    )

    op.alter_column(
        "users",
        "username",
        existing_type=postgresql.CITEXT(),
        type_=sa.VARCHAR(length=30),
        existing_nullable=False,
    )
    # ### end Alembic commands ###
