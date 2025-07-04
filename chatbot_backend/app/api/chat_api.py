# app/api.py
from datetime import datetime 
import random
import uuid
from fastapi import FastAPI, File, Form, HTTPException, BackgroundTasks, Request, UploadFile
from fastapi.responses import StreamingResponse 
from pydantic import BaseModel
from typing import List, Dict, Any, Optional 
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from app.api.model_provider import ChatRequest, get_model_event_generator  
from app.schema.conversation import Conversation
from app.schema.file import FileSystem
from app.schema.message import Message
from app.schema.role import RoleName
from app.service.conversation_service import ConversationService
from app.service.file_service import FileService
from app.service.user_service import UserService
from app.service.message_service import MessageService
from app.files.file_metadata_manager import add_metadata
from app.files.file_pre_processing import preprocess_text
from app.search.document import Document
from app.files.file_loader import load_file
from utils.environment import SERVER_HOST, SERVER_PORT
from app.search.vector_db import chroma_db

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
            "model": "ollama",
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
    files_dir = f"../data/files" 
     
    for file in files:
        extension = file.filename.split(".")[-1]
        file_name_in_server = f"{str(uuid.uuid4())[:8]}.{extension}"
        file_path = os.path.join(files_dir, file_name_in_server) 
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents) 
        
        # Save file metadata
        add_metadata(file_name=file_name_in_server, author=username, roles=[])
        # embed file content into ChromaDB
        contents = load_file(file_path)
        chunks = preprocess_text(contents)  # Ensure contents are decoded to string
        docs = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                id=uuid.uuid4(),
                content=chunk,
                metadata={
                    "filename": file_name_in_server,
                }
            )
            docs.append(doc)
        chroma_db.add_documents(docs)
        # save file to database
        file_system = FileSystem(name=file_name_in_server, orginal_name=file.filename, extension=extension, username=username)
        FileService.create(file=file_system)
        saved_files.append(file_system)
    return saved_files

# upload file for admin
@app.post("/upload", response_model=List[FileSystem])
async def upload_file(files: List[UploadFile] = File(...), roles: List[str] = Form(...)):
    saved_files = []
    documents_dir = f"../data/files" 
    for file in files:
        extension = file.filename.split(".")[-1]
        file_name_in_server = f"{str(uuid.uuid4())[:8]}.{extension}"
        file_path = os.path.join(documents_dir, file_name_in_server) 
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        # Save file metadata
        add_metadata(file_name=file_name_in_server, author="admin", roles=roles)
        # embed file content into ChromaDB
        contents = load_file(file_path)
        chunks = preprocess_text(contents)  # Ensure contents are decoded to string
        docs = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                id=uuid.uuid4(),
                content=chunk,
                metadata={
                    "filename": file_name_in_server,
                }
            )
            docs.append(doc)
        chroma_db.add_documents(docs)
        # save file to database
        file_system = FileSystem(name=file_name_in_server, orginal_name=file.filename, extension=extension, username="admin")
        FileService.create(file=file_system)
        saved_files.append(file_system)
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