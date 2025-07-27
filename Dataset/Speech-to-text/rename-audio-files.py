import os
import shutil
import argparse
from pathlib import Path

def audio_files(root_dir):
    audio_files_list = []

    # 使用os.walk遍历目录树
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            audio_files_list.append(os.path.join(dirpath, filename))

    return audio_files_list

if __name__ == '__main__':
    i = 0
    list_audio = audio_files(r"F:\project\Lilith\Dataset\Speech-to-text\audio")
    for _ in list_audio:
        os.rename( _ , f"{i}.ogg" )
        print(f"Renamed {i}.ogg")
        i = i + 1