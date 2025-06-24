from openai import OpenAI
import os

def call_llm(messages):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.7
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    # 测试 LLM 调用
    messages = [{"role": "user", "content": "用几个词概括生命的意义是什么？"}]
    response = call_llm(messages)
    print(f"提示: {messages[0]['content']}")
    print(f"响应: {response}")
