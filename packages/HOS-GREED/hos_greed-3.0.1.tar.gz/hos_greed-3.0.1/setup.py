from setuptools import setup, find_packages
import os

# 读取README文件内容作为长描述
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    # 包名称
    name="HOS-GREED",
    # 版本号
    version="3.0.1",
    # 作者信息
    author="HOS Team",
    author_email="admin@example.com",
    # 简短描述
    description="轻量化AI安全赋能平台，适合中小型企业",
    # 长描述，用于PYPI
    long_description=long_description,
    long_description_content_type="text/markdown",
    # 项目URL
    url="http://localhost:50000",
    # 包类型
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: System :: Networking :: Monitoring",
    ],
    # Python版本要求
    python_requires=">=3.8",
    # 依赖项
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "pydantic>=2.4.0",
        "pydantic-settings>=2.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    # 查找包
    packages=find_packages(),
    # 包含非Python文件
    include_package_data=True,
    # 入口点
    entry_points={
        "console_scripts": [
            "hos-ai-security=hos_ai_security.main:main",
        ],
    },
    # 关键字
    keywords=["AI", "security", "fastapi", "deepseek", "security-automation"],
)