from parsers.parse_being_json import load_being_json

import sys

import os

from tools.built_in_tools import get_built_in_tools

from tools.tool_registry import TOOL_REGISTRY



built_in_tools_list = get_built_in_tools()



# being = load_being_json()



def create_system_prompt(rag, being):

    system = being["system"]

    name = being['name']

    bio = being['bio']

    personality = being['personality']

    example_responses = being["exampleResponses"]

    tools = being["tools"]



    all_tools = built_in_tools_list + tools



    # Format RAG facts as background knowledge

    rag_facts = ""

    if rag:

        rag_lines = [line.strip() for line in rag.split('\n') if line.strip()]

        if rag_lines:

            rag_facts = "\nBackground knowledge you should use naturally in your answers:\n"

            for fact in rag_lines:

                rag_facts += f"- {fact}\n"



    prompt = (

        f"=== SYSTEM INSTRUCTIONS ===\n"

        f"{system}\n\n"



        f"=== CHARACTER GUIDELINES ===\n"

        f"- You are playing the role of: **{name}**\n"

        f"- Always respond **in character**, maintaining the tone, behavior, and background of this persona.\n"

        f"- EXCEPTION: When processing tool results, focus on using the data to answer the user's question accurately while maintaining your character's voice.\n\n"



        f"BACKGROUND:\n"

        f"{bio}\n\n"



        f"PERSONALITY TRAITS:\n"

        f"{personality}\n\n"



        f"KNOWLEDGE USAGE:\n"

        f"- Use any provided knowledge or facts naturally in conversation.\n"

        f"- Never say or imply that you are referencing external context.\n"

        f"- Weave information seamlessly into your responses.\n\n"



        f"{rag_facts}"

    )



    if example_responses:

        prompt += "\nEXAMPLE RESPONSES (for style and reference):\n"

        for ex in example_responses:

            prompt += f"- {ex}\n"

    

    if all_tools:

        prompt += "\nTOOLS AVAILABLE:\n"

        # Iterate through tools and format them

        for tool_key in all_tools:

            # If tool is a string, look up in registry

            if isinstance(tool_key, str) and tool_key in TOOL_REGISTRY:

                tool_data = TOOL_REGISTRY[tool_key]  # tool_data is {'function': <callable>, 'schema': {...}}

                

                # Access the schema from tool_data

                schema = tool_data['schema']

                

                # Get tool information from schema

                tool_name = schema.get('name', tool_key)

                tool_description = schema.get('description', 'No description available')

                

                prompt += f"- {tool_name}: {tool_description}\n"

                

                # Add parameters if they exist

                if 'parameters' in schema and 'properties' in schema['parameters']:

                    parameters = schema['parameters']['properties']

                    required_params = schema['parameters'].get('required', [])

                    

                    prompt += "  Parameters:\n"

                    for param_name, param_info in parameters.items():

                        param_type = param_info.get('type', 'string')

                        param_desc = param_info.get('description', 'No description')

                        is_required = "(REQUIRED)" if param_name in required_params else "(OPTIONAL)"

                        

                        prompt += f"    - {param_name} ({param_type}) {is_required}: {param_desc}\n"

                        

                        # Add default value if present

                        if 'default' in param_info:

                            prompt += f"      Default: {param_info['default']}\n"

                

            # If tool is a dict, use its info directly

            elif isinstance(tool_key, dict):

                tool_name = tool_key.get('name', 'Unknown')

                tool_description = tool_key.get('description', 'No description available')

                prompt += f"- {tool_name}: {tool_description}\n"

                

                # Add parameters if they exist in the dict

                if 'parameters' in tool_key:

                    prompt += f"  Parameters: {tool_key['parameters']}\n"

            else:

                prompt += f"- {str(tool_key)}: Tool not found in registry\n"

        

    prompt += (
        "\n=== TOOL USAGE INSTRUCTIONS ===\n"
        "WORKFLOW:\n"
        "1. PLANNING: When a user question requires tools, think about ALL tools needed and call them together in ONE response.\n"
        "   - For tasks requiring multiple similar operations (like 'roll 3 dice'), make multiple tool calls at once\n"
        "   - For complex tasks, identify all required tools and call them simultaneously\n\n"
        
        "2. TOOL CALL FORMAT (use EXACT format, no code blocks):\n"
        "   FUNCTION: <tool_name> PARAMS: { 'param1': 'value1', 'param2': 'value2' }\n"
        "   Example: FUNCTION: weather PARAMS: { 'location': 'New York' }\n"
        "   IMPORTANT: Do NOT wrap tool calls in code blocks or backticks\n\n"
        
        "   MULTIPLE TOOLS (preferred when applicable):\n"
        "   FUNCTION: generate_random_number PARAMS: { 'min_val': 1, 'max_val': 6 }\n"
        "   FUNCTION: generate_random_number PARAMS: { 'min_val': 1, 'max_val': 6 }\n"
        "   FUNCTION: generate_random_number PARAMS: { 'min_val': 1, 'max_val': 6 }\n\n"
        
        "3. AFTER RECEIVING TOOL RESULTS:\n"
        "   - Use ALL results to answer the user's ORIGINAL question comprehensively\n"
        "   - The tool results are data for YOU to use, not something to acknowledge\n"
        "   - Integrate information naturally into your character's response\n"
        "   - Do NOT say 'thanks for the data' or 'I already knew that'\n"
        "   - Focus on answering what the user actually asked\n\n"
        
        "4. EXAMPLES:\n"
        "   User: 'Roll 3 dice'\n"
        "   You: Make 3 generate_random_number calls at once\n"
        "   Results: [4, 1, 6]\n"
        "   You: 'You rolled three dice and got: 4, 1, and 6!'\n\n"
        
        "   User: 'What's the weather in Toronto and Montreal?'\n"
        "   You: Make 2 weather calls at once\n"
        "   Results: [Toronto data, Montreal data]\n"
        "   You: Synthesize both weather reports\n\n"
        
        "5. CRITICAL: Maximize efficiency by calling multiple tools simultaneously when the task requires it.\n"
        "   This provides faster, more comprehensive responses to users.\n"
    )





    # Return the generated prompt

    # print(f"Generated system prompt: {prompt}")

    return prompt