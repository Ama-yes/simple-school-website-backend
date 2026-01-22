from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from app.core.config import settings
from sqlalchemy.orm.decl_api import DeclarativeMeta
DATABASE_URL = settings.database_url


engine = create_engine(url=DATABASE_URL, )

localSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base: DeclarativeMeta = declarative_base()