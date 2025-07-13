from typing import Optional

from ollama_config import OLLAMA_HOST, OLLAMA_MODEL
from shared_mcp import mcp
from tools.hr.prompts import (
    system_prompt_filter_cv,
    system_prompt_expiring_contracts
)
from ollama import Client

client = Client(
    host=OLLAMA_HOST
)


@mcp.tool(
    description="Filter candidate CVs based on specific conditions like skills, experience, or position",
    annotations={"title": "Filter CVs by condition"}
)
def filter_candidate_cv(condition: str, file_content: str) -> str:
    """Filter candidate CVs by a given condition (e.g., skill, job title, experience)"""
    messages = [
        {"role": "system", "content": system_prompt_filter_cv()},
        {"role": "user", "content": f"Condition: {condition}\n\nCVs:\n{file_content}"},
    ]

    response = client.chat(model=OLLAMA_MODEL, messages=messages, stream=False)
    return (
        response["message"]["content"]
        if "message" in response
        else "No response from model"
    )



@mcp.tool(
    description="Find employees with contracts that are about to expire soon (e.g., within 30 days)",
    annotations={"title": "Find soon-to-expire contracts"}
)
def find_expiring_contracts(file_content: str) -> str:
    """Identify contracts expiring soon (e.g., in the next 30 days) from HR records"""
    messages = [
        {"role": "system", "content": system_prompt_expiring_contracts()},
        {"role": "user", "content": file_content},
    ]

    response = client.chat(model=OLLAMA_MODEL, messages=messages, stream=False)
    return (
        response["message"]["content"]
        if "message" in response
        else "No response from model"
    )