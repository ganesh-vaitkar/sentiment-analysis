from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import cohere
import os
import google.generativeai as genai
from dotenv import load_dotenv
from database import get_db
from model import Review
from fastapi.middleware.cors import CORSMiddleware  # Add this import

# API Configuration
# COHERE_API_KEY = "udgKNNW1JxHxZYSQ7Xtc2xEFRGqNYcKXpGIjwfga"
GEMINI_API_KEY = "AIzaSyCPmJIxkxEYVfwMGCKjiS8CBuQ0hsf1riY"

# Validation
# if not COHERE_API_KEY:
#     raise ValueError("Cohere API Key not found. Set COHERE_API_KEY in .env file.")

# Initialize clients
# co = cohere.Client(COHERE_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI()


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class ReviewRequest(BaseModel):
    review: str

# Emoji mapping
EMOJI_MAP = {
    "Positive": "😊",
    "Negative": "😔",
    "Neutral": "😐"
}

@app.post("/analyze")
def analyze_sentiment(request: ReviewRequest, db: Session = Depends(get_db)):
    prompt = f"""
    Analyze the sentiment of the following movie review and provide both sentiment and surety:
    
    Review:  "{request.review}"

    Respond with exactly this format: "[Sentiment]|[X]" where:
    - Sentiment is either "Positive", "Negative", or "Neutral"
    - X is a surety percentage between 0 and 100
    
    For example: "Positive|85" or "Negative|70"
    Base the percentage on how confident you are about the sentiment classification.
    """

    try:
        client = genai.GenerativeModel("gemini-2.0-flash")
        response = client.generate_content(prompt)

        response_text = response.text.strip()
        sentiment, surety = response_text.split("|")
        sentiment = sentiment.strip()
        surety = float(surety.strip())
        
        # Save to database
        db_review = Review(
            review=request.review,
            sentiment=sentiment,
            sentiment_score=surety
        )
        db.add(db_review)
        db.commit()
        
        emoji = EMOJI_MAP.get(sentiment, "❓")
        
        result = {
            "sentiment": f"This seems like a {sentiment} review {emoji}",
            "surety": f"{surety}% {sentiment} {emoji}"
        }
        return JSONResponse(content=result)

    except Exception as e:
        db.rollback()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/list_view")
def list_reviews(db: Session = Depends(get_db)):
    try:
        reviews = db.query(Review).all()
        if not reviews:
            return JSONResponse(content={"message": "No reviews found"}, status_code=404)
        
        return [
            {
                "id": review.id,
                "review": review.review,
                "sentiment": review.sentiment,
                "sentiment_score": review.sentiment_score,
                "created_at": review.created_at
            }
            for review in reviews
        ]
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
