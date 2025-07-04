import asyncio
import json
from typing import List, Dict, Any, Optional
from fastapi import Request
from pydantic import BaseModel
from ollama import Client 
from app.llm import mcp_client

from app.api.prompt import SYSTEM_PROMPT, sys_prompt, user_prompt

from app.schema.message import Message
from app.service.message_service import MessageService
from utils.environment import OLLAMA_BASE_URL

class ChatRequest(BaseModel):
    conversationId: str
    userId: str
    role: str
    content: str
    history: Optional[List[Dict[str, str]]] = None
    model: str
    modelName: str

client = Client(
    host=OLLAMA_BASE_URL 
)
from google import genai

def format_yield_content(content: str):
    return f"data: {json.dumps({'content': f'{content}\n\n\n'})}\n\n"

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
                tool_name = tool_data.get("tool")
                tool_args = tool_data.get("params", {})
                tool_order = tool_data.get("order")
                if tool_name:
                    tools.append({"tool": tool_name, "params": tool_args, "order": tool_order})
            return tools
        else:
            print("Error, must be a list of tools")
            return []
    except Exception as e:
        print(f"Error parsing tool call: {str(e)}")
        print(f"Response text was: {response_text}")
        return []

# Hàm generator async để stream dữ liệu theo SSE
async def ollama_event_generator(request: ChatRequest, httpRequest: Request):
    list_tools = await mcp_client.list_available_tools()
    formatted_tools = []
    for tool in list_tools:
        formatted_tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
        ) 
    MessageService.create(Message(conversation_id=request.conversationId, user_id=request.userId, content=request.content, from_user=True))
    chatResponseMessage = ""
    historyMessage = MessageService.get_all_chat(request.userId, request.conversationId)
    histories = [{"role": "user" if message.from_user else "assistant", "content": message.content} for message in historyMessage]
    prompt = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *histories,
        {
            "role": "user",
            "content": request.content,
        },
    ] 
    res = client.chat(
        model=request.modelName,
        messages=prompt,
        stream=False,
        tools=formatted_tools, 
    ) 
    parsed_tools = parse_tools_to_call(res.message.content) 
    print(parsed_tools)
    async for step in stream_tool_plan_steps(parsed_tools):
        chatResponseMessage += step
        yield step
    storage = {}
    for tool in parsed_tools:
        tool_order = tool["order"]
        tool_name = tool["tool"]
        tool_args = tool["params"]
        content = f"⚙️ Executing `{tool_name}` (Step {tool_order})..."
        tool_params = get_tool_params(tool_args, storage)
        yield format_yield_content(content)
        chatResponseMessage += content
        result = await mcp_client.call_tool(tool_name, tool_params)
        stream_gen = await save_response_to_dict(tool_name, result, storage)
        async for chunk in stream_gen:
            chatResponseMessage += chunk
            yield chunk

    MessageService.create(
        message=Message(
            conversation_id=request.conversationId,
            user_id=request.userId,
            content=chatResponseMessage,
            from_user=False
        )
    )
    yield format_yield_content("")
    return


# Hàm generator async để stream dữ liệu theo SSE
async def gemini_event_generator(request: ChatRequest, httpRequest: Request):
    messages = request.history or []
    list_tools = await mcp_client.list_available_tools()
    formatted_tools = []
    for tool in list_tools:
        formatted_tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
        )

    prompt = [
        {"role": "system", "content": sys_prompt()},
        {
            "role": "user",
            "content": user_prompt(messages=messages, query=request.content),
        },
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
    if model == "ollama":
        return ollama_event_generator
    elif model == "gemini":
        return gemini_event_generator
    else:
        raise ValueError(f"Model {model} not supported")


async def save_response_to_dict(tool_name: str, result, storage: Dict[str, Any]):
    content = result.content
    if len(content) == 0:
        return None
    content = content[0]
    if content.type == "text":
        name = f"result_{tool_name}"
        text = content.text
        storage[name] = text
        return fake_text_stream(text)
    return None


def get_tool_params(
    tool_params: Dict[str, Any], storage: Dict[str, Any]
) -> Dict[str, Any]:
    import ast
    for key, value in tool_params.items():
        if isinstance(value, str) and value.startswith("[") and value.endswith("]"):
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                tool_params[key] = parsed
        if isinstance(value, str) and value.startswith("result_"):
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
    import re

    # Use regex to split while keeping spaces before words
    words = re.findall(r"\s*\S+", text)

    for word in words:
        yield f"data: {json.dumps({'content': f'{word}'})}\n\n"
        await asyncio.sleep(delay)

    yield format_yield_content("\n\n")


async def stream_tool_plan_steps(
    parsed_tools: List[Dict[str, Any]], delay: float = 0.1
):
    for tool in parsed_tools:
        tool_name = tool["tool"]
        order = tool["order"]
        params = tool["params"]

        param_str = ", ".join(f"{k}={json.dumps(v)}" for k, v in params.items())
        step_msg = f"🔧 Step {order}: `{tool_name}` → Params: {param_str}"
        yield format_yield_content(step_msg)
        await asyncio.sleep(delay)

    yield format_yield_content("🚀 Executing tools now... Please wait.")
