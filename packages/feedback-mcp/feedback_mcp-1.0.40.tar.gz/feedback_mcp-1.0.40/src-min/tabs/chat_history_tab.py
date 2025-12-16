"""
对话记录标签页 - 展示所有对话内容
"""
import sys
import os
import json
from typing import List, Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame, QLabel, QSizePolicy, QPushButton
)
from PySide6.QtCore import Qt, QFile, QTextStream

try:
    from .base_tab import BaseTab
except ImportError:
    from base_tab import BaseTab

try:
    from ..components.markdown_display import MarkdownDisplayWidget
except ImportError:
    try:
        from components.markdown_display import MarkdownDisplayWidget
    except ImportError:
        from PySide6.QtWidgets import QTextEdit
        MarkdownDisplayWidget = QTextEdit


class ChatHistoryTab(BaseTab):
    """对话记录标签页 - 展示所有对话内容"""

    def __init__(self, project_path: Optional[str] = None, session_id: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.session_id = session_id

        # UI组件
        self.scroll_area = None
        self.messages_container = None
        self.messages_layout = None
        self.load_more_button = None

        # 历史记录管理
        self.all_history = []
        self.displayed_count = 5
        self._loaded = False  # 延迟加载标志

        self.create_ui()

    def create_ui(self):
        """创建对话记录Tab的UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 容器
        self.messages_container = QWidget()
        self.messages_container.setObjectName("messagesContainer")
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(15, 15, 15, 15)
        self.messages_layout.setSpacing(15)
        self.messages_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.messages_container)
        layout.addWidget(self.scroll_area)

        # 加载样式表
        self._load_stylesheet()

    def _load_stylesheet(self):
        """加载QSS样式表"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            qss_path = os.path.join(current_dir, "chat_history_style.qss")
            qss_file = QFile(qss_path)
            if qss_file.open(QFile.ReadOnly | QFile.Text):
                stream = QTextStream(qss_file)
                self.setStyleSheet(stream.readAll())
                qss_file.close()
            else:
                print(f"无法加载样式表: {qss_path}", file=sys.stderr)
        except Exception as e:
            print(f"加载样式表出错: {e}", file=sys.stderr)

    def load_history(self):
        """加载并显示对话历史记录"""
        # 清空现有消息
        self._clear_messages()

        # 读取历史记录
        self.all_history = self._load_history_from_file()

        if not self.all_history:
            # 如果没有历史记录,显示提示
            self._show_empty_message()
            return

        # 显示最后5条记录
        self._display_records()

    def _display_records(self):
        """显示记录(从最新的开始显示指定数量)"""
        # 清空所有现有消息
        self._clear_messages()
        self.load_more_button = None

        total = len(self.all_history)
        # 计算要显示的记录范围
        start_idx = max(0, total - self.displayed_count)
        records_to_show = self.all_history[start_idx:]

        # 如果还有更多记录,显示"加载更多"按钮
        if start_idx > 0:
            self.load_more_button = QPushButton("点击查看更多")
            self.load_more_button.setObjectName("loadMoreButton")
            self.load_more_button.clicked.connect(self._load_more)
            self.load_more_button.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
            """)
            self.messages_layout.insertWidget(0, self.load_more_button)

        # 显示记录
        for record in records_to_show:
            if record.get('role') == 'agent':
                self._add_agent_message(record)
            elif 'messages' in record:
                self._add_dialogue_messages(record)

    def _load_more(self):
        """加载更多记录"""
        self.displayed_count += 5
        self._display_records()

    def _clear_messages(self):
        """清空所有消息"""
        while self.messages_layout.count():
            child = self.messages_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _show_empty_message(self):
        """显示无历史记录提示"""
        empty_label = QLabel("暂无对话记录")
        empty_label.setObjectName("emptyStateLabel")
        empty_label.setAlignment(Qt.AlignCenter)
        self.messages_layout.addWidget(empty_label)

    def _setup_content_display(self, content: str) -> MarkdownDisplayWidget:
        """创建并配置内容显示组件（使用MarkdownDisplayWidget）"""
        content_display = MarkdownDisplayWidget()
        content_display.setMarkdownText(content)
        content_display.setStyleSheet('''
            QTextEdit {
                background-color: transparent;
                border: none;
                padding: 0px;
                color: #e0e0e0;
            }
        ''')
        content_display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # 计算高度
        content_display.document().setTextWidth(400)
        doc_height = content_display.document().size().height()
        content_display.setMinimumHeight(int(doc_height) + 20)
        return content_display

    def _create_avatar(self, text: str) -> QLabel:
        """创建头像标签"""
        label = QLabel(text)
        label.setObjectName("avatarLabel")
        label.setFixedSize(32, 32)
        label.setAlignment(Qt.AlignCenter)
        return label

    def _add_agent_message(self, record: Dict):
        """添加Agent消息"""
        description = record.get('description', '')
        content = record.get('content', '')

        # 主行布局
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 5, 0, 5)
        row_layout.setSpacing(10)

        # 1. 头像
        avatar = self._create_avatar("⚙️")
        row_layout.addWidget(avatar, alignment=Qt.AlignTop)

        # 2. 消息气泡容器
        bubble_container = QWidget()
        bubble_layout = QVBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.setSpacing(2)

        # 角色标签
        role_text = "Agent"
        if description:
            role_text += f" • {description}"
        role_label = QLabel(role_text)
        role_label.setObjectName("roleLabel")
        bubble_layout.addWidget(role_label)

        # 气泡
        bubble = QFrame()
        bubble.setObjectName("agentBubble")
        bubble_content_layout = QVBoxLayout(bubble)
        bubble_content_layout.setContentsMargins(12, 8, 12, 8)
        
        if content:
            content_display = self._setup_content_display(content)
            bubble_content_layout.addWidget(content_display)
        
        bubble_layout.addWidget(bubble)
        
        row_layout.addWidget(bubble_container, stretch=1)
        
        # 3. 右侧占位
        row_layout.addStretch(0)

        self.messages_layout.addWidget(row_widget)

    def _add_dialogue_messages(self, record: Dict):
        """添加对话消息(包含user和assistant)"""
        messages = record.get('messages', [])

        for message in messages:
            role = message.get('role', '')
            content = message.get('content', '')

            if role == 'user':
                self._add_user_message(content)
            elif role == 'assistant':
                self._add_assistant_message(content)

    def _add_user_message(self, content: str):
        """添加用户消息"""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 5, 0, 5)
        row_layout.setSpacing(10)

        # 1. 左侧占位
        row_layout.addStretch(1)

        # 2. 消息气泡
        bubble = QFrame()
        bubble.setObjectName("userBubble")
        bubble_content_layout = QVBoxLayout(bubble)
        bubble_content_layout.setContentsMargins(12, 8, 12, 8)

        if content:
            content_display = self._setup_content_display(content)
            bubble_content_layout.addWidget(content_display)

        row_layout.addWidget(bubble, stretch=0) # 不拉伸，由内容决定

        # 3. 头像
        avatar = self._create_avatar("👤")
        row_layout.addWidget(avatar, alignment=Qt.AlignTop)

        self.messages_layout.addWidget(row_widget)

    def _add_assistant_message(self, content: str):
        """添加AI消息"""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 5, 0, 5)
        row_layout.setSpacing(10)

        # 1. 头像
        avatar = self._create_avatar("🤖")
        row_layout.addWidget(avatar, alignment=Qt.AlignTop)

        # 2. 消息气泡容器
        bubble_container = QWidget()
        bubble_layout = QVBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.setSpacing(2)

        # 角色标签
        role_label = QLabel("AI Assistant")
        role_label.setObjectName("roleLabel")
        bubble_layout.addWidget(role_label)

        # 气泡
        bubble = QFrame()
        bubble.setObjectName("aiBubble")
        bubble_content_layout = QVBoxLayout(bubble)
        bubble_content_layout.setContentsMargins(12, 8, 12, 8)

        if content:
            content_display = self._setup_content_display(content)
            bubble_content_layout.addWidget(content_display)
        
        bubble_layout.addWidget(bubble)
        
        row_layout.addWidget(bubble_container, stretch=1)

        # 3. 右侧占位
        row_layout.addStretch(0)

        self.messages_layout.addWidget(row_widget)

    def _load_history_from_file(self) -> List[Dict]:
        """从文件加载历史记录"""
        try:
            # 如果没有session_id,返回空列表
            if not self.session_id:
                return []

            # 构建历史文件路径
            if self.project_path:
                history_file = os.path.join(self.project_path, '.workspace', 'chat_history', f'{self.session_id}.json')
            else:
                script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                history_file = os.path.join(script_dir, '.workspace', 'chat_history', f'{self.session_id}.json')

            if not os.path.exists(history_file):
                return []

            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # 新格式:{'dialogues': [...]}
                if isinstance(data, dict) and 'dialogues' in data:
                    return data.get('dialogues', [])

                # ���格式数组
                if isinstance(data, list):
                    # 过滤掉stop_hook_status类型的记录
                    return [record for record in data if isinstance(record, dict) and record.get('type') != 'stop_hook_status']

                return []
        except Exception as e:
            print(f"加载历史记录失败: {e}", file=sys.stderr)
            return []

    def refresh_history(self):
        """刷新历史记录"""
        self.load_history()
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        """滚动到底部"""
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def showEvent(self, event):
        """Tab显示时加载历史记录并滚动到底部"""
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self.load_history()
        self._scroll_to_bottom()
