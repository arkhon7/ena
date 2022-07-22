from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


import ena.config

# imported to every other file
AsyncEngine = create_async_engine(ena.config.DB_STRING, echo=True, poolclass=pool.NullPool)
SyncEngine = create_engine(ena.config.SYNC_DB_STRING, echo=True)
Base = declarative_base()
Session = sessionmaker(AsyncEngine, class_=AsyncSession)


