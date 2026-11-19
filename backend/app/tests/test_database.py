from sqlalchemy import text

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect


@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession):
    result = await db_session.execute(text("SELECT 1"))

    assert result.scalar_one() == 1
    
@pytest.mark.asyncio
async def test_database_tables(db_session: AsyncSession):
    connection = await db_session.connection()

    tables = await connection.run_sync(
        lambda sync_connection: inspect(sync_connection).get_table_names()
    )

    assert "users" in tables