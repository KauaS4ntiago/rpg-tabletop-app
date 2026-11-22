
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer

from app.core.config import get_settings
from app.core.database import get_session
from app.main import app


POSTGRES_IMAGE = "postgres:17"  # Keep in sync with docker-compose.yml
TEST_SECRET_KEY = "test-secret-key-with-at-least-32-characters"
BACKEND_DIR = Path(__file__).resolve().parents[1]


# ============================================================
# Infrastructure
# ============================================================

@pytest.fixture(scope="session")
def postgres_container():

    with PostgresContainer(
        POSTGRES_IMAGE,
        username="test",
        password="test",
        dbname="rpg_test",
    ) as postgres:
        yield postgres


# ============================================================
# Test environment
# ============================================================

@pytest.fixture(scope="session")
def test_environment(postgres_container):

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setenv("POSTGRES_USER", postgres_container.username)
        monkeypatch.setenv("POSTGRES_PASSWORD", postgres_container.password)
        monkeypatch.setenv("POSTGRES_DB", postgres_container.dbname)
        monkeypatch.setenv("POSTGRES_HOST", postgres_container.get_container_host_ip())
        monkeypatch.setenv(
            "POSTGRES_PORT", str(postgres_container.get_exposed_port(5432))
        )
        monkeypatch.setenv("SECRET_KEY", TEST_SECRET_KEY)

        get_settings.cache_clear()

        yield

    # Clears the cache again after restoring the original environment.
    get_settings.cache_clear()


# ============================================================
# Database setup
# ============================================================

@pytest.fixture(scope="session")
def setup_database(test_environment):

    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "migrations"))

    command.upgrade(config, "head")


@pytest_asyncio.fixture
async def test_engine(setup_database) -> AsyncIterator[AsyncEngine]:

    engine = create_async_engine(
        get_settings().database_url,
        pool_pre_ping=True,
    )

    try:
        yield engine
    finally:
        await engine.dispose()


# ============================================================
# Database session
# ============================================================

@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncIterator[AsyncSession]:

    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        session_factory = async_sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        try:
            async with session_factory() as session:
                yield session
        finally:
            if transaction.is_active:
                await transaction.rollback()


# ============================================================
# HTTP client
# ============================================================

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as http_client:
            yield http_client
    finally:
        app.dependency_overrides.pop(get_session, None)
