# app/api.py
from datetime import datetime 
import os
import uuid
from fastapi import FastAPI, File, Form, HTTPException, BackgroundTasks, Request, UploadFile
from fastapi.responses import StreamingResponse 
from pydantic import BaseModel
from typing import List, Dict, Any, Optional 
import uvicorn
import os
from fastapi.middleware.cors import CORSMiddleware
from app.api.model_provider import ChatRequest, ollama_event_generator  
from app.schema.conversation import Conversation
from app.schema.file import FileSystem
from app.schema.message import Message
from app.schema.role import Role
from app.service.conversation_service import ConversationService
from app.service.file_service import FileService
from app.service.role_service import RoleName, RoleService
from app.service.user_service import UserService
from app.service.message_service import MessageService
from app.file.file_pre_processing import preprocess_text
from app.file.file_loader import load_file
from app.search.document import Document
from app.service.db_service import truncate_all_tables
from utils.file_utils import get_root_path
from utils.environment import FE_URL, FE_DEPLOY_URL, SERVER_HOST, SERVER_PORT
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
            "description": "Best for complex tasks",
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

@app.get("/roles", response_model=List[Role])
async def get_all_roles():
    return RoleService.get_all()
 
@app.get("/conversations/{userId}", response_model=List[Conversation])
async def get_list_conversations(userId: str):
    return ConversationService.get_all_by_user_id(userId)

@app.post("/conversations/new/{userId}", response_model=Conversation)
async def new_conversation(userId: str):
    conversation_id = str(uuid.uuid4())
    conversation = Conversation( 
        id=conversation_id,
        user_id=userId,
        title="New conservation",
    )
    ConversationService.create(conversation)
    MessageService.create(
        message=Message(
            conversation_id=conversation_id,
            user_id=userId,
            content="Hi, I'm your assistant, how can I help you today?",
            summary="Hi, I'm your assistant, how can I help you today?",
            from_user=False,
            is_error=False, 
        )
    )
    return conversation

class ConversationRenameRequest(BaseModel):
    conversationId: str
    newTitle: str

@app.post("/conversations/rename", response_model=None)
async def rename_conversation(request: ConversationRenameRequest):
    ConversationService.rename(request.conversationId, request.newTitle)
    print(f"Conversation renamed to {request.newTitle}")

class ListFileResponse(BaseModel):
    name: str
    listFiles: List[FileSystem]

@app.get("/files/{username}", response_model=List[ListFileResponse])
def get_list_chat_histories(username: str):
    role = UserService.get_by_username(username).role
    system_files = FileService.get_system_files(role)
    personal_files = FileService.get_by_username(username)
    return [
        { 
            "name": "System",
            "listFiles": system_files
        },
        { 
            "name": "Personal",
            "listFiles": personal_files
        },
    ]
 
@app.get("/chat-histories/{userId}/{conversationId}", response_model=List[Message])
async def get_chat_history(userId: str, conversationId: str):
    return MessageService.get_all_chat(userId, conversationId)
 
@app.post("/chat", response_model=Message)
async def handle_chat(httpRequest: Request, request: ChatRequest):
    try: 
        # Trả về response dạng text/event-stream để client nhận realtime
        return StreamingResponse(ollama_event_generator(request, httpRequest), media_type="text/event-stream")
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# upload file
@app.post("/upload/{username}", response_model=List[FileSystem])
async def upload_files(username: str, files: List[UploadFile] = File(...), allowed_roles: List[str] = Form(...)):
    saved_files : List[FileSystem] = []
    documents_dir = f"{get_root_path()}/data/files" 
    for file in files:
        extension = file.filename.split(".")[-1]
        file_name_in_server = file.filename
        # Lưu tên file gốc để tái sử dụng trong vòng lặp
        original_base_name, ext = os.path.splitext(file_name_in_server)
        file_name_in_server = original_base_name + ext
        file_path = os.path.join(documents_dir, file_name_in_server)
        accumulator = 1
        while os.path.exists(file_path):
            # Tạo tên mới với số thứ tự
            file_name_in_server = f"{original_base_name}({accumulator}){ext}"
            file_path = os.path.join(documents_dir, file_name_in_server)
            accumulator += 1
        
        # Save the file to the filesystem
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        # Save file metadata
        if username != RoleName.ADMIN.split("|")[0]:
            allowed_roles = []
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
        file_system = FileSystem(name=file_name_in_server, orginal_name=file_name_in_server, extension=extension, username=username)
        FileService.create(file=file_system, roles=allowed_roles)
        saved_files.append(file_system)
    return saved_files


# clear data
@app.get("/clear-data", response_model=str)
async def clear_data():
    try:
        # clear all data in the database
        truncate_all_tables()
        chroma_db.clear_collection()
        return "Data clear successfully, please restart the server to apply changes."
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error data clear: {str(e)}")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FE_URL, FE_DEPLOY_URL],  # Allow localhost:3000
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
) 

# Run the API server
def start_api(): 
    host = SERVER_HOST
    port = int(SERVER_PORT) 
    uvicorn.run(app, host=host, port=port)
 