# run_demo.py
import asyncio 
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm.langraph_agent import AdvancedMemoryAgent

async def interactive_demo():
    """Demo tương tác với user"""
    agent = AdvancedMemoryAgent()
    
    print("=" * 60)
    print("🚀 ADVANCED AGENTIC AI DEMO")
    print("✨ Tối ưu Prompt + Memory Management")
    print("=" * 60)
    print(f"📊 Session ID: {agent.session_id}")
    print("💡 Nhập 'quit' để thoát, 'stats' để xem memory stats")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\n👤 Bạn: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Tạm biệt!")
                break
            elif user_input.lower() == 'stats':
                stats = agent.get_memory_stats()
                print(f"📊 Memory Stats: {stats}")
                continue
            elif not user_input:
                continue
            
            # Process với agent
            response = await agent.run_conversation(user_input)
            print(f"\n🤖 Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Tạm biệt!")
            break
        except Exception as e:
            print(f"❌ Lỗi: {str(e)}")

async def automated_demo():
    """Demo tự động với test cases phức tạp"""
    agent = AdvancedMemoryAgent()
    
    print("🎯 AUTOMATED DEMO - Complex Multi-Step Tasks")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Lưu trữ thông tin dự án",
            "query": "Tôi có một dự án với budget 5000000, chi phí đã dùng 3200000, thời gian còn lại 30 ngày. Hãy lưu thông tin này và tính chi phí còn lại."
        },
        {
            "name": "Phân tích hiệu suất dự án", 
            "query": "Dựa trên thông tin dự án đã lưu, tính tỷ lệ % ngân sách đã sử dụng và đánh giá xem có vượt quá kế hoạch không."
        },
        {
            "name": "Dự báo và khuyến nghị",
            "query": "Nếu tôi tiếp tục chi tiêu với tốc độ hiện tại, liệu có đủ ngân sách không? Đưa ra khuyến nghị cụ thể."
        },
        {
            "name": "Xem lại toàn bộ quy trình",
            "query": "Tổng hợp lại toàn bộ phân tích dự án và lịch sử tính toán đã thực hiện."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*20} TEST {i}: {test_case['name']} {'='*20}")
        print(f"📝 Query: {test_case['query']}")
        print("-" * 60)
        
        response = await agent.run_conversation(test_case['query'])
        print(f"🤖 Response: {response}")
        
        # Ngừng giữa các test để user có thể đọc
        if i < len(test_cases):
            input("\n⏸️  Nhấn Enter để tiếp tục test tiếp theo...")
    
    print(f"\n📊 Final Stats: {agent.get_memory_stats()}")

if __name__ == "__main__":
    print("Chọn chế độ demo:")
    print("1. Interactive Demo (tương tác)")
    print("2. Automated Demo (tự động)")
    
    choice = input("Nhập lựa chọn (1 hoặc 2): ").strip()
    
    if choice == "1":
        asyncio.run(interactive_demo())
    elif choice == "2":
        asyncio.run(automated_demo())
    else:
        print("Lựa chọn không hợp lệ!")
