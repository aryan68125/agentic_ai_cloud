from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.configs.config import ProjectConfigurations

"""
This file will serve as a single source of database access through out the entire project
"""

DATABASE_URL = ProjectConfigurations.DB_CONNECTION_STRING.value

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# This will get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
