import os

from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

# 从环境变量中获取 OpenAI API 密钥
api_key = os.getenv("OPENAI_API_KEY")
# 定义 OpenAI API 的基础 URL
base_url = "https://api.openai.com/v1"
# 定义使用的模型
model = "gpt-4o"


def call_llm(message: str):
    # 打印调用 LLM 的消息
    print(f"Calling LLM with message: \n{message}")
    # 初始化 OpenAI 客户端
    client = OpenAI(api_key=api_key, base_url=base_url)
    # 创建聊天补全请求
    response: ChatCompletion = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": message}]
    )
    # 返回 LLM 的响应内容
    return response.choices[0].message.content


if __name__ == "__main__":
    # 在主程序中测试 call_llm 函数
    print(call_llm("你好，你怎么样？"))
