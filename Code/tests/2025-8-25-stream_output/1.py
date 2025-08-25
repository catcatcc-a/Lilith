import time
from AutoKBAgent.llm_server import LLMService  # 替换为实际的模块名


def test_stream_output(config_path: str):
    """测试流式输出功能，在终端模拟前端接收效果"""
    try:
        # 初始化LLM服务
        llm = LLMService(config_path)
        print("模型加载完成，准备接收输入（输入'exit'退出）...\n")

        while True:
            # 获取用户输入
            user_input = input("请输入问题: ")
            if user_input.lower() == "exit":
                print("测试结束")
                break

            print("\n模型输出: ", end="", flush=True)  # 不换行输出

            # 接收流式输出并实时打印
            start_time = time.time()
            full_response = []

            for chunk in llm.generate_stream(user_input):
                # 实时打印每个片段（模拟前端逐字显示）
                print(chunk, end="", flush=True)
                full_response.append(chunk)
                # 模拟网络延迟（可选，增强演示效果）
                # time.sleep(0.05)

            # 输出统计信息
            end_time = time.time()
            full_text = ''.join(full_response)
            print(f"\n\n输出完成 | 长度: {len(full_text)} 字符 | 耗时: {end_time - start_time:.2f}秒\n")

    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
    finally:
        # 显式触发资源释放
        del llm
        print("\n资源已释放")


if __name__ == "__main__":
    # 替换为你的配置文件路径
    CONFIG_PATH = f"F:\project\Lilith\Config\Qwen3-0.6B.json"
    test_stream_output(CONFIG_PATH)
