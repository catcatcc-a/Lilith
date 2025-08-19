# mock_services.py
class CustomLLM:
    def __init__(self, config_path):
        pass

    def generate(self, prompt):
        return "这是模拟的AI回复：" + prompt


class ChatService:
    def __init__(self, llm):
        self.llm = llm

    def login(self, username, password):
        # 模拟登录成功
        return True, "user_123"

    def chat(self, user_id, message):
        # 模拟AI回复
        return f"模拟回复：{message}"

    def get_chat_history(self, user_id):
        # 模拟历史记录
        return [
            {"role": "user", "content": "你好！"},
            {"role": "assistant", "content": "你好，我是莉莉丝，有什么可以帮你？"}
        ]


class Book:
    def __init__(self, file_path, llm):
        self.content = "模拟文档内容：这是一个测试文档"


class DatabaseManager:
    pass


class UserService:
    def __init__(self, db_manager):
        pass

    def register_user(self, username, password):
        return True, "user_123"


# UI部分
import sys
import os
import json
import threading
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTextEdit, QScrollArea,
                             QFrame, QFileDialog, QMessageBox, QSplitter, QListWidget,
                             QListWidgetItem, QTextBrowser, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette, QTextCursor


class AIChatApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        # 设置全局样式
        self.setStyle('Fusion')
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f5f7fa;
            }
            QLabel#titleLabel {
                color: #4a6fa5;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #5c7cfa;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4c6ef5;
            }
            QPushButton:pressed {
                background-color: #3b5bdb;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #d0d7e3;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #5c7cfa;
                outline: none;
            }
            /* 对话气泡基础样式 */
            QFrame#messageFrame {
                border-radius: 12px;
                padding: 12px 15px;
                margin: 6px 10px;
                max-width: 70%;
            }
            /* 用户消息气泡 */
            QFrame#userMessage {
                background-color: #5c7cfa;
                color: white;
                /* 右侧小三角效果 */
                border-top-right-radius: 4px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            /* 助手消息气泡 */
            QFrame#assistantMessage {
                background-color: white;
                color: #333;
                border: 1px solid #e1e4e8;
                /* 左侧小三角效果 */
                border-top-left-radius: 4px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }
            /* 系统消息气泡 */
            QFrame#systemMessage {
                background-color: #f0f7ff;
                color: #4299e1;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                max-width: 60%;
            }
            /* 消息文本样式 - 关键：设置透明背景解决白底问题 */
            .messageText {
                background-color: transparent;
                font-size: 15px;
                line-height: 1.5;
                padding: 0;
                margin: 0;
            }
            QScrollArea {
                border: none;
            }
            QListWidget {
                border: none;
                background-color: #f0f2f5;
            }
            QListWidgetItem {
                padding: 8px;
                border-bottom: 1px solid #e1e4e8;
            }
        """)


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("不存在的你，和我 - 登录")
        self.setGeometry(100, 100, 400, 500)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("不存在的你，和我")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 用户名
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("用户名")
        layout.addWidget(self.username_input)

        # 密码
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("密码")
        layout.addWidget(self.password_input)

        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #e74c3c;")
        layout.addWidget(self.status_label)

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self.login)
        button_layout.addWidget(self.login_btn)

        self.register_btn = QPushButton("注册")
        self.register_btn.clicked.connect(self.register)
        button_layout.addWidget(self.register_btn)
        layout.addLayout(button_layout)

        # 底部空白
        layout.addStretch()

        # 绑定回车键
        self.username_input.returnPressed.connect(self.login)
        self.password_input.returnPressed.connect(self.login)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.status_label.setText("用户名和密码不能为空")
            return

        try:
            # 初始化服务
            self.llm = CustomLLM("config.json")
            self.db_manager = DatabaseManager()
            self.chat_service = ChatService(self.llm)
            success, user_id = self.chat_service.login(username, password)

            if success:
                self.chat_window = ChatWindow(user_id, self.chat_service, self.llm)
                self.chat_window.show()
                self.close()
            else:
                self.status_label.setText("登录失败，用户名或密码错误")
        except Exception as e:
            self.status_label.setText(f"登录出错: {str(e)}")

    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            self.status_label.setText("用户名和密码不能为空")
            return

        # 初始化数据库
        db_manager = DatabaseManager()
        user_service = UserService(db_manager)
        success, user_id = user_service.register_user(username, password)

        if success:
            QMessageBox.information(self, "成功", "注册成功，请登录")
            self.status_label.setText("注册成功，请登录")
            self.status_label.setStyleSheet("color: #2ecc71;")
        else:
            self.status_label.setText("注册失败，用户名可能已存在")


class ChatWindow(QMainWindow):
    # 信号用于在主线程更新UI
    update_chat_signal = pyqtSignal(str, str)  # role, content
    update_status_signal = pyqtSignal(str)

    def __init__(self, user_id, chat_service, llm):
        super().__init__()
        self.user_id = user_id
        self.chat_service = chat_service
        self.llm = llm
        self.init_ui()
        self.load_chat_history()

        # 连接信号与槽
        self.update_chat_signal.connect(self.add_message_to_ui)
        self.update_status_signal.connect(self.update_status)

    def init_ui(self):
        self.setWindowTitle("不存在的你，和我 - 莉莉丝对话")
        self.setGeometry(100, 100, 1000, 700)

        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # 左侧边栏 - 对话历史列表
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(250)
        self.sidebar.addItem("当前对话")
        main_layout.addWidget(self.sidebar)

        # 主内容区
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        main_layout.addWidget(content_widget, 1)

        # 顶部导航栏
        top_bar = QWidget()
        top_bar.setMinimumHeight(60)
        top_bar.setStyleSheet("background-color: white; border-bottom: 1px solid #e1e4e8;")
        top_layout = QHBoxLayout(top_bar)

        title_label = QLabel("莉莉丝对话")
        title_label.setObjectName("titleLabel")
        title_label.setStyleSheet("font-size: 18px;")
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        # 上传文档按钮
        self.upload_btn = QPushButton("上传文档")
        self.upload_btn.setStyleSheet("""
            background-color: #49b380;
            color: white;
            border-radius: 8px;
            padding: 6px 12px;
            font-size: 14px;
        """)
        self.upload_btn.clicked.connect(self.upload_document)
        top_layout.addWidget(self.upload_btn)

        # 添加按钮间距
        top_layout.addSpacing(10)

        # 退出登录按钮
        self.logout_btn = QPushButton("退出登录")
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #f87171;
                color: white;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ef4444;
            }
            QPushButton:pressed {
                background-color: #dc2626;
            }
        """)
        self.logout_btn.setIcon(QIcon.fromTheme("system-log-out", QIcon("logout.png")))
        self.logout_btn.setIconSize(QSize(16, 16))
        self.logout_btn.setToolTip("退出当前账号")
        self.logout_btn.clicked.connect(self.logout)
        top_layout.addWidget(self.logout_btn)

        # 添加右侧边距
        top_layout.addSpacing(15)

        content_layout.addWidget(top_bar)

        # 聊天历史区域
        self.chat_scroll_area = QScrollArea()
        self.chat_scroll_area.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_scroll_area.setWidget(self.chat_container)
        content_layout.addWidget(self.chat_scroll_area, 1)

        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        content_layout.addWidget(self.status_label)

        # 输入区域
        input_widget = QWidget()
        input_widget.setMinimumHeight(100)
        input_layout = QVBoxLayout(input_widget)

        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("输入消息...")
        self.input_edit.setMinimumHeight(80)
        input_layout.addWidget(self.input_edit)

        # 输入框下方按钮
        input_buttons = QHBoxLayout()
        self.send_btn = QPushButton("发送")
        self.send_btn.clicked.connect(self.send_message)
        input_buttons.addWidget(self.send_btn)
        input_layout.addLayout(input_buttons)

        content_layout.addWidget(input_widget)

        # 绑定快捷键
        self.input_edit.keyPressEvent = self.on_enter_press

    def on_enter_press(self, event):
        # 按Enter发送消息，Shift+Enter换行
        if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
            self.send_message()
        else:
            super(QTextEdit, self.input_edit).keyPressEvent(event)

    def add_message_to_ui(self, role, content):
        # 创建气泡容器
        frame = QFrame()
        frame.setObjectName("messageFrame")
        frame.setObjectName(f"{role}Message")

        # 创建外层布局控制对齐
        outer_layout = QHBoxLayout()
        if role == "user":
            outer_layout.setAlignment(Qt.AlignRight)  # 用户消息靠右
        else:
            outer_layout.setAlignment(Qt.AlignLeft)  # 助手/系统消息靠左

        # 创建消息文本标签（核心：解决白底问题）
        message_label = QLabel(content)
        message_label.setObjectName("messageText")  # 应用透明背景样式
        message_label.setWordWrap(True)  # 自动换行
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # 允许选中复制
        message_label.setMinimumWidth(50)  # 确保窄内容也有合适宽度

        # 将标签添加到气泡容器
        frame_layout = QHBoxLayout(frame)
        frame_layout.addWidget(message_label)
        frame_layout.setContentsMargins(0, 0, 0, 0)  # 消除内边距避免多余空白

        # 将气泡添加到外层布局
        outer_layout.addWidget(frame)

        # 创建一行容器放置整个气泡
        row_widget = QWidget()
        row_widget.setLayout(outer_layout)
        self.chat_layout.addWidget(row_widget)

        # 滚动到底部
        self.chat_scroll_area.verticalScrollBar().setValue(
            self.chat_scroll_area.verticalScrollBar().maximum()
        )

    def update_status(self, text):
        self.status_label.setText(text)

    def send_message(self):
        user_text = self.input_edit.toPlainText().strip()
        if not user_text:
            return

        # 清空输入框
        self.input_edit.clear()

        # 显示用户消息
        self.update_chat_signal.emit("user", user_text)

        # 异步获取AI回复
        self.update_status_signal.emit("莉莉丝正在输入...")
        threading.Thread(
            target=self.get_ai_response,
            args=(user_text,),
            daemon=True
        ).start()

    def get_ai_response(self, user_text):
        try:
            response = self.chat_service.chat(self.user_id, user_text)
            self.update_status_signal.emit("")
            self.update_chat_signal.emit("assistant", response)
        except Exception as e:
            self.update_status_signal.emit(f"获取回复失败: {str(e)}")

    def load_chat_history(self):
        try:
            history = self.chat_service.get_chat_history(self.user_id)
            for msg in history:
                self.add_message_to_ui(msg["role"], msg["content"])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载历史记录失败: {str(e)}")

    def upload_document(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文档", "",
            "支持的文件 (*.pdf *.txt *.md);;PDF文件 (*.pdf);;文本文件 (*.txt);;Markdown文件 (*.md)"
        )

        if not file_path:
            return

        try:
            self.update_status_signal.emit(f"正在处理文档 {os.path.basename(file_path)}...")
            threading.Thread(
                target=self.process_document,
                args=(file_path,),
                daemon=True
            ).start()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"上传文档失败: {str(e)}")

    def process_document(self, file_path):
        try:
            book = Book(file_path, self.llm)
            toc_info = f"已从文档中提取目录信息:\n{book.content}"
            self.update_status_signal.emit("")
            self.update_chat_signal.emit("system", toc_info)
        except Exception as e:
            self.update_status_signal.emit(f"处理文档失败: {str(e)}")

    def logout(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()


if __name__ == "__main__":
    app = AIChatApp(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())