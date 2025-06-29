# echo.py
from shared_mcp import mcp; 


@mcp.tool(description="Tool to echo a message to the console")
def echo(message: str) -> None:
    print("* * * * *  echo tool called * * * * *")
    print(message)
    return "Echo tool called"