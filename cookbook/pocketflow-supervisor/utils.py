from openai import OpenAI
import os
from duckduckgo_search import DDGS

def call_llm(prompt):
    # 从环境变量中获取 OpenAI API 密钥，如果未设置则使用默认值
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    # 调用 OpenAI API 创建聊天完成
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    # 返回 LLM 的响应内容
    return r.choices[0].message.content

def search_web(query):
    # 使用 DuckDuckGo Search 搜索网络，最多返回 5 个结果
    results = DDGS().text(query, max_results=5)
    # 将搜索结果转换为字符串格式
    results_str = "\n\n".join([f"标题: {r['title']}\nURL: {r['href']}\n摘要: {r['body']}" for r in results])
    return results_str
    
if __name__ == "__main__":
    print("## 测试 call_llm")
    prompt = "用几句话概括，生命的意义是什么？"
    print(f"## 提示: {prompt}")
    response = call_llm(prompt)
    print(f"## 响应: {response}")

    print("## 测试 search_web")
    query = "谁获得了2024年诺贝尔物理学奖？"
    print(f"## 查询: {query}")
    results = search_web(query)
    print(f"## 结果: {results}")