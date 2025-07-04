import asyncio
import json
from typing import Optional
from typing import List, Dict, Any, Optional
from fastapi import Request
from pydantic import BaseModel
from ollama import Client

from app.llm import mcp_client

from app.api.prompt import sys_prompt, user_prompt

client = Client(
    host='http://192.168.128.1:11434'  # or another host if you're running Ollama elsewhere
)
from google import genai

class ChatRequest(BaseModel):
    role: str
    content: str
    history: Optional[List[Dict[str, str]]] = None
    model: str = "mistral" 

def format_yield_content(content: str):
    return f"data: {json.dumps({'content': f'{content}\n\n\n'})}\n\n"

# Hàm generator async để stream dữ liệu theo SSE
async def ollama_event_generator(request: ChatRequest, httpRequest: Request):
    messages = request.history or []
    storage = {}
    list_tools = await mcp_client.list_available_tools()
    formatted_tools = []
    for tool in list_tools:
        formatted_tools.append({
            "type": "function",
            "function": {"name": tool.name, "description": tool.description, "parameters": tool.inputSchema}
        })

    prompt = [
        {"role": "system", "content": sys_prompt()},
        {"role": "user", "content": user_prompt(messages=messages, query=request.content)},
    ]

    messages.append({"role": request.role, "content": request.content})
    res = client.chat(
        model=request.modelName,
        messages=prompt,
        stream=False,
        tools=formatted_tools,
    )

    parsed_tools = []

    for i, tool_call in enumerate(res.message['tool_calls'], start=1):
        parsed_tools.append({
            "tool": tool_call.function.name,
            "params": tool_call.function.arguments,
            "order": i
        })

    print(parsed_tools)
    for tool in parsed_tools:
        tool_order = tool['order']
        tool_name = tool["tool"]
        tool_args = tool["params"]
        tool_params = get_tool_params(tool_args, storage)
        result = await mcp_client.call_tool(tool_name, tool_params)
        stream_gen = await save_response_to_dict(tool_order, result, storage)
        async for chunk in stream_gen:
            yield chunk

    yield f"data: {json.dumps({'content': 'endddddddddddddd'})}\n\n"
    return
     
# Hàm generator async để stream dữ liệu theo SSE
async def gemini_event_generator(request: ChatRequest, httpRequest: Request):
    messages = request.history or []
    list_tools = await mcp_client.list_available_tools()
    formatted_tools = []
    for tool in list_tools:
        formatted_tools.append({
            "type": "function",
            "function": {"name": tool.name, "description": tool.description, "parameters": tool.inputSchema}
        })

    prompt = [
        {"role": "system", "content": sys_prompt()},
        {"role": "user", "content": user_prompt(messages=messages, query=request.content)},
    ]
    messages.append({"role": request.role, "content": request.content})
    client = genai.Client()
    gemini = client.chats.create(model=request.modelName) 
    res = gemini.send_message(prompt)
    print(res)
    yield format_yield_content("Hey dude, I'm Gemini, your new best friend.") 
    await asyncio.sleep(0.1)
    yield format_yield_content("Just wait a moment, I'm thinking :3") 
    await asyncio.sleep(0.1)
    try: 
        for chunk in res:
            if await httpRequest.is_disconnected():
                print("Client disconnected, cancel streaming")
                return
            content = chunk.text
            if content: 
                yield f"data: {json.dumps({'content': content})}\n\n" 
            await asyncio.sleep(0)
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

def get_model_event_generator(model: str):
    print(model)
    if model == "llama3.1":
        return ollama_event_generator
    elif model == "gemini":
        return gemini_event_generator
    else:
        raise ValueError(f"Model {model} not supported")

async def save_response_to_dict(order: int, result, storage: Dict[str, Any]):
    content = result.content
    if len(content) == 0:
        return None
    content = content[0]
    if content.type == 'text':
        name = f'result_tool_{order}'
        text = content.text
        storage[name] = text
        return fake_text_stream(text)
    return None


def get_tool_params(tool_params: Dict[str, Any], storage: Dict[str, Any]) -> Dict[str, Any]:
    for key, value in tool_params.items():
        if isinstance(value, str) and value.startswith("result_tool_"):
            resolved_value = storage.get(value)
            tool_params[key] = resolved_value
    return tool_params


async def fake_text_stream(text: str, delay: float = 0.05):
    """
    Simulates streaming by yielding one word (or character) at a time with delay.

    Args:
        text (str): The full text to stream.
        delay (float): Delay between chunks (in seconds).

    Yields:
        str: Streaming chunks of text.
    """
    for word in text.split():
        yield f"data: {json.dumps({'content': word})}\n\n"
        await asyncio.sleep(delay)