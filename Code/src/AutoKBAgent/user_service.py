import uuid  # 用于生成唯一的用户ID（UUID）
import hashlib  # 用于对密码进行哈希加密（安全存储密码）
from .database import DatabaseManager  # 导入数据库管理类，用于与数据库交互


class UserService:
    def __init__(self, db_manager: DatabaseManager):
        # 接收数据库管理器实例（采用依赖注入模式，方便后续替换或测试）
        self.db_manager = db_manager

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        私有方法：将明文密码转换为SHA-256哈希值
        哈希是不可逆的加密方式，避免明文存储密码，增强安全性
        """
        # 1. 将字符串密码转为字节流（encode()默认使用UTF-8编码）
        # 2. 使用SHA-256算法计算哈希值
        # 3. 将哈希结果转为十六进制字符串返回
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str) -> tuple[bool, str]:
        """
        注册新用户
        流程：生成UUID -> 哈希密码 -> 调用数据库保存
        返回：(是否成功, 用户ID)
        """
        # 生成唯一用户ID（UUIDv4格式，随机生成，全球唯一）
        user_id = str(uuid.uuid4())
        # 调用私有方法对密码进行哈希处理
        password_hash = self._hash_password(password)

        # 调用数据库管理器的add_user方法保存用户信息
        # 如果保存成功，返回(True, 用户ID)；否则返回(False, 空字符串)
        if self.db_manager.add_user(user_id, username, password_hash):
            return True, user_id
        return False, ""  # 失败场景：如用户名已存在等

    def login_user(self, username: str, password: str) -> tuple[bool, str]:
        """
        用户登录验证
        流程：哈希输入密码 -> 与数据库中存储的哈希值比对
        返回：(是否成功, 用户ID)
        """
        # 对用户输入的密码进行哈希处理（与注册时的算法一致）
        password_hash = self._hash_password(password)
        # 调用数据库管理器的verify_user方法验证用户名和哈希密码
        # 若验证通过，返回对应的user_id；否则返回None
        user_id = self.db_manager.verify_user(username, password_hash)

        # 如果验证成功，返回(True, 用户ID)；否则返回(False, 空字符串)
        if user_id:
            return True, user_id
        return False, ""