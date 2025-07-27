import os
import shutil
import argparse
from pathlib import Path


def find_audio_files(root_dir):
    """
    遍历指定目录及其子目录，查找所有音频文件

    参数:
        root_dir (str): 根目录路径

    返回:
        list: 找到的音频文件路径列表
    """
    # 常见音频文件扩展名列表
    extensions = {
            '.mp3', '.wav', '.flac', '.aac', '.ogg', '.oga', '.m4a',
            '.wma', '.opus', '.alac', '.amr', '.ape', '.au', '.mka'
        }

    audio_files = []

    # 使用os.walk遍历目录树
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            # 检查文件扩展名是否在音频扩展名列表中
            ext = Path(filename).suffix.lower()
            if ext in extensions:
                audio_files.append(os.path.join(dirpath, filename))

    return audio_files


def copy_audio_files(audio_files, dest_dir):
    """
    将音频文件复制到目标目录

    参数:
        audio_files (list): 音频文件路径列表
        dest_dir (str): 目标目录路径
    """
    # 创建目标目录（如果不存在）
    os.makedirs(dest_dir, exist_ok=True)

    copied_count = 0
    skipped_count = 0

    for src_file in audio_files:
        # 获取文件名
        filename = os.path.basename(src_file)
        dest_file = os.path.join(dest_dir, filename)

        # 检查文件是否已存在
        if os.path.exists(dest_file):
            print(f"跳过已存在的文件: {filename}")
            skipped_count += 1
            continue

        try:
            # 复制文件
            shutil.copy2(src_file, dest_file)
            print(f"已复制: {filename}")
            copied_count += 1
        except Exception as e:
            print(f"复制失败 {filename}: {e}")

    print(f"\n操作完成!")
    print(f"总共找到 {len(audio_files)} 个音频文件")
    print(f"成功复制: {copied_count}")
    print(f"跳过已存在: {skipped_count}")
    print(f"复制失败: {len(audio_files) - copied_count - skipped_count}")


if __name__ == "__main__":
    # 查找所有音频文件
    audio_files = find_audio_files(Path(r"F:\project\Lilith\GameAsset"))

    # 将所有音频文件复制到目标目录
    copy_audio_files(audio_files, r"F:\project\Lilith\Dataset\Speech-to-text\audio")