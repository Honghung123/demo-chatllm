# main.py  
from shared_mcp import mcp
from tools.common.file import summary_file_content
from tools.common.filesystem import read_file, create_and_write_file, search_file_has_content_ralated, search_file_has_name_like
from tools.common.metadata import classify_file_based_on_content, search_file_category
# from tools.marketing.tool import analyze_sales, suggest_campaign, predict_future 

if __name__ == "__main__":  
    mcp.run(transport="stdio")  # run MCP server using stdio transport