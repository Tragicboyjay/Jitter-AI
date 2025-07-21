import json
import os
from memory.sqlite_actions import add_message, get_num_messages_by_id
from parsers.create_prompt import create_system_prompt
from parsers.parse_being_json import load_being_json
from core.providers.open_router import open_router_provider
from core.providers.google import google_gemini_provider
from tools.handle_tool_call import is_tool_call, parse_tool_call, run_tool, run_tools_batch
from utils.enums import AI_Providers, Numbers, Role
from utils.dates import now

MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", 5))

def call_model(model_provider, system_prompt, message, rag_context, previous_messages):
    """
    Calls the specified AI model provider.
    """
    if model_provider == AI_Providers.OPENROUTER.value:
        return open_router_provider(system_prompt, message, rag_context, previous_messages)
    elif model_provider == AI_Providers.GOOGLE.value:
        return google_gemini_provider(system_prompt, message, previous_messages)
    else:
        raise ValueError(f"Unsupported model provider specified: {model_provider}")

def get_ai_response(being, rag_context, message):
    """
    Manages the conversation turn, supporting both single and parallel tool calls.
    """
    context_id = being["contextId"]
    
    if not message:
        raise ValueError("Message cannot be empty")
    
    try:
        model_provider = being["modelProvider"]
        if not model_provider:
            raise ValueError("Model provider not specified in being.json")

        # Get previous messages from database for context
        previous_messages = get_num_messages_by_id(context_id, Numbers.MAX_MESSAGES.value)

        # Track messages for this conversation turn as list of tuples
        conversation_messages = [
            (msg, role, created_at) for *_, msg, role, created_at in previous_messages
        ] if previous_messages else []

        # Add current user message to database and to conversation
        now_str = now()
        add_message(context_id, message, Role.USER.value)
        conversation_messages.append((message, Role.USER.value, now_str))

        # --- Main loop for handling tool calls ---
        current_message = message
        ai_response = None
        last_tool_call = None
        repeat_tool_count = 0
        original_user_message = message
        
        # Initialize a list to store tool results for this turn
        tool_results_history = []

        for iteration in range(MAX_ITERATIONS):
            system_prompt = create_system_prompt(rag_context, being)
            ai_response = call_model(model_provider, system_prompt, current_message, rag_context, conversation_messages)

            if not ai_response:
                raise ValueError("Received empty response from AI provider")

            now_str = now()
            # Log the raw assistant message (including tool calls) for full context
            add_message(context_id, ai_response, Role.ASSISTANT.value)
            conversation_messages.append((ai_response, Role.ASSISTANT.value, now_str))

            # Check for tool calls - this now returns a list or False
            tool_calls = is_tool_call(ai_response)

            if tool_calls:
                # Handle multiple tool calls (parallel execution)
                if len(tool_calls) > 1:
                    print(f"[INFO] Processing {len(tool_calls)} tool calls in parallel")
                    
                    # Execute all tools in batch
                    batch_results = run_tools_batch(tool_calls)
                    
                    # Log all results
                    for i, (tool_name, params) in enumerate(tool_calls):
                        result_str = json.dumps(batch_results[i], indent=2) if isinstance(batch_results[i], (dict, list)) else str(batch_results[i])
                        now_str = now()
                        add_message(context_id, result_str, Role.TOOL.value)
                        conversation_messages.append((result_str, Role.TOOL.value, now_str))
                        tool_results_history.append(result_str)
                    
                    # Create synthesis prompt
                    all_tool_results = "\n".join(f"- {res}" for res in tool_results_history)
                    current_message = (
                        f"You completed the user's request: '{original_user_message}'.\n"
                        f"Here are the results from all your tool calls:\n{all_tool_results}\n"
                        "Please synthesize these results into a final, comprehensive answer for the user."
                    )
                    continue
                
                # Handle single tool call (backward compatibility)
                else:
                    tool_name, params = tool_calls[0]
                    tool_call_signature = (tool_name, str(params))
                    
                    if tool_call_signature == last_tool_call:
                        repeat_tool_count += 1
                    else:
                        repeat_tool_count = 1
                    last_tool_call = tool_call_signature
                    
                    if repeat_tool_count > 2:
                        current_message = "The requested tool has already been executed multiple times. Please clarify your next instruction."
                        break
                    
                    tool_result_raw = run_tool(tool_name, params)
                    
                    if isinstance(tool_result_raw, (dict, list)):
                        tool_result_str = json.dumps(tool_result_raw, indent=2)
                    else:
                        tool_result_str = str(tool_result_raw)

                    # Add the tool result to the database and our history list
                    now_str = now()
                    add_message(context_id, tool_result_str, Role.TOOL.value)
                    conversation_messages.append((tool_result_str, Role.TOOL.value, now_str))
                    tool_results_history.append(tool_result_str)

                    # Reconstruct the prompt with the FULL history of tool results
                    all_tool_results = "\n".join(f"- {res}" for res in tool_results_history)
                    current_message = (
                        f"You are fulfilling a user's request. The original request was: '{original_user_message}'.\n"
                        f"You have already executed one or more tools. Here are the results so far:\n{all_tool_results}\n"
                        "Based on these results, please either call the next necessary tool or provide the final answer to the user."
                    )
                    continue
            else:
                # This is a final text response, so exit the loop
                break

        return ai_response

    except Exception as e:
        print(f"AI Error: {str(e)}")
        raise