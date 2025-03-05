from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cohere
import os
from dotenv import load_dotenv
import os
from dotenv import load_dotenv


COHERE_API_KEY = ("udgKNNW1JxHxZYSQ7Xtc2xEFRGqNYcKXpGIjwfga")

if not COHERE_API_KEY:
    raise ValueError("Cohere API Key not found. Set COHERE_API_KEY in .env file.")

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

app = FastAPI()

class ReviewRequest(BaseModel):
    review: str

@app.post("/analyze")
def analyze_sentiment(request: ReviewRequest):
    try:
        response = co.classify(
            model='large',
            inputs=[request.review],
            examples=[
    {"text": "I absolutely loved this movie, it was fantastic!", "label": "Positive"},
    {"text": "The plot was dull and boring, I didn't enjoy it at all.", "label": "Negative"},
    {"text": "The movie was okay, but nothing special.", "label": "Neutral"},
    {"text": "Great acting and direction, but the pacing was off.", "label": "Positive"},
    {"text": "I hated the ending, it ruined the whole experience.", "label": "Negative"},
    {"text": "It was just average, nothing memorable.", "label": "Neutral"}
]

        )
        sentiment = response.classifications[0].prediction
        return {"review": request.review, "sentiment": sentiment}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"message": "Sentiment Analysis API is running!"}
