import uuid

from datetime import UTC, datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RefreshToken

class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self, 
        *, 
        user_id: uuid.UUID, 
        family_id: uuid.UUID, 
        token_hash: str, 
        expires_at: datetime, 
        absolute_expires_at: datetime,
    ) -> RefreshToken:
        
        refresh_token = RefreshToken(
            user_id=user_id, 
            family_id=family_id, 
            token_hash=token_hash, 
            expires_at=expires_at, 
            absolute_expires_at=absolute_expires_at
        )
        
        self._session.add(refresh_token)
        await self._session.flush()
            
        return refresh_token
    
    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        
        result = await self._session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash
            ).with_for_update()
        )
        
        return result.scalar_one_or_none()
    
    async def get_by_id(self, token_id: uuid.UUID) -> RefreshToken | None:
        
        return await self._session.get(RefreshToken, token_id)
    
    def revoke(self, token: RefreshToken, reason: str) -> None:
        if token.revoke_at is None:
            token.revoked_at = datetime.now(UTC)
            token.revocation_reason = reason
        
    async def revoke_family(self, family_id: uuid.UUID, reason: str) -> None:
        await self._session.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == family_id,
                   RefreshToken.revoked_at.is_(None),
            )
            .values(
                revoked_at=datetime.now(UTC),
                revocation_reason=reason,
            )
        )
    
    def set_replaced_by(self, token: RefreshToken, replacement_id: uuid.UUID) -> None:
        token.replaced_by = replacement_id 
        
        
        
           
        