from datetime import datetime
from database import Base, engine
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship








class Review(Base):
    __tablename__ = "tbl_review"

    id = Column(Integer, primary_key=True, index=True)
    review = Column(String(1500), nullable=False)
    sentiment = Column(String(10), nullable=False)
    sentiment_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
Base.metadata.create_all(bind=engine)