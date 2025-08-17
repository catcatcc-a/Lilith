import sqlite3  # 导入SQLite数据库模块
from typing import Optional, List, Dict  # 类型注解支持
import os

current_script_dir = os.path.dirname(os.path.abspath(__file__))

class DatabaseManager:
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

    def verify_user(self, user_id: str, password_hash: str) -> bool:
        """
        验证用户身份
        :param user_id: 待验证的用户ID
        :param password_hash: 待验证的密码哈希
        :return: 验证成功返回user_id，失败返回None
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
            result = cursor.fetchone()

        # 如果有匹配的记录，返回对应的True；否则返回False
        return result is not None

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

    def get_recent_chat_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """获取用户最近的对话历史（默认10条），按时间正序返回"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 按时间倒序查询（最新的在前），限制条数
        cursor.execute(
            "SELECT role, content, timestamp FROM chat_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)
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


import os
import uuid
import sqlite3
from datetime import datetime
import logging


def setup_test_environment():
    """设置测试环境：创建日志目录、配置日志格式"""
    # 确保当前目录存在（实际运行中通常已存在）
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 配置日志：输出到文件和控制台
    log_filename = os.path.join(current_dir, f"test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename, encoding="utf-8"),  # 日志写入文件
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )
    logging.info("=== 测试环境初始化完成 ===")
    logging.info(f"测试日志将保存至：{log_filename}")

    # 数据库文件路径（当前目录下）
    db_filename = os.path.join(current_dir, "test_chat_memory.db")
    logging.info(f"测试数据库将保存至：{db_filename}")

    return db_filename, log_filename


def test_database_manager():
    # 初始化测试环境
    db_path, log_path = setup_test_environment()
    logger = logging.getLogger()

    try:
        # 初始化数据库管理器
        logger.info("\n=== 1. 初始化数据库连接 ===")
        db = DatabaseManager(db_path=db_path)
        logger.info("✅ 数据库连接成功，表结构初始化完成")

        # 生成测试用户数据
        test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"  # 随机唯一用户ID
        test_username = "测试用户"
        test_password_hash = "test_hash_123"  # 模拟密码哈希
        non_exist_user_id = "non_exist_user_123"  # 不存在的用户ID
        logger.info(f"生成测试用户ID：{test_user_id}")

        # 1. 测试添加用户（add_user）
        logger.info("\n=== 2. 测试添加用户 ===")
        add_success = db.add_user(test_user_id, test_username, test_password_hash)
        assert add_success, "添加新用户失败"
        logger.info("✅ 添加新用户成功（数据库写入：users表新增记录）")

        # 测试重复添加同一用户ID
        add_duplicate = db.add_user(test_user_id, "重复用户名", "hash456")
        assert not add_duplicate, "重复添加用户未被拦截"
        logger.info("✅ 重复用户ID拦截成功（未写入数据库）")

        # 2. 测试用户存在性检查（user_exists）
        logger.info("\n=== 3. 测试用户存在性检查 ===")
        exists = db.user_exists(test_user_id)
        assert exists, "存在的用户未检测到"
        logger.info("✅ 存在用户检测成功（查询users表验证）")

        not_exists = db.user_exists(non_exist_user_id)
        assert not not_exists, "不存在的用户被误判"
        logger.info("✅ 不存在用户检测成功（查询users表验证）")

        # 3. 测试用户验证（verify_user）
        logger.info("\n=== 4. 测试用户身份验证 ===")
        # 正确密码验证
        verify_success = db.verify_user(test_user_id, test_password_hash)
        assert verify_success, "正确密码验证失败"
        logger.info("✅ 正确密码验证成功（查询users表：user_id和password_hash匹配）")

        # 错误密码验证
        verify_fail = db.verify_user(test_user_id, "wrong_hash")
        assert not verify_fail, "错误密码验证未拦截"
        logger.info("✅ 错误密码验证拦截成功（密码哈希不匹配）")

        # 4. 测试保存聊天消息（save_chat_message）
        logger.info("\n=== 5. 测试保存聊天消息 ===")
        test_message_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_message_content = "你好，这是一条测试消息"
        db.save_chat_message(
            user_id=test_user_id,
            role="user",
            content=test_message_content,
            message_time=test_message_time
        )
        logger.info(f"✅ 聊天消息保存成功（数据库写入：chat_history表新增记录，内容：{test_message_content}）")

        # 5. 测试获取最近聊天历史（get_recent_chat_history）
        logger.info("\n=== 6. 测试获取聊天历史 ===")
        history = db.get_recent_chat_history(test_user_id, limit=10)
        assert len(history) >= 1, "未查询到聊天消息"
        assert history[0]["content"] == test_message_content, "聊天内容不匹配"
        logger.info(f"✅ 聊天历史查询成功（从chat_history表读取{len(history)}条记录）")

        # 6. 测试保存用户总结（save_user_summary）
        logger.info("\n=== 7. 测试保存用户总结 ===")
        test_summary = "这是测试用户的性格总结：喜欢测试功能"
        summary_success = db.save_user_summary(test_user_id, test_summary)
        assert summary_success, "存在用户的总结保存失败"
        logger.info(f"✅ 用户总结保存成功（数据库更新：users表user_summary字段设为'{test_summary}'）")

        # 对不存在的用户保存总结
        summary_fail = db.save_user_summary(non_exist_user_id, "无效总结")
        assert not summary_fail, "不存在用户的总结未拦截"
        logger.info("✅ 不存在用户的总结拦截成功（未更新数据库）")

        # 7. 测试保存记忆（save_memory）
        logger.info("\n=== 8. 测试保存记忆 ===")
        test_memory = "测试记忆：用户在2025年8月进行了功能测试"
        memory_success = db.save_memory(test_user_id, test_memory)
        assert memory_success, "存在用户的记忆保存失败"
        logger.info(f"✅ 记忆保存成功（数据库写入：memories表新增记录，内容：{test_memory}）")

        # 验证记忆是否正确插入（手动查询数据库）
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT memory FROM memories WHERE user_id = ?", (test_user_id,))
            saved_memory = cursor.fetchone()
            assert saved_memory and saved_memory[0] == test_memory, "记忆内容不匹配"
        logger.info("✅ 记忆内容验证成功（从memories表查询确认）")

        # 对不存在的用户保存记忆
        memory_fail = db.save_memory(non_exist_user_id, "无效记忆")
        assert not memory_fail, "不存在用户的记忆未拦截"
        logger.info("✅ 不存在用户的记忆拦截成功（未写入数据库）")

        # 最终验证：数据库文件是否生成
        assert os.path.exists(db_path), "数据库文件未生成"
        logger.info("\n🎉 所有测试通过！数据库功能正常")
        logger.info(f"测试日志已保存至：{log_path}")
        logger.info(f"测试数据库已保存至：{db_path}")

    except AssertionError as e:
        logger.error(f"\n❌ 测试失败：{str(e)}", exc_info=False)
    except Exception as e:
        logger.error(f"\n❌ 测试过程发生意外错误：{str(e)}", exc_info=True)
    finally:
        logger.info("\n=== 测试结束 ===")


if __name__ == "__main__":
    test_database_manager()