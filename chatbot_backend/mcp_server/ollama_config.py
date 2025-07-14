from typing import Dict, List
from ollama import Client
from google import genai
from google.genai import types

OLLAMA_HOST="http://127.0.0.1:11434"
# OLLAMA_HOST="http://192.168.128.1:11434"
OLLAMA_MODEL="mistral" 
GEMINI_API_KEY="AIzaSyCkWq648GmBm4BQwuY_q9-yHiZ4oC4sbz8"

client = Client(
    host=OLLAMA_HOST
)
# def ask_llm(messages: List[Dict[str, str]], stream: bool = False) -> str:
#     return client.chat(model=OLLAMA_MODEL, messages=messages, stream=stream)

client = genai.Client(api_key=GEMINI_API_KEY)
def ask_llm(messages: List[Dict[str, str]], stream: bool = False) -> str:
    contents = [
        types.Content(role="model", parts=[types.Part(text=messages[0]["content"])]), 
        types.Content(role="user", parts=[types.Part(text=messages[1]["content"])])
    ]
    return client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disable thinking for faster response
        )
    )