from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cohere
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import google.generativeai as genai
import re
import json
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db
from model import Review



COHERE_API_KEY = ("udgKNNW1JxHxZYSQ7Xtc2xEFRGqNYcKXpGIjwfga")

if not COHERE_API_KEY:
    raise ValueError("Cohere API Key not found. Set COHERE_API_KEY in .env file.")

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

app = FastAPI()


class ReviewRequest(BaseModel):
    review: str

genai.configure(api_key="AIzaSyCPmJIxkxEYVfwMGCKjiS8CBuQ0hsf1riY")

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

        # Extract and clean response text
        response_text = response.text.strip()
        
        # Split the response into sentiment and surety
        sentiment, surety = response_text.split("|")
        sentiment = sentiment.strip()
        surety = float(surety.strip())
        
        # Save to database
        db_review = Review(
            review=request.review,
            sentiment=sentiment,
            sentiment_score=surety  # Convert percentage to decimal
        )
        db.add(db_review)
        db.commit()
        
        # Define emoji mapping
        emoji_map = {
            "Positive": "😊",
            "Negative": "😔",
            "Neutral": "😐"
        }
        
        # Get the appropriate emoji
        emoji = emoji_map.get(sentiment, "❓")
        
        result = {
            "sentiment": f"This seems like a {sentiment} review {emoji}",
            "surety": f"{surety}% {sentiment} {emoji}"
        }
        return JSONResponse(content=result)

    except Exception as e:
        db.rollback()  # Rollback on error
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