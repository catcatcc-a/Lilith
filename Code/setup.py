from setuptools import setup, find_packages

setup(
    # 包名称（PyPI上的标识，小写无空格）
    name="AutoKBAgent",
    # 版本号（主.次.修订）
    version="0.1.0",
    # 作者信息
    author="catcatcc",
    author_email="3349848922@qq.com",
    # 简短描述
    description="自动化KB代理服务核心库",
    # 包位置配置（对应之前的目录结构）
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    # 支持的Python版本
    python_requires=">=3.10",
)

# 在project/目录下执行命令，以 “可编辑模式” 安装：
# pip install -e .