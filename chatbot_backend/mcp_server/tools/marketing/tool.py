from typing import Optional

from shared_mcp import mcp
from tools.marketing.prompt import (
    system_prompt_analyze_sales,
    system_prompt_suggest_campaign,
    system_prompt_predict_future,
)
from ollama import Client

client = Client(
    host="http://192.168.128.1:11434"  # or another host if you're running Ollama elsewhere
)


@mcp.tool(description="Analyze marketing data, sales and give insights")
def analyze_sales(file_content: str) -> str:
    """Analyze marketing data, sales and give insights"""
    messages = [
        {"role": "system", "content": system_prompt_analyze_sales()},
        {"role": "user", "content": file_content},
    ]

    response = client.chat(model="llama3.1", messages=messages, stream=False)

    return (
        response["message"]["content"]
        if "message" in response
        else "No response from model"
    )


@mcp.tool(
    description="Suggest marketing campaigns based on user query and optional sales/customer data"
)
def suggest_campaign(query: str, file_content: Optional[str] = None) -> str:
    """Suggest effective marketing campaigns based primarily on the query, with optional data"""
    # Build dynamic user message
    user_message = query
    if file_content:
        user_message += "\n\nAdditional data:\n" + file_content

    messages = [
        {"role": "system", "content": system_prompt_suggest_campaign()},
        {"role": "user", "content": user_message},
    ]

    response = client.chat(model="llama3.1", messages=messages, stream=False)

    return (
        response["message"]["content"]
        if "message" in response
        else "No response from model"
    )


@mcp.tool(
    description="Predict future sales trends from historical data or from a user quert"
)
def predict_future(query: str, file_content: Optional[str] = None) -> str:
    """Predict future trends and performance from marketing and sales data"""
    user_message = query
    if file_content:
        user_message += "\n\nAdditional data:\n" + file_content

    messages = [
        {"role": "system", "content": system_prompt_predict_future()},
        {"role": "user", "content": user_message},
    ]
    response = client.chat(model="llama3.1", messages=messages, stream=False)
    return (
        response["message"]["content"]
        if "message" in response
        else "No response from model"
    )
