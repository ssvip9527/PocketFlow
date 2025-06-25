import os
import asyncio
from anthropic import AsyncAnthropic

# Async version of the simple wrapper, using Anthropic
# 使用Anthropic的异步简单封装版本
async def call_llm(prompt):
    """Anthropic API调用的异步封装。"""
    client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", "your-api-key"))
    response = await client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=20000,
        thinking={
            "type": "enabled",
            "budget_tokens": 16000
        },
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    return response.content[1].text

if __name__ == "__main__":
    async def run_test():
        print("## 正在测试使用Anthropic的异步call_llm")
        prompt = "用几个词概括生命的意义是什么？"
        print(f"## 提示: {prompt}")
        response = await call_llm(prompt)
        print(f"## 响应: {response}")

    asyncio.run(run_test())