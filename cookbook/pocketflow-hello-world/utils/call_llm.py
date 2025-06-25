from openai import OpenAI

def call_llm(prompt):    
    # 初始化 OpenAI 客户端，使用提供的 API 密钥
    client = OpenAI(api_key="YOUR_API_KEY_HERE")
    # 创建聊天补全请求
    r = client.chat.completions.create(
        model="gpt-4o",  # 指定使用的模型
        messages=[{"role": "user", "content": prompt}]  # 用户消息
    )
    # 返回 LLM 的响应内容
    return r.choices[0].message.content
    
if __name__ == "__main__":
    # 定义一个测试提示
    prompt = "生命的意义是什么？"
    # 调用 LLM 并打印响应
    print(call_llm(prompt))