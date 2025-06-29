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
from utils.environment import SERVER_HOST, SERVER_PORT

app = FastAPI(
    title="Offline LLM API",
    description="API for offline LLM search and chat functionality",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow localhost:3000
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
) 

class ChatRequest(BaseModel):
    role: str
    content: str
    history: Optional[List[Dict[str, str]]] = None
    model: str
    modelName: str

class ChatResponse(BaseModel):
    id: str
    userId: str
    chatId: str
    role: str
    content: str
    timestamp: str
    isError: bool

class ConversationResponse(BaseModel):
    chatId: str
    userId: str
    title: str
    createdAt: str

class FileResponse(BaseModel):
    id: str
    userId: str
    name: str
    fileName: str
    fileNameInServer: str
    extension: str
    timestamp: str

class ListFileResponse(BaseModel):
    name: str
    listFiles: List[FileResponse]

@app.get("/ai-models", response_model=List[Dict[str, Any]])
async def getAllModels():
    return [    
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
    ] 

@app.post("/chat", response_model=ChatResponse)
async def handle_chat(httpRequest: Request, request: ChatRequest):
    try:
        event_generator = get_model_event_generator(request.model)
        # Trả về response dạng text/event-stream để client nhận realtime
        return StreamingResponse(event_generator(request, httpRequest), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/chat-histories/{userId}", response_model=List[ConversationResponse])
async def get_list_chat_histories(userId: str):
    return [
	    { 
            "chatId": "1", 
            "userId": userId,
            "title": "A conservation", 
            "createdAt": "2025-05-31T15:30:00Z" 
        }, 
    ]

@app.get("/files/{userId}", response_model=List[ListFileResponse])
async def get_list_chat_histories(userId: str):
    return [
	{ 
		"name": "System",
		"listFiles": [
			{
				"id": "1",
                "userId": userId,
				"name": "Ke hoach 2025",
				"fileName": "Ke hoach 2025.docx",
                "fileNameInServer": "abdfesdff.docx",
				"extension": "docx",
				"timestamp": "2025-05-31T15:30:00Z",
			},
			{
				"id": "2",
                "userId": userId,
				"name": "demo",
				"fileName": "demo.pdf",
                "fileNameInServer": "wrcvxddx.pdf",
				"extension": "pdf",
				"timestamp": "2025-05-31T15:30:00Z",
			},
			{
				"id": "3",
                "userId": userId,
				"name": "test",
				"fileName": "test.pdf",
                "fileNameInServer": "ecxafttx.pdf",
				"extension": "pdf",
				"timestamp": "2025-05-31T15:30:00Z",
			},
		],
	},
	{ 
		"name": "Persional",
		"listFiles": [
			{
				"id": "1",
                "userId": userId,
				"name": "Marketing plan",
				"fileName": "Marketing plan.txt",
                "fileNameInServer": "zfsfsfsd.txt",
				"extension": "txt",
				"timestamp": "2025-05-31T15:30:00Z",
			},
			{
				"id": "2",
                "userId": userId,
				"name": "notes",
				"fileName": "notes.pptx",
                "fileNameInServer": "khklkjhd.pptx",
				"extension": "pptx",
				"timestamp": "2025-05-31T15:30:00Z",
			},
		],
	},
]

@app.get("/chat-histories/{userId}/{chatId}", response_model=List[ChatResponse])
async def get_chat_history(userId: str, chatId: str):
    return [
		{
			"id": "1",
            "userId": userId,
			"chatId": chatId,
			"role": "assistant",
			"content": "Hello! I'm an AI assistant. How can I help you today?",
			"timestamp": datetime.now().isoformat(),
			"isError": False,
		},
	]

@app.post("/new-conversation/{userId}", response_model=ConversationResponse)
async def new_conversation(userId: str):
    return { 
        "chatId": str(random.randint(100, 1000000)), 
        "userId": userId,
        "title": "Start a new conservation", 
        "createdAt": datetime.now().isoformat() }

@app.post("/upload/{userId}", response_model=List[FileResponse])
async def upload_file(userId: str, files: List[UploadFile] = File(...)):
    saved_files = []
    user_dir = f"mcp_server/files/{userId}" 
    if not os.path.exists(user_dir):
        os.makedirs(user_dir, exist_ok=True) 
    for file in files:
        fileNameInServer = str(uuid.uuid4())[:8]
        extension = file.filename.split(".")[-1]
        file_path = os.path.join(user_dir, f"{fileNameInServer}.{extension}") 
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents) 
        saved_files.append({
            "id": str(random.randint(100, 1000000)),
            "userId": userId,
            "name": file.filename.split(".")[0],
            "fileName": file.filename,
            "fileNameInServer": fileNameInServer,
            "extension": extension,
            "timestamp": datetime.now().isoformat(),
        })
    return saved_files
 
# Run the API server
def start_api(): 
    host = SERVER_HOST
    port = int(SERVER_PORT)
    print(f"Starting API server on {SERVER_HOST}:{SERVER_PORT}")
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