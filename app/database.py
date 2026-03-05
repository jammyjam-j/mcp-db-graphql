import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL

Base = declarative_base()

engine_kwargs = {
    "pool_pre_ping": True,
    "echo": os.getenv("SQLALCHEMY_ECHO", "false").lower() == "true",
}

try:
    engine = create_engine(DATABASE_URL, **engine_kwargs)
except Exception as exc:
    raise RuntimeError(f"Failed to create database engine: {exc}") from exc

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_session() -> Base:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as err:
        session.rollback()
        raise RuntimeError(f"Database operation failed: {err}") from err
    finally:
        session.close()

def init_db():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        raise RuntimeError(f"Failed to initialize database schema: {exc}") from exc

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if engine.dialect.name == "sqlite":
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()