import re
import ast
import sys
import os

# Import get_tool_function to retrieve the actual callable tool function
from tools.tool_registry import get_tool_function

# Regex to match FUNCTION: <tool_name> PARAMS: { ... }
TOOL_CALL_REGEX = r"FUNCTION:\s*(\w+)\s*PARAMS:\s*(\{.*?\})"

def is_tool_call(message: str):
    """
    Returns a list of tool calls if the message contains valid tool calls, else False.
    This supports both single and multiple tool calls in one message.
    
    Returns:
    - List of tuples [(tool_name, params), ...] if tool calls found
    - False if no tool calls found
    """
    matches = re.findall(TOOL_CALL_REGEX, message, re.DOTALL)
    if not matches:
        return False
    
    tool_calls = []
    for tool_name, params_str in matches:
        try:
            # Safely evaluate the params dict string
            params = ast.literal_eval(params_str)
            # Ensure params is actually a dictionary
            if not isinstance(params, dict):
                print(f"[WARNING] Parsed parameters for '{tool_name}' are not a dictionary: {params}")
                continue
            tool_calls.append((tool_name, params))
        except Exception as e:
            print(f"[ERROR] Failed to parse tool call parameters for '{tool_name}': {e}")
            continue
    
    return tool_calls if tool_calls else False

def parse_tool_call(message: str):
    """
    LEGACY FUNCTION: Maintains backward compatibility.
    Returns the FIRST tool call found in the message.
    Returns (tool_name, params_dict) or (None, None) if not found.
    
    This function is kept for backward compatibility with existing code.
    For new implementations, use is_tool_call() directly.
    """
    tool_calls = is_tool_call(message)
    if tool_calls:
        return tool_calls[0]  # Return first tool call
    return None, None

def run_tool(tool_name: str, params: dict):
    """
    Executes the tool if registered. Returns the result or error message.
    """
    # Use get_tool_function from tool_registry to get the actual callable function
    tool_function = get_tool_function(tool_name)
    
    if tool_function is None:
        return f"Tool '{tool_name}' not found in registry or is not a callable function."
    
    try:
        # Call the actual Python function with unpacked parameters
        result = tool_function(**params)
        print(f"[TOOL EXECUTION] Successfully ran '{tool_name}' with params {params}. Result: {result}")
        return result
    except TypeError as e:
        # This usually means missing parameters or incorrect parameter types for the tool function
        print(f"[ERROR] Error executing tool '{tool_name}': Invalid parameters or missing required arguments. Details: {e}")
        return f"Error executing tool '{tool_name}': Invalid parameters or missing required arguments. Ensure all required parameters are provided and are of the correct type. Details: {e}"
    except Exception as e:
        # Catch any other unexpected errors during tool execution
        print(f"[ERROR] An unexpected error occurred while running tool '{tool_name}': {e}")
        return f"An unexpected error occurred while running tool '{tool_name}': {e}"

def run_tools_batch(tool_calls):
    """
    NEW FUNCTION: Executes multiple tools in parallel (conceptually).
    
    Args:
        tool_calls: List of tuples [(tool_name, params), ...]
    
    Returns:
        List of results corresponding to each tool call
    """
    results = []
    for tool_name, params in tool_calls:
        result = run_tool(tool_name, params)
        results.append(result)
    return results