import asyncio
import random

from fastapi import FastAPI

from core.agent import get_ai_response
from memory.sqlite_actions import get_num_messages_by_id
from rag.rag_system import search_rag

FEELINGS = [
    "energetic",
    "sleepy",
    "curious",
    "creative",
    "focused",
    "happy",
    "thoughtful.",
    "playful",
    "alert.",
    "inspired",
    "upset",
    "silly.",
    "overwhelmed",
    "calm and collected.",
    "excited",
    "grumpy",
    "horny",
    "sad",
]

async def agent_live(app: FastAPI):
    """
    A robust background task to keep the agent alive and communicate its mood.
    """
    while True:
        try:
            await asyncio.sleep(60)

            being = app.state.being

            last_messages = get_num_messages_by_id(being["contextId"], 5)

            prompt = (
                f"Last 5 messages:\n"
                f"{last_messages}\n\n"
                f"How do you feel right now? Base it on what was said and when.\n"
                f"Don't reply to the messages—just share your mood.\n"
                f"Keep it short unless you're really emotional, or just feel like expressing why you are feeling the way you do.\n"
                f"If you feel like it, act on your emotions—use tools, make choices, do something if you'd like.\n"
                f"Example feelings:\n{FEELINGS}\n"
            )

            # rag_context = search_rag(prompt, top_k=3)
            response = get_ai_response(being, "", prompt)
    
            if not response:
                raise ValueError("AI response was empty")
            
            print(f"\n{response}\n")  
        except Exception as e:
            print(f"ERROR:    An error occurred in agent_live: {e}")
            await asyncio.sleep(5)  # Wait before retrying in case of an error