# ChatLLM: Offline AI Chat 
This repository a chat application that leverages local Large Language Models (LLMs) to provide an offline, private, and intelligent assistant. The application is capable of searching through user-uploaded documents and executing complex tasks through a series of tools orchestrated by the Model Context Protocol (MCP).
The system consists of a Next.js frontend, a FastAPI backend, an MCP tool server, and integrates with Ollama for local LLM inference.

## Architecture

The application is composed of several key components that work together:

-   **Frontend (`chatbot_ui`):** A responsive web interface built with Next.js and Shadcn. It provides the user-facing chat experience, file upload capabilities, and conversation management.
-   **Backend (`chatbot_backend`):** A FastAPI server that acts as the central hub. It handles:
    -   API endpoints for user authentication, chat history, and file management.
    -   User, role, conversation, and message data persistence using SQLite.
    -   Real-time chat responses using Server-Sent Events (SSE).
    -   Communication with the Local LLM to generate responses and plan tool execution.
    -   Interaction with the MCP server to execute tools.
-   **MCP Server (`mcp_server`):** A dedicated Python server that exposes a suite of tools via the Model Context Protocol. These tools perform specific actions like file system operations, content analysis, and data classification.
-   **Local LLM (Ollama):** The application runs entirely offline by using local models like Mistral or Llama3.1 served via Ollama. The LLM is responsible for understanding user intent, orchestrating tool calls, and generating natural language responses.
-   **Vector Database (ChromaDB):** For efficient semantic search, document chunks are converted into embeddings and stored in a local ChromaDB instance, enabling powerful RAG capabilities.

## Features

-   **Offline AI Chat:** All chat interactions are processed locally using Ollama, ensuring data privacy and functionality without an internet connection.
-   **Multi-Model Support:** Easily switch between different local models (e.g., Mistral, Llama 3.1) or even cloud models like Gemini.
-   **User and Role Management:** A complete authentication system with predefined roles (Admin, HR, Sales, etc.) to manage access to files and tools.
-   **Document Interaction:**
    -   Upload and process various file types including PDF, DOCX, PPTX, and TXT.
    -   Files are chunked, embedded, and stored in a ChromaDB vector store.
-   **Retrieval-Augmented Generation (RAG):** The chat assistant can answer questions based on the content of uploaded documents by performing semantic searches.
-   **Tool Orchestration with MCP:** The LLM can plan and execute a sequence of actions using a rich set of tools provided by the MCP server, including:
    -   **File System:** `read_file`, `create_and_write_file`, `search_file_has_name_like`, `search_file_has_content_related`.
    -   **Content Analysis:** `summary_file_content`, `classify_file_based_on_content`.
    -   **Metadata Management:** `save_file_category`, `search_file_category`.
-   **Agentic Behavior & Chain of Thought:** The assistant can break down complex requests into a series of tool calls and explain its execution plan to the user.

## Getting Started

### Prerequisites

-   **Python 3.9+**
-   **Node.js 18+**
-   **Ollama:** Follow the installation guide at [https://ollama.com/download](https://ollama.com/download).

### 1. Install LLM Models

After installing Ollama, pull the required models from the command line. This project is configured to use `mistral` and `llama3.1`.

```bash
ollama pull mistral
ollama pull llama3.1
```

### 2. Backend Setup (`chatbot_backend`)

1.  **Navigate to the backend directory:**
    ```bash
    cd chatbot_backend
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Create a `.env` file in the `chatbot_backend` directory and add the following content. Adjust the values if your setup differs.
    ```env
    SERVER_HOST=0.0.0.0
    SERVER_PORT=8000
    FE_URL=http://localhost:3000
    FE_DEPLOY_URL=https://demo-chatllm.vercel.app
    OLLAMA_BASE_URL=http://127.0.0.1:11434
    ```

4.  **Run the backend server:**
    ```bash
    python app/main.py
    ```
    The server will start on `http://0.0.0.0:8000`. On first run, it will automatically create the necessary directories and seed the database with default users and roles.

### 3. Frontend Setup (`chatbot_ui`)

1.  **Navigate to the frontend directory:**
    ```bash
    cd chatbot_ui
    ```

2.  **Install Node.js dependencies:**
    ```bash
    npm install
    ```

3.  **Configure environment variables:**
    Create a `.env.local` file in the `chatbot_ui` directory with the following content, pointing to your running backend.
    ```env
    NEXT_PUBLIC_BASE_URL=http://localhost:8000
    ```

4.  **Run the frontend development server:**
    ```bash
    npm run dev
    ```
    The application will be accessible at `http://localhost:3000`.

## Usage

1.  Open your browser and navigate to `http://localhost:3000`.
2.  Log in using one of the default accounts. For full access to all files and tools, use:
    -   **Username:** `admin`
    -   **Password:** `123456`
3.  Click the `+` button in the input area to open the file upload modal. Upload documents you want the chat assistant to know about.
4.  Start a new conversation and ask questions. You can ask the assistant to perform tasks related to your documents, such as:
    -   `Summarize the contents of 'report.pdf'.`
    -   `What are the key points in the marketing plan document?`
    -   `Find all files related to the 2024 budget.`
    -   `Classify the 'project_proposal.docx' file and save its category.`

## Project Structure

```
.
├── chatbot_backend/
│   ├── app/                # Main FastAPI application source
│   │   ├── api/            # API endpoints (chat, login, files)
│   │   ├── file/           # File loading and pre-processing logic
│   │   ├── llm/            # MCP client for tool communication
│   │   ├── schema/         # Pydantic models for data structures
│   │   ├── search/         # ChromaDB vector store integration
│   │   └── service/        # Business logic for database operations
│   ├── mcp_server/         # MCP tool server
│   │   └── tools/          # Definition of all available tools
│   ├── .env                # Backend environment configuration
│   └── requirements.txt    # Python dependencies
│
└── chatbot_ui/
    ├── src/
    │   ├── app/            # Next.js pages and layouts
    │   ├── api/            # Frontend API clients
    │   ├── components/     # Reusable UI components
    │   ├── hooks/          # Custom React hooks
    │   └── types/          # TypeScript type definitions
    ├── .env.local          # Frontend environment configuration
    └── package.json        # Node.js dependencies
