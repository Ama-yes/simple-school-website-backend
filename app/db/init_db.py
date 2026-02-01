from app.db.database import engine
from app.models.models import Base
import asyncio


async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)



if __name__ == "__main__":
    print("Initializing database...")
    asyncio.run(create_tables())
    print("Database initiated successfully!")