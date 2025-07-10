from typing import Dict, List
from ollama import Client


OLLAMA_HOST="http://127.0.0.1:11434"
# OLLAMA_HOST="http://192.168.128.1:11434"
OLLAMA_MODEL="mistral"

client = Client(
    host=OLLAMA_HOST
)
def ask_llm(messages: List[Dict[str, str]], stream: bool = False) -> str:
    return client.chat(model=OLLAMA_MODEL, messages=messages, stream=stream)