# main.py  
from shared_mcp import mcp;
from tools.common import filesystem
from tools.marketing.tool import analyze_sales, suggest_campaign, predict_future 

if __name__ == "__main__":  
    mcp.run(transport="stdio")  # run MCP server using stdio transport