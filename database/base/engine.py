from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from data.config import configuration as cfg

DATABASE_URL = cfg.ASYNC_DATABASE_URL


async_engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = async_sessionmaker(async_engine)
