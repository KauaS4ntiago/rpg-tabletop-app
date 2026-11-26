import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    __table_args__ = (
        # Ensures that the token expiration never exceeds the session limit.
        CheckConstraint(
            "expires_at <= absolute_expires_at",
            name="expiry_within_absolute_limit",
        ),
    )

    # Unique identifier for this refresh token record.
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    # Identifies the user who owns this token.
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Groups tokens belonging to the same login session.
    family_id: Mapped[uuid.UUID] = mapped_column(
        nullable=False,
        index=True,
    )

    # SHA-256 hash of the refresh token (never store the raw token).
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    # Individual expiration date of this refresh token.
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Maximum expiration date allowed for the entire session.
    absolute_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Date when this token record was created.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Date when this token was revoked or invalidated.
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ID of the token that replaced this one during rotation.
    replaced_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("refresh_tokens.id"),
        nullable=True,
    )

    # Explains why this token was revoked.
    revocation_reason: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )