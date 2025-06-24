from anthropic import Anthropic
import os

def call_llm(prompt):
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "your-api-key"))
    response = client.messages.create(
        model="claude-sonnet-4-20250514", # 模型选择
        max_tokens=6000, # 最大 token 数
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.content[0].text

if __name__ == "__main__":
    print("## 测试 call_llm")
    prompt = "用几句话概括生命的意义是什么？"
    print(f"## 提示: {prompt}")
    response = call_llm(prompt)
    print(f"## 响应: {response}")