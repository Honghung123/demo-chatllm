# main.py  
from shared_mcp import mcp;
from tools import echo, calculator, filesystem

if __name__ == "__main__":  
    mcp.run(transport="stdio")  # run MCP server using stdio transport