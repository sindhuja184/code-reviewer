from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from config import Config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

#Create async engine
async_engine = create_async_engine(
    Config.DATABASE_URL,
    echo = True,
    future= True
)

#Initialise DB
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    Session = sessionmaker(
        bind= async_engine,
        class_ = AsyncSession,
        expire_on_commit = False
    )
    async with Session() as session:
        yield session