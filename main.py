# main.py
import argparse
import os
import asyncio
from contextlib import asynccontextmanager

from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.agent import get_ai_response
from parsers.parse_being_json import load_being_json
from tasks.live import agent_live
from tasks.twitter import tweet_generator
from utils.print_details import print_being_details
from rag.rag_system import ingest_data, search_rag
from memory.sqlite_setup import setup_database

load_dotenv()

# --- CLI Argument Parsing (must be before app creation) ---
parser = argparse.ArgumentParser(description="Run the FastAPI application with optional being name.")
parser.add_argument(
    "--being",
    type=str,
    default=None, # Default to None, so load_being_json can handle it
    help="Optional name of the being to load (e.g., 'my_custom_being' for 'my_custom_being.json')."
)
parser.add_argument(
    "--host",
    type=str,
    default=os.getenv("HOST", "0.0.0.0"),
    help="Host address for the server."
)
parser.add_argument(
    "--port",
    type=int,
    default=int(os.getenv("PORT", 8000)),
    help="Port for the server."
)
parser.add_argument(
    "--reload", # Use --reload to enable, default is False
    action="store_true",
    dest="reload",
    help="Enable auto-reloading of the server."
)

# Parse known args so uvicorn doesn't get confused
args, _ = parser.parse_known_args()
_being_name_from_cli = args.being
HOST = args.host
PORT = args.port

GENERATE_TWEET = os.getenv("GENERATE_TWEET", "true").lower() == "true"
TWEET_INTERVAL = int(os.getenv("TWEET_INTERVAL", 2))

AGENT_ALIVE = os.getenv("AGENT_ALIVE", "false").lower() == "true"

# --- Application State and Lifespan Management ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages application startup and shutdown events.
    """
    # -- Startup --
    print("INFO:     Starting up application...")

    # Ensure DB tables exist before any RAG/model logic
    setup_database()

    # Load resources once
    being_data = load_being_json(being_name=_being_name_from_cli)
    print_being_details(being_data)

    # Ingest RAG data (process new/changed files and update index/db)
    ingest_data()

    # Store being in the app state for access elsewhere
    app.state.being = being_data
    
    # Create and start background tasks
    tasks = []
    
    if GENERATE_TWEET:
        print(f"INFO:     Starting tweet generator. Interval: {TWEET_INTERVAL} minute(s).")
        tasks.append(asyncio.create_task(tweet_generator(app)))

    if AGENT_ALIVE:
        tasks.append(asyncio.create_task(agent_live(app)))

    yield

    # -- Shutdown --
    print("INFO:     Shutting down application...")
    for task in tasks:
        task.cancel()
    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except asyncio.CancelledError:
        print("INFO:     All background tasks cancelled successfully.")

# Create the FastAPI app with the lifespan manager
server_app = FastAPI(lifespan=lifespan)

# --- Dependency Injection ---

def get_being():
    """Dependency to get the 'being' object from app state."""
    return server_app.state.being



# --- API Endpoints ---

class Message(BaseModel):
    content: str

server_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, change to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@server_app.get("/being")
async def get_being_details(being: dict = Depends(get_being)):
    """Returns being details using dependency injection."""
    return being


@server_app.post("/message")
async def get_message_response(
    message: Message,
    being: dict = Depends(get_being)
):
    """Gets an AI response using dependency injection for resources."""
    if not message.content:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        rag_context = search_rag(message.content, top_k=3)
        response = get_ai_response(being, rag_context, message.content)
        if not response:
            raise ValueError("AI response was empty")
        return {"response": response}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# --- Main entry point ---
if __name__ == "__main__":
    uvicorn.run(
        "main:server_app", 
        host=args.host, # Use parsed host
        port=args.port, # Use parsed port
        reload=args.reload # Use parsed reload
    )