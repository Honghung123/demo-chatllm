import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file from current directory or parent directories

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL") 
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

