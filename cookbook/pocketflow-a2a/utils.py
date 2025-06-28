from openai import OpenAI
import os
from duckduckgo_search import DDGS

def call_llm(prompt):    
    # 出于测试目的，请替换为您的实际OpenAI密钥或设置为环境变量
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

def search_web(query):
    results = DDGS().text(query, max_results=5)
    # 将结果转换为字符串
    results_str = "\n\n".join([f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}" for r in results])
    return results_str
    
if __name__ == "__main__":
    print("## 测试call_llm")
    prompt = "In a few words, what is the meaning of life?"
    print(f"## 提示: {prompt}")
    response = call_llm(prompt)
    print(f"## 响应: {response}")

    print("## 测试search_web")
    query = "Who won the Nobel Prize in Physics 2024?"
    print(f"## 查询: {query}")
    results = search_web(query)
    print(f"## 结果: {results}")