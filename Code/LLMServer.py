from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import json
from typing import Optional,Dict,List

class LLMService :
    """this is a class encapsulate model loading and inference functions"""
    def __init__(self,config_path:str):
        """initialize the model
        Args:
            the path of config file
            """
        self.configp_path = config_path
        self.model,self.tokenizer,self.generation_config,self.model_name = self._load_model()
        self.context = [] #存储对话上下文

    def _load_model(self):
        """load the model based on the config file"""
        with open(self.configp_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            # 1. 加载分词器
            # 作用：将文本转换为模型可理解的数字编码
            # 为什么需要：模型只能处理数值输入，分词器负责文本->数字的转换
            tokenizer = AutoTokenizer.from_pretrained(config["model"]["path"])
            # 2. 加载模型
            # 作用：加载模型权重和架构
            # 为什么需要：将本地权重文件转换为可执行的模型实例
            generation_config = GenerationConfig.from_pretrained(config["model"]["path"])
            # 3. 配置生成参数
            # 作用：设置文本生成的行为（如随机性、长度等）
            # 为什么需要：控制生成质量和风格
            model= AutoModelForCausalLM.from_pretrained(
                config["model"]["path"],
                device_map=config["model"]["device"],
                trust_remote_code=True,
                use_safetensors=True
            )
            model_name = config["model"]["name"]
            return model,tokenizer,generation_config,model_name

    def build_prompt_with_context(self):
        """build the prompt with context"""
        prompt = ""
        for msg in self.context:
            if msg["role"] == "user":
                prompt = prompt + f"user : {msg['content']}\n"
            else:
                prompt += f"assistant : {msg['content']}\n"
        prompt += "assistant: "
        return prompt

    def generate_response(self,user_input:str,use_context:bool = True):
        """
        generate a response based on text

        Args:
            user_input (str): the input text
            use_context (bool): whether to use content or not
        """
        # 1. 构建输入（带或不带上下文）
        if use_context:
            # 拼接历史对话（多轮对话）
            self.context.append({"role": "user", "content": user_input})
            prompt = self.build_prompt_with_context()
        else:
            # 不使用上下文（单轮对话）
            prompt = user_input

        # 2.编码输入
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True
        ).to(self.model.device)

        # 3.generate response
        outputs = self.model.generate(
            **inputs,
            generation_config = self.generation_config
        )

        # 4.decoding and output
        response = self.tokenizer.decode(outputs[0])

        # 5.renew contest
        if use_context:
            self.context.append({"role": "assistant", "content": response})

        return response

if __name__ == "__main__":
    Qwen = LLMService(config_path=r"F:\project\Lilith\Code\qwen2.5-1.8B.json")
    generated_response = Qwen.generate_response(user_input="你好，介绍一下你自己吧！")
    print(generated_response)