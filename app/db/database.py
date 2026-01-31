from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from sqlalchemy.orm.decl_api import DeclarativeMeta
DATABASE_URL = settings.database_url


engine = create_async_engine(url=DATABASE_URL, echo=False)

localSession = async_sessionmaker(bind=engine, class_=AsyncSession, autoflush=False, autocommit=False, expire_on_commit=False)

Base: DeclarativeMeta = declarative_base()