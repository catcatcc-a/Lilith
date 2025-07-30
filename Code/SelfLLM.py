from LLMServer import LLMService
from langchain.llms.base import LLM
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from typing import Optional, List, Mapping, Any

# 模型相关的设置均在配置文件中设置
LargeLanguageModel = LLMService(config_path=r"F:\project\Lilith\Code\qwen2.5-1.8B.json")

# 包装自定义的LLM接口
def custom_pipeline(input_text: str):
    response = LargeLanguageModel.generate_response(input_text)
    return response


class CustomLLM(LLM):
    #作用：返回一个字符串，表示这个 LLM 的类型。
    @property
    def _llm_type(self) -> str:
        return "custom"

    def _call(self, prompt: str, stop: Optional[List[str]] = None,**kwargs) -> str:
        result = custom_pipeline(prompt)
        # 如果需要处理停止词，可以在这里添加逻辑
        if stop is not None:
            for s in stop:
                if s in result:
                    result = result[:result.index(s)]
        return result

    #作用：返回一个字典，包含标识这个 LLM 实例的参数。
    @property
    def _model_config(self) -> Mapping[str, Any]:
        return LargeLanguageModel.model_config

    @property
    def _generation(self) -> Mapping[str, Any]:
        return LargeLanguageModel.generation


# 集成到 LangChain
llm = CustomLLM()

# 使用新的 RunnableSequence API
prompt = PromptTemplate(
    template="请详细解释 {concept} 的基本原理",
    input_variables=["concept"]
)

# 构建链
chain = prompt | llm

# 调用链（使用 invoke 方法）
result = chain.invoke({"concept": "量子计算"})
print(result)