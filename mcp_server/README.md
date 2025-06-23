# MCP Server

This is a FastAPI server that provides multiple Model Context Protocol (MCP) endpoints for different functionalities.

## Running the Server

```bash
uvicorn main:app --reload
```

## Available Endpoints

The main API documentation is available at: http://127.0.0.1:8000/

### Echo Service
- **Endpoint:** `/echo`
- **Documentation:** http://127.0.0.1:8000/echo/docs
- **Description:** A simple echo service that returns the message you send.

### Calculator Service
- **Endpoint:** `/add`
- **Documentation:** http://127.0.0.1:8000/add/docs
- **Description:** Provides mathematical operations like addition.

### File System Services

#### Read File
- **Endpoint:** `/read_file`
- **Documentation:** http://127.0.0.1:8000/read_file/docs
- **Description:** Read the contents of a file.

#### Write File
- **Endpoint:** `/write_file`
- **Documentation:** http://127.0.0.1:8000/write_file/docs
- **Description:** Write content to a file.

#### List Files
- **Endpoint:** `/list_files`
- **Documentation:** http://127.0.0.1:8000/list_files/docs
- **Description:** List files in a directory.

#### Create File
- **Endpoint:** `/create_file`
- **Documentation:** http://127.0.0.1:8000/create_file/docs
- **Description:** Create a new file with content.

## Important Note

When using FastAPI's `app.mount()` function, each mounted application has its own separate Swagger UI documentation. 
This means that the main app's documentation at http://127.0.0.1:8000/docs will not show the endpoints from the mounted applications.

To access the documentation for each mounted application, you need to go to the specific path for that application followed by `/docs`.
For example, to see the documentation for the Echo service, go to http://127.0.0.1:8000/echo/docs.


