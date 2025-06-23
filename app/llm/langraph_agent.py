# agent_with_memory.py

import asyncio
import uuid
from datetime import datetime
from typing import List, Dict, Any

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt.chat_agent_executor import AgentState

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession

from utils.file_utils import get_root_path

class AdvancedMemoryAgent:
    def __init__(self, model_name: str = "mistral", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.session_id = str(uuid.uuid4())
        self.checkpointer = MemorySaver()  # Persistent memory storage
        self.conversation_history = []
        
        # Initialize LLM với configuration tối ưu
        self.llm = ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=0.1,  # Giảm nhiễu để kết quả ổn định hơn
            num_predict=2048,  # Tăng độ dài response
            format="json",  # Đảm bảo output có thể parse
            verbose=False
        )
        
        # Optimized prompt template theo nguyên tắc ReAct
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self._create_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
    def _create_system_prompt(self) -> str:
        """Tạo system prompt tối ưu cho multi-step reasoning"""
        return """Bạn là một AI assistant thông minh chuyên xử lý các tác vụ phức tạp theo từng bước.

NGUYÊN TẮC HOẠT ĐỘNG:
1. Phân tích yêu cầu một cách chi tiết và có hệ thống
2. Xác định các bước cần thực hiện theo thứ tự logic
3. Sử dụng tools để thu thập thông tin cần thiết TRƯỚC khi thực hiện tác vụ chính
4. Lưu trữ ngữ cảnh quan trọng để sử dụng cho các bước tiếp theo
5. Trả lời ngắn gọn, rõ ràng với thông tin đầy đủ

CÁCH SỬ DỤNG TOOLS:
- Nếu thiếu thông tin, hãy lưu trữ ngữ cảnh bằng store_user_context trước
- Sử dụng get_user_context để lấy thông tin đã lưu cho các tool khác
- Luôn kiểm tra lịch sử tính toán trước khi thực hiện phép tính mới
- Kết hợp kết quả từ nhiều tool để đưa ra câu trả lời hoàn chỉnh

SESSION ID hiện tại: {session_id}

Hãy thực hiện từng bước một cách có hệ thống và báo cáo tiến trình cho người dùng biết.""".format(
            session_id=self.session_id
        )
    
    def _create_state_modifier(self):
        """Tạo state modifier để inject memory vào prompt"""
        def modify_state_messages(state: AgentState):
            # Lấy messages từ state
            messages = state.get("messages", [])
            
            # Thêm conversation history vào context
            if self.conversation_history:
                history_messages = []
                for entry in self.conversation_history[-6:]:  # Chỉ lấy 6 turn gần nhất
                    history_messages.append(HumanMessage(content=entry["human"]))
                    history_messages.append(AIMessage(content=entry["ai"]))
                
                # Combine với messages hiện tại
                messages = history_messages + messages
            
            return self.prompt_template.invoke({
                "chat_history": messages[:-1] if messages else [],
                "input": messages[-1].content if messages else "",
                "agent_scratchpad": []
            }).to_messages()
        
        return modify_state_messages

    async def get_mcp_tools(self):
        """Kết nối MCP server và lấy danh sách tools"""
        server_params = StdioServerParameters(
            command="python",
            args=[f"{get_root_path()}/mcp_server/database_mcp_server.py"],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Lấy danh sách tools từ MCP server
                available_tools = await session.list_tools()
                print(f"✅ Đã kết nối MCP server với {len(available_tools.tools)} tools", flush=True)
                
                # Convert MCP tools thành LangChain tools
                tools = []
                for tool in available_tools.tools:
                    async def tool_func(*args, tool_name=tool.name, **kwargs):
                        return await session.call_tool(tool_name, kwargs)
                    
                    # Tạo LangChain tool wrapper
                    from langchain.tools import StructuredTool
                    lc_tool = StructuredTool.from_function(
                        func=tool_func,
                        name=tool.name,
                        description=tool.description,
                    )
                    tools.append(lc_tool)
                
                return tools

    async def create_agent(self):
        """Tạo agent với memory và tools"""
        tools = await self.get_mcp_tools()
        
        # Tạo agent với memory support
        agent = create_react_agent(
            model=self.llm,
            tools=tools,
            state_modifier=self._create_state_modifier(),
            checkpointer=self.checkpointer  # Enable persistent memory
        )
        
        return agent
    
    async def run_conversation(self, user_input: str) -> str:
        """Chạy conversation với memory management"""
        print(f"🤖 Đang xử lý: {user_input}", flush=True)
        
        agent = await self.create_agent()
        
        # Configuration cho thread-based memory
        config = {
            "configurable": {
                "thread_id": self.session_id  # Sử dụng session_id làm thread_id
            }
        } 

        try:
            # Invoke agent với memory context
            response = await agent.ainvoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )
            print("The response is: ", response)
            # Extract response content
            ai_response = response["messages"][-1].content
            
            # Lưu vào conversation history để tối ưu memory
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "human": user_input,
                "ai": ai_response
            })
            
            # Giới hạn conversation history để tránh memory bloat
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-8:]  # Chỉ giữ 8 turn gần nhất
            
            print(f"✅ Hoàn thành xử lý", flush=True)
            return ai_response
            
        except Exception as e:
            error_msg = f"❌ Lỗi xử lý: {str(e)}"
            print(error_msg, flush=True)
            return error_msg

    def get_memory_stats(self) -> Dict[str, Any]:
        """Lấy thống kê memory sử dụng"""
        return {
            "session_id": self.session_id,
            "conversation_turns": len(self.conversation_history),
            "memory_usage": "Optimized with sliding window",
            "checkpointer_status": "Active" if self.checkpointer else "Inactive"
        }

# Demo usage
async def main():
    """Demo chính với các test case phức tạp"""
    agent = AdvancedMemoryAgent()
    
    print("🚀 Khởi động Advanced Memory Agent")
    print(f"📊 Memory stats: {agent.get_memory_stats()}")
    print("-" * 50)
    
    # Test case 1: Multi-step calculation với context
    print("\n🧮 Test 1: Multi-step calculation")
    response1 = await agent.run_conversation(
        "Tôi cần tính toán lợi nhuận. Trước tiên hãy lưu doanh thu là 1000000 và chi phí là 750000. "
        "Sau đó tính lợi nhuận = doanh thu - chi phí."
    )
    print(f"Agent: {response1}")
    
    # Test case 2: Sử dụng context đã lưu
    print("\n💡 Test 2: Sử dụng context đã lưu")
    response2 = await agent.run_conversation(
        "Bây giờ hãy tính tỷ lệ lợi nhuận = (lợi nhuận / doanh thu) x 100%. "
        "Sử dụng các số liệu đã lưu trước đó."
    )
    print(f"Agent: {response2}")
    
    # Test case 3: History và memory
    print("\n📈 Test 3: Kiểm tra lịch sử")
    response3 = await agent.run_conversation(
        "Cho tôi xem lịch sử các phép tính đã thực hiện và tổng kết những gì đã làm."
    )
    print(f"Agent: {response3}")
    
    # Test case 4: Complex reasoning
    print("\n🎯 Test 4: Complex reasoning")
    response4 = await agent.run_conversation(
        "Dựa trên dữ liệu đã có, nếu tôi muốn tăng lợi nhuận lên 300000, "
        "tôi cần tăng doanh thu bao nhiêu % (giả sử chi phí không đổi)?"
    )
    print(f"Agent: {response4}")
    
    print(f"\n📊 Final memory stats: {agent.get_memory_stats()}")

if __name__ == "__main__":
    asyncio.run(main())
