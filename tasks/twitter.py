import asyncio
from fastapi import FastAPI

from core.agent import get_ai_response
from rag.rag_system import search_rag


async def tweet_generator(app: FastAPI):
    """
    A robust background task to generate tweets.
    """
    while True:
        try:
            print("INFO:     Generating a new tweet...")
            # Access resources from the app state

            being = app.state.being
            # Use a consistent prompt
            prompt = "tweet something in the style of your personality, do not repeat recent tweets"
            rag_context = search_rag(prompt, top_k=3)
            response = get_ai_response(being, rag_context, prompt)

            print(f"Generated Tweet: {response}")

        except Exception as e:
            # Add error handling to prevent the task from crashing
            print(f"ERROR:    An error occurred in tweet_generator: {e}")
        
        # Use the interval from settings
        await asyncio.sleep(2 * 60)