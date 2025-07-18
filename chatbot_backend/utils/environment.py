import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file from current directory or parent directories

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL") 
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

SERVER_HOST=os.getenv("SERVER_HOST")
SERVER_PORT=os.getenv("SERVER_PORT")
FE_URL=os.getenv("FE_URL")
FE_DEPLOY_URL=os.getenv("FE_DEPLOY_URL")