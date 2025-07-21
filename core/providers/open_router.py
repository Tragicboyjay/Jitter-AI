import os
import requests
import json

from utils.enums import Role

def open_router_provider(system_prompt, message, rag, previous_messages=[]):
    model = os.getenv("OPENROUTER_MODEL_ID", "moonshotai/kimi-k2:free")
    api_key = os.getenv("OPENROUTER_API_KEY")

    messages = [{"role": Role.SYSTEM.value, "content": system_prompt}]

    # Add previous messages to the array
    for msg, role, created_at in reversed(previous_messages):
        messages.append({"role": role, "content": msg})

    # Add the current user message
    messages.append({"role": Role.USER.value, "content": message})

    if not api_key:
        raise ValueError("API key for OpenRouter is not set in environment variables")
    if not message:
        raise ValueError("Message cannot be empty")
    if not model:
        raise ValueError("Model ID is not specified in environment variables or defaults")
    
    try:
        payload = {
            "model": model,
            "messages": messages,
        }
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            data=json.dumps(payload)
        )

        try:
            response.raise_for_status()  # Raise an exception for HTTP errors
        except requests.exceptions.HTTPError as e:
            raise ValueError(f"Failed to get response from OpenRouter: {str(e)}")

        response_data = response.json()

        if "error" in response_data:
            raise ValueError(f"API Error: {response_data['error']}")

        content = response_data.get("choices", [{}])[0].get("message", {}).get("content")
        if not content:
            raise ValueError(f"Invalid API Response: {response_data}")

        return content

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {str(e)}")
        raise ValueError(f"Failed to get response from OpenRouter: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {response.text}")
        raise ValueError("Invalid response from OpenRouter")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage
    api_key = os.getenv("OPENROUTER_API_KEY")
    test_response = open_router_provider("hello", "moonshotai/kimi-k2:free", api_key, "You are a helpful assistant.")
    print(test_response)  # Should print the response from the model