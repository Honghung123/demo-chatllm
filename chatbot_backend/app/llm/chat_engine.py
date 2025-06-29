import asyncio
import json
from typing import List, Dict, Optional, Sequence, Union, Mapping, Any, Callable
import ollama

from app.llm.langchain_agent import run_agent
from . import mcp_client

from app.llm.prompt_templates import TOOL_SELECTION_FORMAT, TOOL_SELECTION_PROMPT 

def parse_tools_to_call(response_text: str):
    try:
        # Strip any markdown formatting if present
        if "```json" in response_text:
            json_content = response_text.split("```json")[1].split("```")[0].strip()
            response_text = json_content
        elif "```" in response_text:
            json_content = response_text.split("```")[1].split("```")[0].strip()
            response_text = json_content
            
        data = json.loads(response_text)
        if isinstance(data, list):
            # Handle list of tools
            tools = []
            for tool_data in data:
                tool_name = tool_data.get("tool_name")
                tool_args = tool_data.get("parameters", {})
                if tool_name:
                    tools.append({"name": tool_name, "parameters": tool_args})
            return tools
        else:
            print("Error, must be a list of tools")
            return []
    except Exception as e:
        print(f"Error parsing tool call: {str(e)}")
        print(f"Response text was: {response_text}")
        return []

async def process_request_message(
        prompt: str, 
        history: Optional[List[Dict[str, str]]] = None, 
        on_chunk: Optional[callable] = None
) -> None: 
    # res = await run_agent(prompt)
    # on_chunk(res) 
    # return
    on_chunk("Getting tools...\n")
    list_tools = await mcp_client.list_available_tools()
    on_chunk(f"Got {len(list_tools)} tools.\n")
    print(list_tools)
    formatted_tools = []
    for tool in list_tools: 
        formatted_tools.append({
            "type": "function",
            "function": {"name": tool.name, "description": tool.description, "parameters": tool.inputSchema}
        })   
    messages = history.copy() if history else []
    request_prompt = TOOL_SELECTION_PROMPT.format(query=prompt, format=TOOL_SELECTION_FORMAT)
    messages.append({"role": "user", "content": request_prompt}) 
    on_chunk("Chat model is processing the request to get tools...\n")
    response = chat_llm(messages=messages, tools=formatted_tools, streaming=True, on_chunk=on_chunk)
    print(response)
    on_chunk("\nChat completed. Parsing tools...\n")
    tools_to_call = parse_tools_to_call(response)
    if not tools_to_call:
        print("No valid tools to call were found in the response")
        return
        
    try:
        on_chunk("Executing tools...\n")
        print(f"First tool to execute: {tools_to_call[0]['name']}")
        for tool in tools_to_call:
            tool_name = tool["name"]
            tool_args = tool["parameters"]
            print(f"Executing tool: {tool_name} with parameters: {tool_args}")
            result = await mcp_client.call_tool(tool_name, tool_args)
            print(result)
        on_chunk("✅ All tools executed successfully\n")
    except Exception as e:
        print(f"Error executing tools: {str(e)}")
        return

def chat_llm( 
    messages: Optional[List[Dict[str, str]]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    model: str = "mistral",
    streaming: bool = False, 
    on_chunk: Optional[callable] = None
) -> str: 
    try:     
        response = ollama.chat(
            model=model, 
            messages=messages, 
            stream=streaming,
            tools=tools
        ) 
        if streaming: 
            # Process streaming response
            result = ""
            try:
                for chunk in response:
                    content = chunk.get("message", {}).get("content", "")
                    if on_chunk:
                        on_chunk(content) 
                    else:
                        print(content, end='', flush=True)
                    result += content
            except Exception as stream_err:
                if on_chunk:
                    on_chunk(f"\n❌ Error streaming response: {str(stream_err)}")
                else:
                    print("\n❌ Error streaming response:", str(stream_err))
            return result
        else:
            return response['message']['content']
    except Exception as e:
        err = f"❌ Unexpected error: {str(e)}"
        print(err)
        if on_chunk:
            on_chunk(err)
        return None 


"""
messages = history.copy() if history else []
    request_prompt = TOOL_SELECTION_PROMPT.format(query=prompt, format=TOOL_SELECTION_FORMAT)
    messages.append({"role": "user", "content": request_prompt}) 
    try:
        print("Getting tools...")
        tools = mcp_client.list_available_tools()
        formatted_tools = []
        for tool in tools: 
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        print("Chat is responding...")
        list_tools_string_response = chat_llm(messages=messages, tools=formatted_tools, streaming=True, on_chunk=on_chunk)
        list_tools = parse_tool_call(list_tools_string_response)
        print(list_tools) 
"""