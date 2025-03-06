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
def analyze_sentiment(request: ReviewRequest):
   
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
        
        # Create JSON response with both parameters
        # Define emoji mapping
        emoji_map = {
            "Positive": "😊",
            "Negative": "😔",
            "Neutral": "😐"
        }
        
        # Get the appropriate emoji
        emoji = emoji_map.get(sentiment.strip(), "❓")
        
        result = {
            "sentiment": f"This seems like a {sentiment.strip()} review {emoji}",
            "surety": f"{surety.strip()}% {sentiment.strip()} {emoji}"
        }
        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/")
def home():
    return {"message": "Sentiment Analysis API is running!"}
