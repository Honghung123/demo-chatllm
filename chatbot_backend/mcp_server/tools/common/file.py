from shared_mcp import mcp 

from ollama_config import ask_llm

@mcp.tool(
    description="Make sure the file content was read from a file before using this tool. Summarize the content of a file into a short summary.",
    annotations={
        "title": "Summarizing the content of file",
    }
)
def summary_file_content(content: str) -> str:
    messages = [
        {"role": "system", "content": "You are a file summary expert. Your task is to analyze the content of the speicific file content and summarize it into a short summary. Only return the summary without any additional text."},
        {"role": "user", "content": content},
    ]
    response = ask_llm(messages) 
    # return (
    #     response["message"]["content"]
    #     if "message" in response
    #     else ""
    # )
    return response.text