# AI-Lilith

## 项目概述
这个项目结合了langchain与fastapi开发了一个可以调用本地大模型的后端与对应的前端，通过下载模型以及编写配置文件的方式可以实现对这个项目的部署

## 快速启动
- **后端**
    --
    - 克隆git仓库到本地
    - 创建虚拟环境
    - 根据requirements.txt安装对应的各种包
        - 注意：
            - **torch** , **torchaudio** ,**torchvision** 这三个库建议自己根据操作系统安装
            - AutoKBAgent这个作者自己写的库建议删除了 **“.\Lilith\Code\src”** 下的 **AutoKBAgent.egg-info**文件夹之后。将工作文件夹切到 **“.\Code”** 文件夹下用 **pip install -e .** 进行安装
    - 配置文件的编写
        - 在 **“.\Config”** 中有配置文件的示例，重要参数解释如下
            - **path** ：这里填下载好的模型的绝对位置
            - **device** ：建议使用auto，因为已经在环境中下载了accelerate库了，如果accelerate库安装失败，可以尝试不安装这个库，并且手动设置llm运行设备，如果是显卡的话就选择 **cuda0** ，cpu的话就是 **cpu**
            - **其余的配置参数建议不用修改直接使用**
    - 打开api.py文件，通过设置 **LLM_CONFIG_PATH** 和 **database_manager_path** 来设置大模型配置文件的绝对位置和你希望数据库文件的绝对位置
    - 仍然是api.py文件，在代码的34-40行左右，可以设置前端的域名
    - 现在你已经完成了后端快速启动所需的所有配置！！！ ：）
    - Attention:
        配置文件中 “model.path” 这个变量在windows和linux系统中都应该使用 “/” 作为路径的分隔符而不是 “\” 

- **前端**
    --
    - 




