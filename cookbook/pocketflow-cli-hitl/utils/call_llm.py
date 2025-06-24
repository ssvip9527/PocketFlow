from anthropic import Anthropic
import os

def call_llm(prompt: str) -> str:
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "your-anthropic-api-key")) # 如果未找到密钥，则使用默认值
    response = client.messages.create(
        model="claude-3-haiku-20240307", # 使用较小的模型生成笑话
        max_tokens=150, # 笑话不需要很长
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.content[0].text

if __name__ == "__main__":
    print("正在测试 Anthropic LLM 笑话调用：")
    joke_prompt = "讲一个关于猫的单行笑话。"
    print(f"提示: {joke_prompt}")
    try:
        response = call_llm(joke_prompt)
        print(f"响应: {response}")
    except Exception as e:
        print(f"调用 LLM 时出错: {e}")
        print("请确保您的 ANTHROPIC_API_KEY 环境变量已正确设置。")