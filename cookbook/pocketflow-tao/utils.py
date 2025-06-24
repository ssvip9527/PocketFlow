# utils.py

from openai import OpenAI
import os

def call_llm(prompt):    
    # 调用大型语言模型 (LLM) 生成响应
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "Your Key Here"),base_url=os.environ.get("OPENAI_API_BASE", "Your API Base Here"))
    r = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "openai/gpt-4.1-nano"),
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

if __name__ == "__main__":
    print("## 测试 call_llm")
    prompt = "用几句话概括生命的意义是什么？"
    print(f"## 提示: {prompt}")
    response = call_llm(prompt)
    print(f"## 响应: {response}")