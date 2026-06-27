from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker, 
    AsyncSession
)

from ..config import DB_URL

engine = create_async_engine(
    DB_URL, 
    echo=False,
)
session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def session_getter():
    async with session_factory() as session:
        yield session


async def get_session():
    async with session_factory() as session:
        return session
