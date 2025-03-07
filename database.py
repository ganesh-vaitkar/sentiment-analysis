from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
import os

# Use environment variables for sensitive data
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    "mysql+pymysql://root:MahitNahi%4012@localhost:3306/sentiment_db"
)

# Create an engine with error handling
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
except SQLAlchemyError as e:
    print(f"Error connecting to database: {e}")
    raise

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session with error handling
def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        print(f"Database error: {e}")
        raise
    finally:
        db.close()