from fastapi import FastAPI, HTTPException, Depends
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import os,functools

from AutoKBAgent.chat_service import ChatService
from AutoKBAgent.custom_llm import CustomLLM
from AutoKBAgent.database import DatabaseManager

# 配置文件路径（根据实际情况修改）
LLM_CONFIG_PATH = f"F:\project\configs\Qwen3-0.6B.json"
# 数据库路径
database_manager_path = "chat_memory.db"

db_manager = DatabaseManager(database_manager_path)

def valid_user_id(func):
    @functools.wraps(func)  # 新增：保留原函数的元信息（包括__name__）
    def wrapper(*args, **kwargs):
        request = kwargs.get("request")
        if db_manager.user_exists(request.user_id):
            return func(*args, **kwargs)
        else:
            raise HTTPException(status_code=404, detail=f"{request.user_id} not exist")
    return wrapper


# 初始化FastAPI应用
app = FastAPI(title="AI聊天接口服务")

# 配置CORS，允许前端跨域访问
# TODO 这里的域名到时候要改一下
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需指定具体前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# 单例LLM和ChatService实例
def get_chat_service():
    """依赖注入：获取ChatService实例"""
    llm = CustomLLM(config_path=LLM_CONFIG_PATH)
    chat_service = ChatService(llm=llm,db_path=database_manager_path)
    return chat_service

# 请求模型定义
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    user_id: str
    password: str

class ChatRequest(BaseModel):
    user_id: str
    input_text: str

# 响应模型定义
class RegisterResponse(BaseModel):
    success: bool
    user_id: str
    message: str

class LoginResponse(BaseModel):
    success: bool
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    user_id: str
    timestamp: str  # 可从数据库记录中获取

# API路由
@app.post("/register", response_model=RegisterResponse)
def register(
    request: RegisterRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """用户注册接口"""
    success, user_id = chat_service.register(request.username, request.password)
    if success:
        return {
            "success": True,
            "user_id": user_id,
            "message": "注册成功"
        }
    raise HTTPException(status_code=400, detail="注册失败，用户名可能已存在")

@app.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """用户登录接口"""
    success, user_id = chat_service.login(request.user_id, request.password)
    if success:
        return {
            "success": True,
            "user_id": user_id,
            "message": "登录成功"
        }
    raise HTTPException(status_code=401, detail="登录失败，用户名或密码错误")

@app.post("/chat", response_model=Dict[str, str])
@valid_user_id
def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """聊天交互接口"""
    try:
        # 获取LLM响应
        response = chat_service.chat(request.user_id, request.input_text)
        # 生成用户总结（可以定期调用而非每次调用）
        chat_service.generate_user_summary(request.user_id)
        return {
            "user_id": request.user_id,
            "response": response["output"],
            "timestamp": response.get("timestamp", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天处理失败: {str(e)}")

@app.get("/history/{user_id}", response_model=List[Dict[str, str]])
@valid_user_id
def get_chat_history(
    user_id: str,
    hours_ago: float = 1,
    chat_service: ChatService = Depends(get_chat_service)
):
    """获取聊天历史记录"""
    try:
        history = chat_service.get_chat_history(user_id, hours_ago)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")

@app.get("/user-summary/{user_id}", response_model=Dict[str, str])
@valid_user_id
def get_user_summary(
    user_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    """获取用户总结信息"""
    try:
        summary = chat_service.get_user_summary(user_id)
        return {
            "user_id": user_id,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户总结失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)