import uuid  # 用于生成唯一用户ID
import hashlib  # 用于密码哈希
from database import DatabaseManager  # 导入数据库管理类


class UserService:
    def __init__(self, db_manager: DatabaseManager):
        # 接收数据库管理器实例（依赖注入，便于测试）
        self.db_manager = db_manager

    def _hash_password(self, password: str) -> str:
        """将明文密码转为SHA-256哈希值（不可逆，增强安全性）"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str) -> tuple[bool, str]:
        """注册新用户：生成UUID、哈希密码，调用数据库保存"""
        user_id = str(uuid.uuid4())  # 生成唯一用户ID（UUIDv4）
        password_hash = self._hash_password(password)  # 哈希密码

        # 调用数据库添加用户，返回成功状态和user_id
        if self.db_manager.add_user(user_id, username, password_hash):
            return True, user_id
        return False, ""  # 失败（如用户名重复）

    def login_user(self, username: str, password: str) -> tuple[bool, str]:
        """用户登录：哈希输入密码，与数据库中存储的哈希值比对"""
        password_hash = self._hash_password(password)  # 哈希输入密码
        user_id = self.db_manager.verify_user(username, password_hash)  # 验证

        if user_id:
            return True, user_id  # 验证成功
        return False, ""  # 失败（用户名或密码错误）