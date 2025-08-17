from langchain.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema import Document

from . import custom_llm

class Book :
    """
    这个类用于实现对文档的操作
    """
    def __init__(self, file_path:str, llm:custom_llm.CustomLLM = None):
        self.file_path = file_path
        self.llm = llm

        #Document这个类存储了一段文本及其相关元数据的类，可以用page_content属性来访问
        self.document = self._load_document(self.file_path)
        self.content = self._content(self.document, self.llm)

    @staticmethod
    def _load_document(file_path):
        """
        加载 PDF 或文本文件，返回 LangChain Document 列表。
        :param file_path: 文件路径（支持 .pdf, .txt, .md）
        :return: 加载后的 Document 列表
        """
        if file_path.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith((".txt", ".md")):
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise ValueError("仅支持 PDF、TXT、MD 格式")
        return loader.load()

    @staticmethod
    def _is_table_of_contents_complete(text:str , llm : custom_llm.CustomLLM = None):
        """
        让LLM判断当前文本中的目录是否完整
        :param text: 待判断的文本内容
        :param llm: LangChain LLM 实例
        :return: 目录是否完整（True/False）
        """
        if llm is None:
            llm = custom_llm.CustomLLM()
        prompt = PromptTemplate(
            input_variables=["text"],
            template="""请判断以下文本中的目录是否完整。判断标准：
        1. 是否包含文档所有主要章节
        2. 章节层级是否完整（如章、节、小节）
        3. 页码标注是否连续且合理

        仅返回"完整"或"不完整"，无需额外解释。

        文本内容：
        {text}
        """
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.run(text=text).strip()
        if result == "完整":
            return True
        elif result == "不完整":
            return False
        else:
            raise ValueError(f"没有返回“完整”或者“不完整”\nAI输出：{result}")

    @staticmethod
    def _structure_table_of_contents(raw_toc: str, llm: custom_llm.CustomLLM) -> list:
        """
        将原始目录文本转换为结构化列表（包含章节标题和页码）
        :param raw_toc: 原始目录文本
        :param llm: OpenAI LLM实例
        :return: 结构化目录列表，每个元素为{"title": "...", "page": "..."}
        """
        prompt = PromptTemplate(
            input_variables=["raw_toc"],
            template="""请将以下目录文本转换为结构化列表，每个条目包含"title"（章节标题）和"page"（页码）字段。
    输出格式要求：
    1. 严格使用JSON数组格式
    2. 页码仅保留数字（去除"页"等后缀）
    3. 保留章节层级关系（如在标题前添加"1.1 "等前缀）
    
    目录文本：
    {raw_toc}
        """
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        structured_result = chain.run(raw_toc=raw_toc)

        # 解析JSON结果（实际使用中建议添加异常处理）
        import json
        return json.loads(structured_result)

    @staticmethod
    def _content(documents:list[Document], llm: custom_llm.CustomLLM = None):
        """
        用 LLM 提取文档目录（章节标题+页码）
        :param documents: 加载后的 Document 列表
        :param llm: LangChain LLM 实例
        :return: 目录文本（字符串）
        """
        prompt = PromptTemplate(
            input_variables=["document"],
            template="请提取以下文档的**目录结构**（含章节标题和页码）：\n{document}\n\n目录："
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        # 取前 3 页内容分析目录（减少 Token 消耗）
        sample_text = "\n".join([doc.page_content for doc in documents[:3]])
        return chain.run(document=sample_text)