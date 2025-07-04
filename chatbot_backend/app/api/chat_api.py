# app/api.py
from datetime import datetime 
import random
import uuid
from fastapi import FastAPI, File, HTTPException, BackgroundTasks, Request, UploadFile
from fastapi.responses import StreamingResponse 
from pydantic import BaseModel
from typing import List, Dict, Any, Optional 
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from app.api.model_provider import get_model_event_generator  
from app.schema.conversation import Conversation
from app.schema.file import FileSystem
from app.schema.message import Message
from app.schema.role import RoleName
from app.service.conversation_service import ConversationService
from app.service.file_service import FileService
from app.service.user_service import UserService
from app.service.message_service import MessageService
from utils.environment import SERVER_HOST, SERVER_PORT

app = FastAPI(
    title="Offline LLM API",
    description="API for offline LLM search and chat functionality",
    version="1.0.0"
)

aiModels = [    
        {
            "model": "gemini",
            "modelName": "gemini-2.5-flash",
            "displayName": "Gemini",
            "description": "Our smartest model & more",
        },
        {
            "model": "ollama",
            "modelName": "mistral",
            "displayName": "Ollama - Mistral",
            "description": "Great for everyday tasks",
        },
{
            "model": "llama3.1",
            "modelName": "llama3.1",
            "displayName": "Ollama - llama3.1",
            "description": "Great for everyday tasks",
        },
    ]

@app.get("/ai-models", response_model=List[Dict[str, Any]])
async def getAllModels():
    return aiModels  

class LoginRequest(BaseModel):
    username: str
    password: str
    
@app.post("/login", response_model=Dict[str, Any])
async def login(request: LoginRequest): 
    user = UserService.authenticate(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    print("Authenticated user:", user.to_response_dict())
    return user.to_response_dict()
 
@app.get("/conversations/{userId}", response_model=List[Conversation])
async def get_list_conversations(userId: str):
    return ConversationService.get_all_by_user_id(userId)

@app.post("/conversations/new/{userId}", response_model=Conversation)
async def new_conversation(userId: str):
    conversation = Conversation( 
        user_id=userId,
        title="New conservation",
    )
    ConversationService.create(conversation)
    return conversation
class ListFileResponse(BaseModel):
    name: str
    listFiles: List[FileSystem]

@app.get("/files/{username}", response_model=List[ListFileResponse])
def get_list_chat_histories(username: str):
    system_files = FileService.get_by_username(RoleName.ADMIN)
    personal_files = FileService.get_by_username(username)
    return [
        { 
            "name": "System",
            "listFiles": system_files
        },
        { 
            "name": "Persional",
            "listFiles": personal_files
        },
    ]
 
@app.get("/chat-histories/{userId}/{conversationId}", response_model=List[Message])
async def get_chat_history(userId: str, conversationId: str):
    return MessageService.get_all_chat(userId, conversationId)

class ChatRequest(BaseModel):
    conversationId: str
    userId: str
    role: str
    content: str
    history: Optional[List[Dict[str, str]]] = None
    model: str
    modelName: str
 
@app.post("/chat", response_model=Message)
async def handle_chat(httpRequest: Request, request: ChatRequest):
    try:
        event_generator = get_model_event_generator(request.model)
        # Trả về response dạng text/event-stream để client nhận realtime
        return StreamingResponse(event_generator(request, httpRequest), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@app.post("/upload/{username}", response_model=List[FileSystem])
async def upload_file(username: str, files: List[UploadFile] = File(...)):
    saved_files = []
    user_dir = f"mcp_server/files/{username}" 
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True) 
    for file in files:
        fileNameInServer = str(uuid.uuid4())[:8]
        extension = file.filename.split(".")[-1]
        file_path = os.path.join(user_dir, f"{fileNameInServer}.{extension}") 
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents) 
        saved_files.append(FileSystem(name=fileNameInServer, orginal_name=file.filename, extension=extension, username=username))
    return saved_files

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow localhost:3000
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
) 

# Run the API server
def start_api(): 
    host = SERVER_HOST
    port = int(SERVER_PORT) 
    uvicorn.run(app, host=host, port=port)

"""
@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    try:
        results = retriever.search(request.query, request.top_k)
        return SearchResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.post("/files/index", response_model=IndexFilesResponse)
async def index_files(request: IndexFilesRequest):
    try:
        # Count files before indexing
        docs_dir = "data/documents"
        file_count = 0
        for root, _, files in os.walk(docs_dir):
            for file in files:
                if file.lower().endswith(('.pdf', '.docx', '.pptx', '.doc', '.ppt')) and not file.startswith('.'):
                    file_count += 1
        
        # Index files
        success = retriever.index_files(force_reindex=request.force_reindex)
        
        if success:
            return IndexFilesResponse(
                success=True,
                message=f"Successfully indexed {file_count} files",
                file_count=file_count
            )
        else:
            return IndexFilesResponse(
                success=False,
                message="No files were indexed",
                file_count=0
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing error: {str(e)}")

@app.post("/agent/chat", response_model=AgentResponse)
async def agent_chat(request: AgentRequest):
    try:
        # Get or create agent instance
        session_id = request.session_id
        if not session_id or session_id not in agent_instances:
            agent = AdvancedMemoryAgent()
            session_id = agent.session_id
            agent_instances[session_id] = agent
        else:
            agent = agent_instances[session_id]
        
        # Process with agent
        response = await agent.run_conversation(request.query)
        
        return AgentResponse(
            response=response,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.get("/agent/sessions/{session_id}/stats")
async def get_agent_memory_stats(session_id: str):
    if session_id not in agent_instances:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    agent = agent_instances[session_id]
    stats = agent.get_memory_stats()
    return {"session_id": session_id, "stats": stats}
"""