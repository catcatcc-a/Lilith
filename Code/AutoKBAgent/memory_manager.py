from typing import List, Dict, Optional  # 类型注解
from datetime import datetime
from database import DatabaseManager  # 数据库操作
from custom_llm import CustomLLM  # 自定义LLM类
from utils import dict_or_list_to_str


class MemoryManager:
    def __init__(self, db_manager: DatabaseManager, llm: CustomLLM):
        # 依赖数据库管理器和LLM实例
        self.db_manager = db_manager
        self.llm = llm
        self.generate_memory_prompt = """
        你是一个善解人意的朋友，现在要根据之前你和用户的对话来总结这段对话里面重要的事件，方便你记忆住这些事情，为你们以后成为更好的朋友打下基础，输出中不要暴露你是一个ai，就像一个正常的朋友一样说话就好。
        要求：总结严谨有逻辑，不失人文风采
        """
        self.generate_summary_prompt = """
        你是一个善解人意的朋友，现在要根据之前你和用户的对话以及对之前对用户的印象来总结你对用户新的印象
        要求：总结出来的印象严谨有逻辑，不失人文风采，可以帮助你判断用户真实的性格
        """

    def save_message(self, user_id: str, response: Dict[str,str]) -> None:
        """
        保存单条对话消息（代理调用数据库方法）
        每次生成完消息之后要调用
        """
        self.db_manager.save_chat_message(
            user_id, role = "user",
            content = response["input"],
            message_time = datetime.now().isoformat()
        )
        self.db_manager.save_chat_message(
            user_id, role = "assistant",
            content = response["output"],
            message_time = datetime.now().isoformat()
        )

    def generate_memory (self, user_id: str) -> None:
        """
        根据近期的对话生成新的记忆并且存储入数据库
        实现思路：
            提取历史记录（默认是一个小时）
            将历史记录转化成字符串
            然后生成对应的提示词
            传给ai获得回答
            写入数据库
        """
        chat_history = self.db_manager.get_recent_chat_history(user_id)
        str_chat = dict_or_list_to_str(chat_history)
        memory_prompt = str_chat+self.generate_memory_prompt
        memory = self.llm._custom_pipeline(memory_prompt)["output"]
        self.db_manager.save_memory(user_id, memory)


    def generate_user_summary(self, user_id: str) -> str:
        """
        根据新存在的对话，以及之前的对用户的印象，结合起来生成新的对用户的印象
        实现思路：
            提取最近对话的历史
            将历史记录转化成字符串
            读取之前的记忆
            生成对应的提示词
            传入ai并且获得回答
            写入数据库
        """
        # 获取最近的对话历史
        chat_history = self.db_manager.get_recent_chat_history(user_id)
        str_chat = dict_or_list_to_str(chat_history)
        old_memory = self.db_manager.get_user_summary(user_id)
        mixture_prompt = f"""历史对话：\n{str_chat}\n\n\n前一次对用户的印象：\n{old_memory}\n\n\n"""+self.generate_summary_prompt
        memory = self.llm._custom_pipeline(mixture_prompt)["output"]
        self.db_manager.save_user_summary(user_id, memory)

