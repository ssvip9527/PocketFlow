from openai import OpenAI
import os

# 初始化 OpenAI 客户端
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def call_llm(prompt: str) -> str:
    """调用 OpenAI API 分析文本
    
    参数:
        prompt (str): 模型的输入提示
        
    返回:
        str: 模型响应
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"调用 LLM API 时出错: {str(e)}")
        return ""

if __name__ == "__main__":
    # 测试 LLM 调用
    response = call_llm("What is web crawling?")
    print("响应:", response)
