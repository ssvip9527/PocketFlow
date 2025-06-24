import os
import numpy as np
from openai import OpenAI

def get_embedding(text):
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "YOUR_API_KEY"))
    
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    
    # 从响应中提取嵌入向量
    embedding = response.data[0].embedding
    
    # 转换为 numpy 数组，以与其他嵌入函数保持一致
    return np.array(embedding, dtype=np.float32)


if __name__ == "__main__":
    # 测试嵌入函数
    text1 = "敏捷的棕色狐狸跳过懒狗。"
    text2 = "Python 是一种流行的数据科学编程语言。"
    
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    
    print(f"嵌入 1 形状: {emb1.shape}")
    print(f"嵌入 2 形状: {emb2.shape}")
    
    # 计算相似度（点积）
    similarity = np.dot(emb1, emb2)
    print(f"文本之间的相似度: {similarity:.4f}")