import asyncio
import json
from typing import List, Dict, Any, Optional
from fastapi import Request
from pydantic import BaseModel
from ollama import Client 
from app.llm import mcp_client

from app.api.prompt import sys_prompt, user_prompt

from app.schema.message import Message
from app.service.message_service import MessageService
from utils.environment import OLLAMA_BASE_URL

class ChatRequest(BaseModel):
    conversationId: str
    userId: str
    username: str
    userRole: str
    role: str
    content: str
    history: Optional[List[Dict[str, str]]] = None
    model: str
    modelName: str

client = Client(
    host=OLLAMA_BASE_URL 
) 

def format_yield_content(content: str):
    return f"data: {json.dumps({'content': f'{content}\n\n\n'})}\n\n"  

def parse_response_text(response_text: str): 
    if "```json" in response_text:
        json_content = response_text.split("```json")[1].split("```")[0].strip()
        response_text = json_content.strip()
    elif "```" in response_text:
        json_content = response_text.split("```")[1].split("```")[0].strip()
        response_text = json_content.strip() 
    try:
        return json.loads(response_text)
    except Exception as e:
        return {
            "message": response_text
        }

def determine_message_type(data: Any): 
    if isinstance(data, list):
        return "list"
    elif isinstance(data, dict): 
        if "message" in data:
            return "message"
        else:
            return "error"
    else:
        return "error"

def parse_tools_to_call(data: Any):
    try: 
        tools = []
        for tool_data in data:
            tool_name = tool_data.get("name")
            tool_args = tool_data.get("arguments", {})
            tool_order = tool_data.get("order", len(tools) + 1)
            if tool_name:
                tools.append({"name": tool_name, "arguments": tool_args, "order": tool_order})
        return tools 
    except Exception as e:
        print(f"Error parsing tool call: {e}") 
        return None

# Hàm generator async để stream dữ liệu theo SSE
async def ollama_event_generator(request: ChatRequest, httpRequest: Request): 
    list_tools = await mcp_client.list_available_tools()
    formatted_tools = []
    toolMapper = {} 
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
        toolMapper[tool.name] = tool.annotations.title  
    chatResponseMessage = ""
    chatResponseSummaryMessage = ""
    historyMessage = MessageService.get_all_chat(request.userId, request.conversationId)
    histories = [{"role": "user" if message.from_user else "assistant", "content": message.summary} for message in historyMessage]
    prompt = [
        {"role": "system", "content": sys_prompt(request.username, request.userRole, formatted_tools, histories)},
        {
            "role": "user",
            "content": user_prompt(request.username, request.role, request.content),
        },
    ]  
    MessageService.create(Message(conversation_id=request.conversationId, user_id=request.userId, content=request.content, summary=request.content, from_user=True))
    res = client.chat(
        model=request.modelName,
        messages=prompt,
        stream=False, 
    )    
    parsed_response = []
    print('res.message.content', res.message.content)
    try:
        if not res.message.content:
            parsed_response = []
            for i, tool_call in enumerate(res.message["tool_calls"], start=1):
                parsed_response.append(
                    {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                )
        else:
            parsed_response = parse_response_text(res.message.content)   
        print('parsed_response', parsed_response)
        message_type = determine_message_type(parsed_response)
        if message_type == "error":
            if isinstance(parsed_response, str):
                yield format_yield_content(parsed_response)
                chatResponseMessage += "\n" + parsed_response
                chatResponseSummaryMessage += parsed_response + ", "
            elif isinstance(parsed_response, dict):
                yield format_yield_content(parsed_response['error']) 
                chatResponseMessage += "\n" + parsed_response['error']
                chatResponseSummaryMessage += parsed_response['error'] + ", "
            await asyncio.sleep(0.1)
        elif message_type == "message":
            chatResponseMessage += "\n" + parsed_response['message']
            chatResponseSummaryMessage += parsed_response['message'] + ", "
            yield format_yield_content(parsed_response['message'])
            await asyncio.sleep(0.1)
        elif message_type == "list": 
            parsed_tools = parse_tools_to_call(parsed_response)
            if not parsed_tools:
                yield format_yield_content("No tools to call")
                chatResponseMessage += "\n" + "No tools to call"
                chatResponseSummaryMessage += "No tools to call, "
                return
            yield format_yield_content("Here are the steps to complete the task:")
            chatResponseMessage += "\n" + "Here are the steps to complete the task:"
            async for step in stream_tool_plan_steps(parsed_tools, toolMapper):
                yield step
                chatResponseMessage += step
            storage = {}
            index = 1
            for tool in parsed_tools: 
                tool_name = tool.get("name", "")
                tool_args = tool.get("arguments", {})
                tool_params = get_tool_params(tool_args, storage)
                content = f"🚀 Executing step {index}: {displayToolMessage(toolMapper.get(tool_name), tool_params)}"
                chatResponseMessage += "\n" + content
                yield format_yield_content(content)
                await asyncio.sleep(0.1)
                result = await mcp_client.call_tool(tool_name, tool_params)
                if (result.isError):
                    print('result', result)
                    # raise Exception()
                if tool_name.startswith("search_file"):
                    if(not result.content or len(result.content) == 0):
                        raise Exception("FILE_NOT_FOUND")
                chatResponseSummaryMessage += f"{displayToolMessage(toolMapper.get(tool_name), tool_params)}: {result.content[0].text if len(result.content) > 0 else ''}, " 
                
                tool_result = save_response_to_dict(tool_name, result, storage)
                chatResponseMessage += tool_result
                yield format_yield_content(tool_result)
                index += 1
        yield format_yield_content("\n🎉 Done!")  
        chatResponseMessage += "\n🎉 Done!"
    except Exception as e:
        print(e)
        if(str(e) == "FILE_NOT_FOUND"):
            yield format_yield_content(f"No such file was found in the system!")
            chatResponseMessage += "\n" + f"File not found."
        else:
            yield format_yield_content(f"Failed to response. Please try again.")
            chatResponseMessage += "\n" + f"Failed to response. Please try again."
    MessageService.create(
        message=Message(
            conversation_id=request.conversationId,
            user_id=request.userId,
            content=chatResponseMessage,
            summary=chatResponseSummaryMessage,
            from_user=False
        )
    )
    return

def get_model_event_generator(): 
    return ollama_event_generator 

def save_response_to_dict(tool_name: str, result, storage: Dict[str, Any]):
    content = result.content
    if len(content) == 0:
        return ""
    content = content[0]
    if content.type == "text":
        name = f"result_{tool_name}"
        text = content.text
        storage[name] = text 
        return text
    return ""


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
 
def displayToolMessage(toolMessage: str, toolParams: Dict[str, Any]):
    print(toolMessage, toolParams)
    message = f"`{toolMessage}`"
    # Replace placeholders in the message with actual parameter values
    for key, value in toolParams.items():
        placeholder = f"{{{key}}}"
        if placeholder in message:
            message = message.replace(placeholder, str(value))
    return message

async def stream_tool_plan_steps(
    parsed_tools: List[Dict[str, Any]], toolMapper: Dict[str, str] = {}
):
    should_show_step = len(parsed_tools) > 0
    index = 1
    for tool in parsed_tools:
        step = f"🔧 Step {index}: " if should_show_step else ""
        tool_name = tool.get("name", "")
        tool_args = tool.get("arguments", {})
        tool_message = toolMapper.get(tool_name, tool_name)
        yield format_yield_content(f"{step}{displayToolMessage(tool_message, tool_args)}")
        await asyncio.sleep(0.1)
        index += 1
 