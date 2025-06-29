import asyncio
import json
from typing import Optional
from typing import List, Dict, Any, Optional
from fastapi import Request
from pydantic import BaseModel
import ollama
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
    # Gọi Ollama chat với stream=True để nhận token từng phần
    messages = request.history or []
    messages.append({"role": request.role, "content": request.content})  

    # Tạo một future để chạy ollama.chat trong một thread riêng biệt
    loop = asyncio.get_running_loop()
    # Khởi tạo stream từ ollama
    stream = await loop.run_in_executor(
        None, 
        lambda: ollama.chat(
            model=request.modelName,
            messages=messages,
            stream=True
        )
    )  

    # Xử lý từng chunk một cách đồng bộ
    async def process_stream():
        yield format_yield_content("Ollama is starting response...") 
        await asyncio.sleep(0.1)
        yield format_yield_content("Be patient, it may take a while...") 
        await asyncio.sleep(0.1)
        try: 
            for chunk in stream:
                if await httpRequest.is_disconnected():
                    print("Client disconnected, cancel streaming")
                    return
                content = chunk.get("message", {}).get("content", "") 
                if content:
                    # Trả về từng phần nhỏ ngay khi nhận được
                    yield f"data: {json.dumps({'content': content})}\n\n"
                # Nhường quyền điều khiển cho event loop
                await asyncio.sleep(0)
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    # Trả về từng phần của phản hồi
    async for chunk in process_stream():
        yield chunk

# Hàm generator async để stream dữ liệu theo SSE
async def gemini_event_generator(request: ChatRequest, httpRequest: Request):
    # Gọi Ollama chat với stream=True để nhận token từng phần
    messages = request.history or []
    messages.append({"role": request.role, "content": request.content})   

    client = genai.Client()
    gemini = client.chats.create(model=request.modelName) 
    stream = gemini.send_message_stream(request.content)

    # Xử lý từng chunk một cách đồng bộ
    async def process_stream():
        yield format_yield_content("Hey dude, I'm Gemini, your new best friend.") 
        await asyncio.sleep(0.1)
        yield format_yield_content("Just wait a moment, I'm thinking :3") 
        await asyncio.sleep(0.1)
        try: 
            for chunk in stream: 
                if await httpRequest.is_disconnected():
                    print("Client disconnected, cancel streaming")
                    return
                content = chunk.text
                if content:
                    # Trả về từng phần nhỏ ngay khi nhận được
                    yield f"data: {json.dumps({'content': content})}\n\n"
                # Nhường quyền điều khiển cho event loop
                await asyncio.sleep(0)
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    # Trả về từng phần của phản hồi
    async for chunk in process_stream():
        yield chunk

def get_model_event_generator(model: str):
    if model == "ollama":
        return ollama_event_generator
    elif model == "gemini":
        return gemini_event_generator
    else:
        raise ValueError(f"Model {model} not supported")
