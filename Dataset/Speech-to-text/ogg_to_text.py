import whisper
import os


def ogg_to_text(audio_path, model_name="base"):
    """
    使用 Whisper 模型识别 .ogg 音频文件中的文字

    参数:
        audio_path (str): .ogg 音频文件的路径
        model_name (str): Whisper 模型名称（可选，默认是 "base"）
                          可选模型：tiny, base, small, medium, large (模型越大精度越高，速度越慢)

    返回:
        str: 识别出的文字内容（如果失败则返回空字符串）
    """
    # 检查文件是否存在
    if not os.path.exists(audio_path):
        print(f"错误：文件不存在 - {audio_path}")
        return ""

    # 检查文件是否为 .ogg 格式
    if not audio_path.lower().endswith(".ogg"):
        print(f"错误：请提供 .ogg 格式的音频文件，当前文件：{audio_path}")
        return ""

    try:
        # 加载 Whisper 模型（首次运行会自动下载模型，可能需要几分钟）
        print(f"正在加载 Whisper 模型：{model_name}...")
        model = whisper.load_model(model_name)

        # 识别音频文件（Whisper 原生支持 .ogg 格式）
        print(f"正在识别音频：{os.path.basename(audio_path)}...")
        result = model.transcribe(audio_path)

        # 提取识别结果中的文字
        text = result["text"]
        print("识别完成！")
        return text

    except Exception as e:
        print(f"识别过程出错：{str(e)}")
        return ""


if __name__ == "__main__":
    for i in range(365) :
        audio_file = f".\\audio_renamed\\{i}.ogg"
        recognized_text = ogg_to_text(audio_file, model_name="base")
        with open(f".\\audio_renamed\\{i}.txt", "w", encoding="utf-8") as f:
            f.write(recognized_text)


