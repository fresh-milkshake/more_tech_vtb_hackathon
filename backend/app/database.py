from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import redis
from app.config import settings

def create_database_engine():
    """
    Create SQLAlchemy database engine based on database type.
    
    Returns:
        Engine: Configured SQLAlchemy engine for SQLite or PostgreSQL
    """
    if settings.DATABASE_URL.startswith("sqlite"):
        return create_engine(
            settings.DATABASE_URL,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG
        )
    else:
        return create_engine(
            settings.safe_database_url,
            echo=settings.DEBUG,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=300
        )

engine = create_database_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_redis_client():
    """
    Create Redis client connection.
    
    Returns:
        Redis: Configured Redis client with response decoding
    """
    return redis.from_url(settings.REDIS_URL, decode_responses=True)

redis_client = create_redis_client()


def get_db() -> Session:
    """
    FastAPI dependency to get database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Note:
        Session is automatically closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_redis():
    """
    FastAPI dependency to get Redis client.
    
    Returns:
        Redis: Redis client instance for caching and session management
    """
    return redis_client