from openai import OpenAI
import os

def stream_llm(prompt):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))

    # 发送流式聊天补全请求
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        stream=True  # 启用流式传输
    )
    return response

def fake_stream_llm(prompt, predefined_text="这是一个虚假响应。今天是个晴天。阳光普照。鸟儿歌唱。花儿绽放。蜜蜂嗡嗡。风儿吹拂。云儿飘荡。天空湛蓝。草地翠绿。树木高耸。水流清澈。鱼儿畅游。阳光普照。鸟儿歌唱。花儿绽放。蜜蜂嗡嗡。风儿吹拂。云儿飘荡。天空湛蓝。草地翠绿。树木高耸。水流清澈。鱼儿畅游。"):
    """
    返回一个简单对象列表，模仿 OpenAI 流式响应所需的结构。
    """
    # 将文本分割成小块
    chunk_size = 10
    chunks = []
    
    # 使用一个简单的类在嵌套结构之外创建块
    class SimpleObject:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    # 构建块
    for i in range(0, len(predefined_text), chunk_size):
        text_chunk = predefined_text[i:i+chunk_size]
        
        # 使用简单对象创建嵌套结构
        delta = SimpleObject(content=text_chunk)
        choice = SimpleObject(delta=delta)
        chunk = SimpleObject(choices=[choice])
        
        chunks.append(chunk)
    
    return chunks

if __name__ == "__main__":
    print("## 测试流式 LLM")
    prompt = "生命的意义是什么？"
    print(f"## 提示: {prompt}")
    # response = fake_stream_llm(prompt)
    response = stream_llm(prompt)
    print(f"## 响应: ")
    for chunk in response:
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
            chunk_content = chunk.choices[0].delta.content
            # 打印传入的文本，不带换行符（模拟实时流式传输）
            print(chunk_content, end="", flush=True)

