# Unit test cho chat_engine 
import os
import sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
from app.llm.chat_engine import chat_llm
from app.llm import prompt_templates as pt

class TestChatEngine(unittest.TestCase):
    def test_offline_answer_generation(self):
        prompt = "Giới thiệu ngắn gọn về Mistral LLM." 
        answer = chat_llm(prompt, streaming=True, max_tokens=50) 
        self.assertIsInstance(answer, str)
        self.assertTrue(len(answer.strip()) > 0, "Câu trả lời bị rỗng!")
        self.assertFalse(answer.startswith("❌"), f"Lỗi khi sinh câu trả lời: {answer}")
        print()

    def test_with_history(self):
        history = [
            {"role": "user", "content": "Bạn tên là gì?"},
            {"role": "assistant", "content": "Tôi là AI trợ lý."},
        ]
        prompt = "Bạn có thể giúp tôi làm gì?"
        answer = chat_llm(prompt, history=history, streaming=True, max_tokens=50) 
        self.assertIsInstance(answer, str)
        self.assertTrue(len(answer.strip()) > 0)
        self.assertFalse(answer.startswith("❌"))
        print()

    def test_classify_prompt(self):
        prompt = pt.CLASSIFY_PROMPT.format(
            content="Đây là báo cáo tài chính năm 2023 của công ty ABC.",
            labels="Báo cáo, Hợp đồng, Thư từ"
        )
        answer = chat_llm(prompt, streaming=True, max_tokens=50) 
        self.assertIsInstance(answer, str)
        self.assertTrue(len(answer.strip()) > 0)
        self.assertFalse(answer.startswith("❌"))
        print()

    def test_search_prompt(self):
        prompt = pt.SEARCH_PROMPT.format(
            query="Kế hoạch marketing 2024",
            file_summaries="plan2024.pdf: Kế hoạch tổng thể năm 2024.\nmarketing2024.pptx: Slide chiến lược marketing."
        )
        answer = chat_llm(prompt, streaming=True, max_tokens=50)
        self.assertIsInstance(answer, str)
        self.assertTrue(len(answer.strip()) > 0)
        self.assertFalse(answer.startswith("❌"))
        print()

    def test_rlhf_confirm_prompt(self):
        prompt = pt.RLHF_CONFIRM_PROMPT.format(
            filename="marketing2024.pptx",
            label="Nhóm B",
            content="Slide trình bày chiến lược marketing năm 2024."
        )
        answer = chat_llm(prompt, streaming=True, max_tokens=50)
        self.assertIsInstance(answer, str)
        self.assertTrue(len(answer.strip()) > 0)
        self.assertFalse(answer.startswith("❌"))
        print()

    def test_summarize_file_prompt(self):
        prompt = pt.SUMMARIZE_FILE_PROMPT.format(
            content="Đây là báo cáo tài chính năm 2023 của công ty ABC. Doanh thu tăng trưởng 20%."
        )
        answer = chat_llm(prompt, streaming=True, max_tokens=50)
        self.assertIsInstance(answer, str)
        self.assertTrue(len(answer.strip()) > 0)
        self.assertFalse(answer.startswith("❌"))
        print()

    def test_suggest_labels_prompt(self):
        prompt = pt.SUGGEST_LABELS_PROMPT.format(
            file_summaries="file1.pdf: Báo cáo tài chính.\nfile2.docx: Hợp đồng lao động."
        )
        answer = chat_llm(prompt, streaming=True, max_tokens=50)
        self.assertIsInstance(answer, str)
        self.assertTrue(len(answer.strip()) > 0)
        self.assertFalse(answer.startswith("❌"))
        print()

if __name__ == "__main__":
    unittest.main() 