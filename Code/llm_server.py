"""
这个模块实现了调用本地大模型的功能，只需要一个配置文件就可以配置所有大模型需要的参数
"""

import json

from transformers import AutoModelForCausalLM, AutoTokenizer , GenerationConfig # 第三方库导入放在后面

class LLMService :
    """
    this is a class encapsulate model loading and inference functions
    every config is stored in config.json
    """
    def __init__(self,config_path:str):
        """initialize the model
        Args:
            the path of config file
            """
        self.config_path = config_path

        self.model_config = self._model_config()
        self.generation = self._generation()

        self.model,self.tokenizer,self.generation_config = self._load_model()

        self.context = [] #存储对话上下文



    def _model_config(self):
        """load model configuration as a dictionary based on the config file"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            _ = config["model"]
            return _

    def _generation(self):
        """load generation based on the config file"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            _ = config["generation"]
            return _


    def _load_model(self):
        """load the model based on the config file"""
        # 1. 加载分词器
        # 作用：将文本转换为模型可理解的数字编码
        # 为什么需要：模型只能处理数值输入，分词器负责文本->数字的转换
        tokenizer = AutoTokenizer.from_pretrained(
            self.model_config["path"],
            local_files_only=True  # 明确指定使用本地文件
        )
        # 2. 加载模型
        # 作用：加载模型权重和架构
        # 为什么需要：将本地权重文件转换为可执行的模型实例
        generation_config = GenerationConfig.from_pretrained(self.model_config["path"])
        generation_config.max_new_tokens = self.generation["max_new_tokens"]
        generation_config.temperature = self.generation["temperature"]
        generation_config.top_p = self.generation["top_p"]
        generation_config.repetition_penalty = self.generation["repetition_penalty"]
        # 3. 配置生成参数
        # 作用：设置文本生成的行为（如随机性、长度等）
        # 为什么需要：控制生成质量和风格
        model= AutoModelForCausalLM.from_pretrained(
            self.model_config["path"],
            device_map=self.model_config["device"],
            trust_remote_code=self.model_config["trust_remote_code"],
            use_safetensors=self.model_config["use_safetensors"]
        )
        return model,tokenizer,generation_config

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

    def generate_response(self,user_input:str):
        """
        generate a response based on text

        Args:
            user_input (str): the input text
        """
        # 1. 构建输入（带或不带上下文）
        if self.model_config["use_context"]:
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
        if self.model_config["use_context"]:
            self.context.append({"role": "assistant", "content": response})

        return response
