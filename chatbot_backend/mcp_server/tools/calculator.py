# calculator.py
from shared_mcp import mcp;

# Add an addition tool
@mcp.tool(description="Add two numbers")
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool(description="Subtract two numbers")
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b

@mcp.tool(description="Multiply two numbers")
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool(description="Divide two numbers")
def divide(a: int, b: int) -> int:
    """Divide two numbers"""
    return a / b




