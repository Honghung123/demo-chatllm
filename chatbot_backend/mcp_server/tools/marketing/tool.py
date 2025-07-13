from typing import Optional

from ollama_config import OLLAMA_HOST, OLLAMA_MODEL
from shared_mcp import mcp
from tools.marketing.prompt import (
    system_prompt_analyze_sales,
    system_prompt_suggest_campaign,
    system_prompt_predict_future,
)
from ollama import Client

client = Client(
    host=OLLAMA_HOST
)

@mcp.tool(
    description="Analyze marketing data, sales and give insights",  
    annotations={
        "title": "Analyze marketing data, sales and give insights"
    }
)
def analyze_sales(file_content: str) -> str:
    """Analyze marketing data, sales and give insights"""
    messages = [
        {"role": "system", "content": system_prompt_analyze_sales()},
        {"role": "user", "content": file_content},
    ]

    response = client.chat(model=OLLAMA_MODEL, messages=messages, stream=False)

    return (
        response["message"]["content"]
        if "message" in response
        else "No response from model"
    )


@mcp.tool(
    description="Suggest marketing campaigns based on user query (user input) and optional sales/customer data", 
    annotations={
        "title": "Suggest marketing campaigns based on user query and optional sales/customer data"
    }
)
def suggest_campaign(query: Optional[str] = None, file_content: Optional[str] = None) -> str:
    query = query or "sales"
    """Suggest effective marketing campaigns based primarily on the query, with optional data"""
    # Build dynamic user message
    user_message = query
    if file_content:
        user_message += "\n\nAdditional data:\n" + file_content

    messages = [
        {"role": "system", "content": system_prompt_suggest_campaign()},
        {"role": "user", "content": user_message},
    ]

    response = client.chat(model=OLLAMA_MODEL, messages=messages, stream=False)

    return (
        response["message"]["content"]
        if "message" in response
        else "No response from model"
    )


@mcp.tool(
    description="Predict future sales trends from historical data or from a user query",
    annotations={
        "title": "Predict future sales trends from historical data or from a user query"
    }
)
def predict_future(query: Optional[str] = None, file_content: Optional[str] = None) -> str:
    """Predict future trends and performance from marketing and sales data"""
    query = query or "sales"
    user_message = query
    if file_content:
        user_message += "\n\nAdditional data:\n" + file_content

    messages = [
        {"role": "system", "content": system_prompt_predict_future()},
        {"role": "user", "content": user_message},
    ]
    response = client.chat(model=OLLAMA_MODEL, messages=messages, stream=False)
    return (
        response["message"]["content"]
        if "message" in response
        else "No response from model"
    )
