from app.main import app
from app.models.models import Base
from app.core.dependencies import get_database
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient, ASGITransport
import pytest
from asgi_lifespan import LifespanManager


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="function")
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=StaticPool, connect_args={"check_same_thread": False})
    
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    async with session_factory() as session:
        yield session
    
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def client(db_session):
    async def override_get_database():
        yield db_session
    
    app.dependency_overrides[get_database] = override_get_database
    
    async with LifespanManager(app=app) as manager:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
            yield async_client
    
    app.dependency_overrides.clear()