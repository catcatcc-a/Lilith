import sqlite3  # 导入SQLite数据库模块
from datetime import datetime, timedelta
from typing import Optional, List, Dict  # 类型注解支持
import os

current_script_dir = os.path.dirname(os.path.abspath(__file__))

class DatabaseManager:
    """
    这是一个使用sqlite3编写的轻量化管理数据库的模块
    """
    def __init__(self, db_path: str = "chat_memory.db"):
        # 初始化数据库连接路径，默认创建chat_memory.db文件
        # TODO:这里的存储路径要晚点要改一下
        self.db_path = db_path
        self._init_tables()  # 初始化数据表

    def _init_tables(self):
        """初始化数据库表结构：用户表、对话历史表、对话总结表"""
        conn = sqlite3.connect(self.db_path)  # 连接数据库（不存在则创建）
        cursor = conn.cursor()  # 创建游标用于执行SQL

        # 用户表：存储用户唯一标识、用户名、密码哈希、创建时间
        # 注意，这里的密码哈希要在其他地方处理，这里没有处理
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,  -- 唯一用户ID（UUID）
            username TEXT NOT NULL,  -- 用户名（不唯一）
            password_hash TEXT NOT NULL,  -- 密码哈希（不存明文）
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间（默认当前时间）
            user_summary  TEXT  -- 让ai总结出来的用户性格，可以改变，每次对话结束的时候更新
        )
        ''')

        # 对话历史表：存储用户的每一条对话消息
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增ID
            user_id TEXT NOT NULL,  -- 关联用户ID（外键）
            role TEXT NOT NULL,  -- 角色（'user'或'assistant'）
            content TEXT NOT NULL,  -- 消息内容
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 消息时间
            FOREIGN KEY (user_id) REFERENCES users(user_id)  -- 关联用户表，保证外键关联的合法性
        )
        ''')

        # 重要事件记录表：存储用户与llm提及的事件的记忆，通过对对话的提取实现
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- 自增id
            user_id TEXT NOT NULL,  -- 关联用户ID（外键）
            memory TEXT NOT NULL,  -- 用户与llm提及的事件  
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 记录时间
            FOREIGN KEY (user_id) REFERENCES users(user_id)  -- 关联用户表，保证外键关联的合法性
        )''')

        conn.commit()  # 提交事务
        conn.close()  # 关闭连接

    def add_user(self, user_id: str, username: str, password_hash: str) -> bool:
        """添加新用户，返回是否成功（失败可能因user_id重复）"""
        try:
            # 确保数据库连接正确关闭
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 插入用户数据，现在允许用户名重复
                cursor.execute(
                    "INSERT INTO users (user_id, username, password_hash) VALUES (?, ?, ?)",
                    (user_id, username, password_hash)
                )
                # with语句会自动提交事务，无需手动调用conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            # 现在唯一可能的完整性错误是user_id重复（因为username已允许重复）
            if "UNIQUE constraint failed: users.user_id" in str(e):
                # 用户ID重复的情况
                return False
            # 处理其他可能的完整性错误
            raise  # 抛出未预期的完整性错误
        except sqlite3.Error:
            # 处理其他数据库错误（如连接问题等）
            return False

    def user_exists(self, user_id: str) -> bool:
        """用于检查用户是否存在，返回bool值"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT user_id FROM users WHERE user_id = ?""",(user_id,))
                result = cursor.fetchone()
                if result:
                    return True
                else:
                    return False

        except sqlite3.Error:
            return False

    def verify_user(self, user_id: str, password_hash: str) -> str:
        """
        验证用户身份
        :param user_id: 待验证的用户ID
        :param password_hash: 待验证的密码哈希
        :return: 验证成功返回对应的user_id，失败返回None
        """
        # 使用with语句确保数据库连接自动关闭
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 查询用户ID和密码哈希都匹配的记录
            cursor.execute(
                "SELECT user_id FROM users WHERE user_id = ? AND password_hash = ?",
                (user_id, password_hash)  # 用user_id作为查询条件之一
            )
            # 获取查询结果（最多一条，因为user_id是主键唯一）
            # 返回值的类型是tuple或者None
            result = cursor.fetchone()

        # 如果有匹配的记录，返回查询到的user_id；否则返回None
        # result是一个元组（如(user_id,)），取第一个元素即为user_id
        return result[0] if result else None

    def save_chat_message(self, user_id: str, role: str, content: str, message_time: str) -> None:
        """保存单条对话消息（用户或助手）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, role, content, message_time)
        )
        conn.commit()
        conn.close()

    def get_recent_chat_history(self, user_id: str, hours_ago: float = 1) -> List[Dict]:
        """获取用户最近的对话历史（默认当前系统时间前一个小时到当前系统时间的所有消息，可以设置时间），按时间正序返回"""

        start_time = datetime.now() - timedelta(hours=hours_ago)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 按时间倒序查询（最新的在前），限制条数
        cursor.execute(
            """SELECT role, content, timestamp FROM chat_history 
               WHERE user_id = ? 
               AND timestamp >= ? 
               ORDER BY timestamp ASC""",
            (user_id, start_time.isoformat())
        )
        results = cursor.fetchall()  # 获取所有结果
        # 获取查询到的所有记录，返回一个列表，每个元素是一个元组（包含 role, content, timestamp 的值）。
        conn.close()
        # 反转列表，转为时间正序（最早的在前），包装成字典
        return [
            {"role": role, "content": content, "timestamp": timestamp}
            for role, content, timestamp in reversed(results)
        ]

    def save_user_summary(self, user_id: str, user_summary: str) -> bool:
        """保存或更新用户的对话总结（存在则更新，否则新增）"""
        if self.user_exists(user_id):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                UPDATE users SET user_summary = ? WHERE user_id = ?
                """,
                (user_summary, user_id))
            return True

        else:
            return False

    def save_memory(self, user_id: str, memory: str) -> bool:
        """保存或更新记忆（存在则更新，否则新增）"""
        if self.user_exists(user_id):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO memories (user_id, memory) VALUES (?, ?)
                """,
                (user_id, memory))
            return True

        else:
            return False

    def get_user_summary(self, user_id: str) -> str:
        """
        读取对用户的印象
        """
        if self.user_exists(user_id):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT user_summary FROM users WHERE user_id = ?
                """,(user_id,))

                result = cursor.fetchone()
                if result:
                    return result[0]
                else:
                    return "nothing!"
        else :
            return "user not found!"