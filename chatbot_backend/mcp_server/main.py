# main.py  
from shared_mcp import mcp;
from tools.common.filesystem import read_file, write_file, create_file, search_file_has_content_ralated
from tools.common.metadata import classify_file_based_on_content, search_file_category
from tools.marketing.tool import analyze_sales, suggest_campaign, predict_future 

if __name__ == "__main__":  
    mcp.run(transport="stdio")  # run MCP server using stdio transport