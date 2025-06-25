import os
from anthropic import Anthropic

def call_llm(prompt):
    # 从环境变量获取 Anthropic API 密钥，如果未设置则使用默认值
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "your-api-key"))
    # 调用 Anthropic API 创建消息
    response = client.messages.create(
        model="claude-3-7-sonnet-20250219",  # 指定使用的模型
        max_tokens=10000,  # 设置最大生成令牌数
        messages=[
            {"role": "user", "content": prompt}  # 用户输入的消息
        ]
    )
    # 返回 LLM 的响应文本内容
    return response.content[0].text

if __name__ == "__main__":
    print("## 测试 call_llm")
    prompt = "用几个词概括生命的意义是什么？"
    print(f"## 提示: {prompt}")
    response = call_llm(prompt)
    print(f"## 响应: {response}")