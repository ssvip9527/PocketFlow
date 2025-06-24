import os
from openai import OpenAI
from pathlib import Path

# 获取项目根目录（utils目录的父目录）
ROOT_DIR = Path(__file__).parent.parent

# 使用环境变量中的API密钥初始化OpenAI客户端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
