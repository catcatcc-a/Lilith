"""
这个模块实现了调用本地大模型的功能，只需要一个配置文件就可以配置所有大模型需要的参数
"""

import json
import gc

from transformers import AutoModelForCausalLM, AutoTokenizer , GenerationConfig # 第三方库导入放在后面
import torch

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

    def __del__(self):
        """
        析构函数：在实例被销毁时释放资源，适配Accelerate管理的模型
        """
        # 1. 优先释放模型（针对Accelerate dispatch的模型，不手动移动设备）
        if hasattr(self, 'model') and self.model is not None:
            try:
                # 移除手动移动设备的代码（避免触发Accelerate冲突）
                # 删除模型参数和缓冲区（直接释放引用）
                if hasattr(self.model, 'parameters'):
                    for param in self.model.parameters():
                        del param
                if hasattr(self.model, 'buffers'):
                    for buf in self.model.buffers():
                        del buf
                del self.model  # 直接删除模型实例，由Accelerate自动处理设备资源
            except Exception as e:
                print(f"释放模型资源时出错: {e}\n")

        # 2. 释放分词器（不变）
        if hasattr(self, 'tokenizer') and self.tokenizer is not None:
            try:
                del self.tokenizer
            except Exception as e:
                print(f"释放分词器时出错: {e}\n")

        # 3. 释放其他属性（不变）
        if hasattr(self, 'generation_config'):
            del self.generation_config
        if hasattr(self, 'context'):
            del self.context
        if hasattr(self, 'model_config'):
            del self.model_config
        if hasattr(self, 'generation'):
            del self.generation

        # 4. 强制垃圾回收
        gc.collect()

        # 5. 清理PyTorch GPU缓存（不变）
        if torch.cuda.is_available():
            try:
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
            except Exception as e:
                print(f"清理GPU缓存时出错: {e}\n")

        print("LLMService 实例已销毁，相关资源已释放\n")


    def _model_config(self) -> dict:
        """
        根据配置文件加载所有model相关的配置
        output：字典
        具体结构可以参考配置文件
        example：
            model = self._model_config
            model["name"]可以访问到模型的名字
        """
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            _ = config["model"]
            return _

    def _generation(self) -> dict:
        """
        根据配置文件加载所有generation相关的配置
        output：字典
        具体结构可以参考配置文件
        example：
            generation = self._generation
            generation["temperature"]可以访问到生成时候设置的temperature
        """
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            _ = config["generation"]
            return _

    def _load_model(self):
        """加载模型和分词器（可能抛出多种错误，由上层try-except捕获）"""
        # 1. 加载分词器（单独捕获分词器加载错误）
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_config["path"],
                local_files_only=True
            )
            print("分词器加载成功")
        except Exception as e:
            raise RuntimeError(f"分词器加载失败：{e}") from e

        # 2. 加载生成配置（单独捕获生成配置错误）
        try:
            generation_config = GenerationConfig.from_pretrained(self.model_config["path"])
            # 更新生成参数
            generation_config.max_new_tokens = self.generation.get("max_new_tokens", 512)
            generation_config.temperature = self.generation.get("temperature", 0.7)
            generation_config.top_p = self.generation.get("top_p", 0.9)
            generation_config.repetition_penalty = self.generation.get("repetition_penalty", 1.0)
            print("生成配置加载成功")
        except Exception as e:
            raise RuntimeError(f"生成配置加载失败：{e}") from e

        # 3. 加载模型（单独捕获模型加载错误）
        try:
            model = AutoModelForCausalLM.from_pretrained(
                self.model_config["path"],
                device_map=self.model_config.get("device", "auto"),  # 允许配置默认值
                trust_remote_code=self.model_config.get("trust_remote_code", False),
                use_safetensors=self.model_config.get("use_safetensors", True)
            )
            # 验证模型是否成功加载到设备
            if not hasattr(model, "device"):
                raise RuntimeError("模型未正确绑定到设备")
            print(f"模型成功加载到设备：{model.device}")
        except Exception as e:
            raise RuntimeError(f"模型权重加载失败：{e}") from e

        return model, tokenizer, generation_config


    def build_prompt_with_context(self):
        """
        在要使用上下文的前提下构建模型的上下文
        是否使用上下文应该在模型的配置文件中设置
        Output： str -> 包含了上下文以及本轮问题的字符串
        """
        prompt = ""
        for msg in self.context:
            if msg["role"] == "user":
                prompt = prompt + f"user : {msg['content']}\n"
            else:
                prompt += f"assistant : {msg['content']}\n"
        prompt += "assistant: "
        return prompt

    def generate_response(self, user_input: str):
        current_input = user_input

        # 构建prompt（记录原始prompt文本，用于后续剥离）
        if self.model_config["use_context"]:
            self.context.append({"role": "user", "content": current_input})
            prompt = self.build_prompt_with_context()
        else:
            prompt = current_input
        # 保存原始prompt用于后续剥离（关键：用原始字符串而非token长度）
        original_prompt = prompt

        # 编码输入（取消max_length强制填充，仅截断过长输入）
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,  # 仅截断超过模型最大长度的输入
            # 移除padding="max_length"和max_length，避免填充导致的长度失真
        ).to(self.model.device)

        # 生成模型输出（包含完整prompt+生成内容）
        outputs = self.model.generate(
            **inputs,
            generation_config=self.generation_config
        )

        # 解码完整输出（含prompt）
        full_output = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        ).strip()

        # 从完整输出中剥离原始prompt，提取纯净回答（核心修改）
        # 处理可能的空格/格式差异（如prompt末尾可能有空格，生成内容前可能有空格）
        original_prompt_stripped = original_prompt.strip()
        full_output_stripped = full_output.strip()

        # 找到prompt在完整输出中的位置并剥离
        if full_output_stripped.startswith(original_prompt_stripped):
            # 从prompt长度之后截取，再处理首尾空格
            current_output = full_output_stripped[len(original_prompt_stripped):].strip()
        else:
            # 极端情况：prompt未完整出现在输出中（如模型截断了prompt），则取完整输出
            # 可根据业务需求调整此处逻辑（如报警、重试）
            current_output = full_output_stripped

        # 更新上下文
        if self.model_config["use_context"]:
            self.context.append({"role": "assistant", "content": current_output})

        # 构建完整上下文
        full_context = "\n".join([
            f"{item['role']}: {item['content']}"
            for item in self.context
        ])

        return {
            "content": full_context,
            "input": current_input,
            "output": current_output
        }