"""
实现了langchain库与llm_server库对大模型封装的对接，方便后续做workflow
"""

from typing import Optional, List, Mapping, Any
from pydantic import PrivateAttr
from pathlib import Path

from langchain.llms.base import LLM

from .llm_server import LLMService

class CustomLLM(LLM):
    """
    作用：返回一个字符串，表示这个 LLM 的类型。

    通过_custom_pipeline得到包含了上下文，用户输入，LLM输出的完整content
    通过_call得到纯净的LLM输出，并且可以自定义停止词
    """
    _config_path: str = PrivateAttr()
    _large_language_model: LLMService = PrivateAttr()

    def __init__(self, config_path: str):
        super().__init__()  # 不需要向父类传递config_path
        self._config_path = str(Path(config_path).resolve())  # 赋值给私有属性
        # 初始化模型服务
        self._large_language_model = LLMService(self._config_path)

    # 包装自定义的LLM接口
    def custom_pipeline(self,input_text: str):
        """
        这个是一个包装自定义LLM接口的函数

        Args：input_text -> 用户的输入

        Output：response -> 返回一个字典
            通过"input"访问用户的输入
            通过"output"访问纯净的LLM输出
            通过"content"访问上下文（如果在配置文件中有开启模型上下文的话）
        """
        response = self._large_language_model.generate_response(input_text)
        return response

    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self, prompt :str, stop: Optional[List[str]] = None,**kwargs) -> str:
        """
        Args：
            prompt -> 用户的输入
            stop -> 列表，包括了停止的词，每个词是一个str

        Output：纯净的LLM输出
        """
        result = self.custom_pipeline(prompt)["output"]
        # 如果需要处理停止词，可以在这里添加逻辑
        if stop is not None:
            for s in stop:
                if s in result:
                    result = result[:result.index(s)]
        return result

    #作用：返回一个字典，包含标识这个 LLM 实例的参数。
    @property
    def _model_config(self) -> Mapping[str, Any]:
        """
        返回一个字典，包含标识这个 LLM 实例的参数

        example：
            config = self._large_language_model.config
            config["model"]["name"]
            这样就返回了模型的名称，具体的结构可以参考配置文件
        """
        return self._large_language_model.model_config

    @property
    def _generation(self) -> Mapping[str, Any]:
        return self._large_language_model.generation
