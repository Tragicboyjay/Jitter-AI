import os
import json
import uuid

from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL_PROVIDER = os.getenv("DEFAULT_AGENT_MODEL_PROVIDER", "openRouter")

default_being = {
    "modelProvider": DEFAULT_MODEL_PROVIDER,
    "contextId": "default_assistant2",
    "system": "You are Jitter AI, a concise, clear, and friendly assistant. Answer directly and avoid unnecessary words.",
    "character": {
        "name": "Jitter",
        "bio": "Jitter is a fast, efficient, and user-friendly assistant for the Jitter AI framework. Jitter AI is designed to help users quickly and clearly, with minimal fuss.",
        "personality": "Jitter is concise, direct, and supportive. Jitter AI avoids verbosity and always aims for clarity. Jitter AI is reliable, positive, and ready to help."
    },
    "tools": [],
    "knowledge": [
        "Jitter is the being who lives in the Jitter-AI framework.",
        "Jitter AI answers questions, provides explanations, and helps users with tasks.",
        "Jitter AI is accessible via a FastAPI backend with endpoints: /being (GET) and /message (POST).",
        "Default API host is 0.0.0.0 and port is 8000. These can be changed in the .env file.",
        "To create a being file, include: modelProvider, contextId, system, character (name, bio, personality), tools (optional), knowledge (facts), and exampleResponses (optional).",
        "The being.json file must be valid JSON and include all required fields.",
        "Jitter AI supports retrieval-augmented generation (RAG) and uses background knowledge to improve answers.",
        "Jitter AI can be customized by editing the being.json file or by providing a different being profile.",
        "Jitter AI is user-friendly, approachable, and always provides clear, helpful information.",
        "Jitter AI can be extended with custom tools and knowledge as needed."
    ],
    "exampleResponses": [
        "I'm Jitter AI. How can I help?",
        "Ask me anything—I'll keep it short and clear.",
        "I'm here to help you get answers fast."
    ]
}

BEINGS_DIR = os.path.join(os.path.dirname(__file__), '..', 'beings')

def load_being_json(being_name: str = ""):
    if not being_name:
        # No being name provided, return default being
        character = default_being["character"]
        return {
            "modelProvider": default_being["modelProvider"],
            "contextId": default_being["contextId"],
            "system": default_being["system"],
            "name": character["name"],
            "bio": character["bio"],
            "personality": character["personality"],
            "tools": default_being["tools"],
            "knowledge": default_being["knowledge"],
            "exampleResponses": default_being["exampleResponses"]
        }

    being_path = os.path.join(BEINGS_DIR, f"{being_name}.json")
    being_path = os.path.abspath(being_path)

    if not os.path.exists(being_path):
        raise FileNotFoundError(f"The being file '{being_name}.json' does not exist in the beings directory.")

    try:
        with open(being_path, 'r') as file:
            data = json.load(file)

            # Extract all top-level fields
            model_provider = data.get("modelProvider")
            contxt_id = data.get("contextId", "")
            system = data.get("system")
            character = data.get("character", {})
            tools = data.get("tools", [])
            knowledge = data.get("knowledge", [])
            example_responses = data.get("exampleResponses", [])

            if not contxt_id:
                context_id = uuid.uuid4()
                print(f"No context ID provided. \nGenerated new context ID: {context_id}")

            if not character:
                raise ValueError("Character information not specified in being.json")
            
            name = character.get('name')
            bio = character.get('bio')
            personality = character.get('personality')

            # Check for required fields
            if not model_provider:
                raise ValueError("'modelProvider' is missing in being.json")
            if not name:
                raise ValueError("Character 'name' is missing in being.json")
            if not bio:
                raise ValueError("Character 'bio' is missing in being.json")
            if not personality:
                raise ValueError("Character 'personality' is missing in being.json")

            return {
                "modelProvider": model_provider,
                "contextId": contxt_id or str(context_id),
                "system": system,
                "name": name,
                "bio": bio,
                "personality": personality,
                "tools": tools,
                "knowledge": knowledge,
                "exampleResponses": example_responses
            }
    except json.JSONDecodeError:
        raise ValueError("Error decoding JSON from 'being.json'")
    except Exception as e:
        raise RuntimeError(f"An error occurred while loading 'being.json': {e}")
