"""Database connection and session management."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from core_infinity_stones_sso.config import Settings
from core_infinity_stones_sso.models import Base


def get_engine(database_url: str):
    """Create a SQLAlchemy engine."""
    # Use StaticPool for SQLite (useful for testing), otherwise use default pool
    if database_url.startswith("sqlite"):
        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(database_url, pool_pre_ping=True)


class Database:
    """Database connection manager."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.engine = get_engine(settings.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """Get a database session."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


def get_db(settings: Settings) -> Generator[Session, None, None]:
    """Dependency for FastAPI to get database session."""
    database = Database(settings)
    yield from database.get_session()
