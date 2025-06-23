from langchain_ollama.chat_models import ChatOllama
from langchain_mcp_adapters.client import MultiServerMCPClient 
from langchain_core.prompts import ChatPromptTemplate
# from langchain.agents import AgentExecutor, create_react_agent
from langgraph.prebuilt import create_react_agent

from app.llm import mcp_client
from utils.environment import LANGSMITH_API_KEY, MCP_SERVER_URL, OLLAMA_MODEL, OLLAMA_BASE_URL
from utils.file_utils import get_root_path

from langchain import hub
from langchain_core.tools import render_text_description

# Initialize LLM
llm = ChatOllama(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0,
    # format="json"  # Format response to JSON
)
 
async def get_tools(): 
    client = MultiServerMCPClient(
        {
            "mcp_server": {
                "command": "python",
                "args": [f"{get_root_path()}/{MCP_SERVER_URL}"],
                "transport": "stdio",
            },
            # Another MCP servers
        }
    ) 
    return await client.get_tools()

# 5. Create and run agent
async def run_agent(query: str): 
    tools = await get_tools()  
    # tools = await mcp_client.list_mcp_tools()
    print(tools)
    # tools = await mcp_client.list_available_tools()
    # Create agent
    # prompt_template = ChatPromptTemplate.from_messages([
    # ("system", f"You are a helpful assistant. Use tools when necessary. Answer briefly. Here is the tools: {[{tool.name: tool.description} for tool in tools]}")
    # ])   
    prompt = hub.pull(owner_repo_commit="hwchase17/react-json", api_key=LANGSMITH_API_KEY)
    prompt = prompt.partial(
        tools=render_text_description(tools),
        tool_names=", ".join([t.name for t in tools]),
    )
 
    agent = create_react_agent(
        model=llm,
        tools=tools,
        # prompt=prompt
    ) 
    
    print("Executing query...")  
    agent_response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": query}]})
    # result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})  
    # agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True, verbose=False)
    # agent_response = await agent_executor.ainvoke({"input": query})
    return agent_response 

