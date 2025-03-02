from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    AsyncEngine, async_sessionmaker, AsyncSession)
from config import settings



# Create an asynchronous engine for the database connection
engine: AsyncEngine = create_async_engine(
    url=settings.db.database_url,
    echo=False,
    echo_pool=False,
    pool_size=5,
    max_overflow=5,
    pool_timeout=30,  # Connection timeout
    pool_recycle=30,  # Connection lifetime (30 seconds)
)


# Create a session factory for generating asynchronous sessions
session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    autoflush=False,
    class_=AsyncSession,
    autocommit=False,
    expire_on_commit=False
)

async def session_getter() -> AsyncGenerator[AsyncSession, None]:
    """
        Asynchronous generator function that provides
        a session from the session factory.
    """
    async with session_factory() as session:
        try:
            yield session
        finally:
            print("SESSION CLOSED IN session_getter!", flush=True)
            await session.close()


SessionDep = Annotated[AsyncSession, Depends(session_getter)]