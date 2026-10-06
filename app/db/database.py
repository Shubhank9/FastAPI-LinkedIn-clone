from sqlalchemy import create_engine, text 
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20
    )                       

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal() 
    try:
        yield db
    finally:
        db.close()

def test_db_connection():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))