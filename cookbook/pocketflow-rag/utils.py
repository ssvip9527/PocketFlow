import os
import numpy as np
from openai import OpenAI

def call_llm(prompt):    
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

def get_embedding(text):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    
    # 从响应中提取嵌入向量
    embedding = response.data[0].embedding
    
    # 转换为 numpy 数组以与其他嵌入函数保持一致
    return np.array(embedding, dtype=np.float32)

def fixed_size_chunk(text, chunk_size=2000):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i : i + chunk_size])
    return chunks

if __name__ == "__main__":
    print("=== 测试 call_llm ===")
    prompt = "用几句话概括一下生命的意义是什么？"
    print(f"提示: {prompt}")
    response = call_llm(prompt)
    print(f"响应: {response}")

    print("=== 测试嵌入函数 ===")
    
    text1 = "The quick brown fox jumps over the lazy dog."
    text2 = "Python is a popular programming language for data science."
    
    oai_emb1 = get_embedding(text1)
    oai_emb2 = get_embedding(text2)
    print(f"OpenAI 嵌入 1 形状: {oai_emb1.shape}")
    oai_similarity = np.dot(oai_emb1, oai_emb2)
    print(f"文本之间的 OpenAI 相似度: {oai_similarity:.4f}")