import os
from pathlib import Path

import pytest
import pytest_asyncio

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer

from app.core.config import get_settings


# --------------------------------------------------
# Temporary PostgreSQL 
# --------------------------------------------------

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer(
        "postgres:16-alpine",
        username="test",
        password="test",
        dbname="rpg_test",
    ) as postgres:
        yield postgres


# --------------------------------------------------
# est environment settings
# --------------------------------------------------

@pytest.fixture(scope="session")
def test_settings(postgres_container):
    env_vars = {
        "POSTGRES_USER": postgres_container.username,
        "POSTGRES_PASSWORD": postgres_container.password,
        "POSTGRES_DB": postgres_container.dbname,
        "POSTGRES_HOST": postgres_container.get_container_host_ip(),
        "POSTGRES_PORT": str(postgres_container.get_exposed_port(5432)),
        "SECRET_KEY": "test-secret-key-with-at-least-32-characters",
    }

    original_env = {
        key: os.environ.get(key)
        for key in env_vars
    }

    os.environ.update(env_vars)
    get_settings.cache_clear()

    try:
        yield
    finally:
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

        get_settings.cache_clear()


# --------------------------------------------------
# Migrations
# --------------------------------------------------

@pytest.fixture(scope="session")
def setup_database(test_settings):
    project_root = Path(__file__).resolve().parents[2]

    alembic_config = Config(str(project_root / "alembic.ini"))

    command.upgrade(alembic_config, "head")


# --------------------------------------------------
# Test engine
# --------------------------------------------------

@pytest_asyncio.fixture
async def test_engine(setup_database):
    engine = create_async_engine(
        get_settings().database_url,
        pool_pre_ping=True,
    )

    try:
        yield engine
    finally:
        await engine.dispose()


# --------------------------------------------------
# Test section
# --------------------------------------------------

@pytest_asyncio.fixture
async def db_session(test_engine):
    async with test_engine.connect() as connection:
        transaction = await connection.begin()

        session_factory = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        try:
            async with session_factory() as session:
                yield session
        finally:
            if transaction.is_active:
                await transaction.rollback()