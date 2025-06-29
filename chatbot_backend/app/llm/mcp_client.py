# mcp_client.py
from pathlib import Path
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp.client.stdio import StdioServerParameters
from utils.file_utils import get_root_path
from langchain_mcp_adapters.tools import load_mcp_tools

from utils.environment import MCP_SERVER_URL

SERVER_PARAMS = StdioServerParameters(
    command="python", 
    args=[f"{get_root_path()}/{MCP_SERVER_URL}"]
) 

async def list_available_tools(): 
    try:
        async with stdio_client(SERVER_PARAMS) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize() 
                tools = await session.list_tools()
                return tools.tools 
    except Exception as e:
        print(f"Error listing tools: {str(e)}") 
        raise

async def list_mcp_tools(): 
    try:
        async with stdio_client(SERVER_PARAMS) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize() 
                tools = await load_mcp_tools(session)
                return tools
    except Exception as e:
        print(f"Error listing tools: {str(e)}") 
        raise
 
async def call_tool(tool_name, params):
    try:
        async with stdio_client(SERVER_PARAMS) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize() 
                return await session.call_tool(tool_name, params) 
    except Exception as e:
        print(f"Error calling tool: {str(e)}") 
        raise
