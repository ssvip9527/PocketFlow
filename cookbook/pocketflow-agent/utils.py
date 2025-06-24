from openai import OpenAI
import os
from duckduckgo_search import DDGS
import requests

def call_llm(prompt):    
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-api-key"))
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return r.choices[0].message.content

def search_web_duckduckgo(query):
    results = DDGS().text(query, max_results=5)
    # 将结果转换为字符串
    results_str = "\n\n".join([f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}" for r in results])
    return results_str

def search_web_brave(query):

    url = f"https://api.search.brave.com/res/v1/web/search?q={query}"
    api_key = "your brave search api key"

    headers = {
        "accept": "application/json",
        "Accept-Encoding": "gzip",
        "x-subscription-token": api_key
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        results = data['web']['results']
        results_str = "\n\n".join([f"Title: {r['title']}\nURL: {r['url']}\nDescription: {r['description']}" for r in results])     
    else:
        print(f"请求失败，状态码: {response.status_code}")
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