from setuptools import setup, find_packages

setup(
    name="AutoKBAgent",
    version="0.1",
    packages=find_packages()  # 自动识别mylib
)
# 在project/目录下执行命令，以 “可编辑模式” 安装：
# pip install -e .