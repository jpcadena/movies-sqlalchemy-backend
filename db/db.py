"""
Database module
"""
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

SQLITE_FILE_NAME: str = 'movie.db'
DATABASE_URL: str = f'sqlite+aiosqlite:///./{SQLITE_FILE_NAME}'
connect_args = {"check_same_thread": False}
engine = create_async_engine(
    DATABASE_URL, future=True, echo=True, connect_args=connect_args)


async def create_db_and_tables() -> None:
    """
    Create database and tables without duplicating them.
    :return: None
    :rtype: NoneType
    """
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    await engine.dispose()


async def get_session() -> AsyncSession:
    """
    Get connection session to the database
    :return session: Async session for database connection
    :rtype session: AsyncSession
    """
    async with AsyncSession(engine) as session:
        yield session
