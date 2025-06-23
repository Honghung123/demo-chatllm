# Chat bot UI with PyQt

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import sys
import asyncio
from app.llm.chat_engine import chat_llm, process_request_message

USER_AVATAR = "🧑"
BOT_AVATAR = "🤖"
USER_COLOR = "#1976D2"
BOT_COLOR = "#E3F2FD"
USER_TEXT_COLOR = "#fff"
BOT_TEXT_COLOR = "#23272F"
BG_COLOR = "#F4F4F4"

class MessageBubble(QFrame):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {USER_COLOR if is_user else BOT_COLOR}; border-radius: 12px;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("Segoe UI", 11))
        self.label.setStyleSheet(f"color: {USER_TEXT_COLOR if is_user else BOT_TEXT_COLOR};")
        layout.addWidget(self.label)

    def setText(self, text):
        self.label.setText(text)

class ChatMessage(QWidget):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent) 
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        avatar = QLabel(USER_AVATAR if is_user else BOT_AVATAR)
        avatar.setFont(QFont("Segoe UI Emoji", 22))
        if is_user:
            layout.addStretch()
            self.bubble = MessageBubble(text, is_user=True)
            layout.addWidget(self.bubble)
            layout.addWidget(avatar)
        else:
            layout.addWidget(avatar)
            self.bubble = MessageBubble(text, is_user=False)
            layout.addWidget(self.bubble)
            layout.addStretch()

    def setText(self, text):
        self.bubble.setText(text)

class ChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {BG_COLOR};")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QLabel("Chat offline")
        header.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header.setStyleSheet(f"background: #E0E0E0; color: {USER_COLOR}; padding: 16px;")
        main_layout.addWidget(header)

        # Chat area with scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"background: {BG_COLOR}; border: none;")
        self.chat_content = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.addStretch()
        self.scroll_area.setWidget(self.chat_content)
        main_layout.addWidget(self.scroll_area, 1)

        # Bottom input area
        bottom = QFrame()
        bottom.setStyleSheet(f"background: {BG_COLOR};")
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(16, 8, 16, 8)
        self.input = QLineEdit()
        self.input.setFont(QFont("Segoe UI", 11))
        self.input.setText("Read and print the file test.txt")
        self.input.setStyleSheet("background: #2C313A; color: #fff; border-radius: 8px; padding: 12px;")
        bottom_layout.addWidget(self.input, 1)
        self.send_btn = QPushButton("➤")
        self.send_btn.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.send_btn.setStyleSheet(f"background: {USER_COLOR}; color: #fff; border-radius: 8px; padding: 8px 16px;")
        bottom_layout.addWidget(self.send_btn)
        main_layout.addWidget(bottom)

        # Lịch sử chat
        self.history = []

        # Sự kiện gửi
        self.send_btn.clicked.connect(self.on_send)
        self.input.returnPressed.connect(self.on_send)

    def add_message(self, text, is_user=True):
        msg = ChatMessage(text, is_user)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg)
        # Auto-scroll to bottom
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        return msg

    def on_send(self):
        user_text = self.input.text().strip()
        if not user_text:
            return
        self.input.clear() 
        self.add_message(user_text, is_user=True)
        self.history.append({"role": "user", "content": user_text})
        # Tạo bot message rỗng để update dần
        self.bot_msg_widget = ChatMessage("", is_user=False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, self.bot_msg_widget)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum()) 
        self.worker = BotResponseWorker(user_text, self.history[:-1])
        self.worker.chunk_received.connect(self.on_bot_chunk)
        self.worker.finished.connect(self.on_bot_done)
        self.worker.start()
        self.bot_response = ""

    def on_bot_chunk(self, chunk):
        self.bot_response += chunk
        # Cập nhật nội dung bot message
        if hasattr(self, 'bot_msg_widget') and self.bot_msg_widget:
            self.bot_msg_widget.setText(self.bot_response)
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

    def on_bot_done(self, full_response):
        if hasattr(self, 'bot_msg_widget') and self.bot_msg_widget:
            self.bot_msg_widget.setText(full_response)
        self.history.append({"role": "assistant", "content": full_response})
        self.input.setDisabled(False)
        self.send_btn.setDisabled(False)
        self.input.setFocus()

# QThread để lấy response streaming
class BotResponseWorker(QThread):
    chunk_received = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, prompt, history):
        super().__init__()
        self.prompt = prompt
        self.history = history

    def run(self):
        self.full = ""
        def on_chunk(chunk):
            self.full += chunk
            self.chunk_received.emit(chunk)
        try: 
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop) 
            loop.run_until_complete(process_request_message(self.prompt, history=self.history, on_chunk=on_chunk)) 
            self.finished.emit(self.full)
        except Exception as e:
            self.chunk_received.emit(f"\n❌ Lỗi: {str(e)}")
            self.finished.emit("")
        finally:
            loop.close()

def start_desktop_ui():
    app = QApplication(sys.argv)
    win = ChatWidget()
    win.setWindowTitle("Chat offline")
    win.resize(400, 600)
    win.show()
    sys.exit(app.exec())
