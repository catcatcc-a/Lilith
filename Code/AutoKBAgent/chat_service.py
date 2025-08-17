from custom_llm import CustomLLM  # 自定义LLM
from user_service import UserService  # 用户服务
from memory_manager import MemoryManager  # 记忆管理
from database import DatabaseManager  # 数据库管理


class ChatService:
    def __init__(self, llm: CustomLLM, db_path: str = "chat_memory.db"):
        # 初始化依赖组件
        self.llm = llm  # LLM实例
        self.db_manager = DatabaseManager(db_path)  # 数据库管理器
        self.user_service = UserService(self.db_manager)  # 用户服务
        self.memory_manager = MemoryManager(self.db_manager, llm)  # 记忆管理器
        # 对话提示模板：指导LLM基于上下文生成回复
        self.CONVERSATION_PROMPT_TEMPLATE = """
        基于以下上下文信息和用户当前的问题，生成合适的回答:

        上下文信息:
        {context}

        用户当前问题:
        {user_input}

        回答:
        """

    def register(self, username: str, password: str) -> tuple[bool, str]:
        """用户注册（代理调用用户服务）"""
        return self.user_service.register_user(username, password)

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """用户登录（代理调用用户服务）"""
        return self.user_service.login_user(username, password)

    def chat(self, user_id: str, user_input: str) -> str:
        """处理用户对话的完整流程"""
        # 1. 保存用户输入到对话历史
        self.memory_manager.save_message(user_id, "user", user_input)

        # 2. 获取上下文（总结+最近对话）
        context = self.memory_manager.get_context_for_generation(user_id)

        # 3. 构建完整提示（上下文+用户输入）
        prompt = self.CONVERSATION_PROMPT_TEMPLATE.format(
            context=context,
            user_input=user_input
        )

        # 4. 调用LLM生成回复
        response = self.llm._call(prompt)

        # 5. 保存LLM回复到对话历史
        self.memory_manager.save_message(user_id, "assistant", response)

        # 6. 每5条消息更新一次总结（控制总结频率，避免频繁调用LLM）
        history_count = len(self.memory_manager.get_recent_history(user_id, 100))
        if history_count % 5 == 0:
            self.memory_manager.generate_summary(user_id)

        return response  # 返回LLM回复

    def get_chat_history(self, user_id: str, limit: int = 20) -> List[dict]:
        """获取用户对话历史（代理调用记忆管理器）"""
        return self.memory_manager.get_recent_history(user_id, limit)

    def get_chat_summary(self, user_id: str) -> str:
        """获取用户对话总结（代理调用记忆管理器）"""
        return self.memory_manager.get_chat_summary(user_id) or "暂无对话总结"