---
layout: default
title: "网络搜索"
parent: "实用函数"
nav_order: 3
---
# 网络搜索

我们推荐一些常用网络搜索工具的实现。

| **API**                         | **免费额度**                                | **定价模式**                                              | **文档**                                                  |
|---------------------------------|-----------------------------------------------|-----------------------------------------------------------------|------------------------------------------------------------------------|
| **Google Custom Search JSON API** | 每天 100 次查询免费       | 每 1000 次查询 5 美元。           | [链接](https://developers.google.com/custom-search/v1/overview)        |
| **Bing Web Search API**         | 每月 1,000 次查询               | 每 1,000 次查询 15-25 美元。 | [链接](https://azure.microsoft.com/en-us/services/cognitive-services/bing-web-search-api/) |
| **DuckDuckGo Instant Answer**   | 完全免费（仅限即时答案，**无 URL**） | 无付费计划；使用无限制，但数据有限             | [链接](https://duckduckgo.com/api)                                     |
| **Brave Search API**         | 每月 2,000 次查询免费 | 基础版每 1k 次查询 3 美元，专业版每 1k 次查询 5 美元 | [链接](https://brave.com/search/api/)                                  |
| **SerpApi**              | 每月 100 次搜索免费            | 5,000 次搜索每月 75 美元起| [链接](https://serpapi.com/)                                             |
| **RapidAPI**           | 许多选项    | 许多选项             | [链接](https://rapidapi.com/search?term=search&sortBy=ByRelevance)      |

## Python 代码示例

### 1. Google 自定义搜索 JSON API
```python
import requests

API_KEY = "YOUR_API_KEY"
CX_ID = "YOUR_CX_ID"
query = "example"

url = "https://www.googleapis.com/customsearch/v1"
params = {
    "key": API_KEY,
    "cx": CX_ID,
    "q": query
}

response = requests.get(url, params=params)
results = response.json()
print(results)
```

### 2. Bing 网络搜索 API
```python
import requests

SUBSCRIPTION_KEY = "YOUR_BING_API_KEY"
query = "example"

url = "https://api.bing.microsoft.com/v7.0/search"
headers = {"Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY}
params = {"q": query}

response = requests.get(url, headers=headers, params=params)
results = response.json()
print(results)
```

### 3. DuckDuckGo 即时答案
```python
import requests

query = "example"
url = "https://api.duckduckgo.com/"
params = {
    "q": query,
    "format": "json"
}

response = requests.get(url, params=params)
results = response.json()
print(results)
```

### 4. Brave 勇敢搜索 API
```python
import requests

SUBSCRIPTION_TOKEN = "YOUR_BRAVE_API_TOKEN"
query = "example"

url = "https://api.search.brave.com/res/v1/web/search"
headers = {
    "X-Subscription-Token": SUBSCRIPTION_TOKEN
}
params = {
    "q": query
}

response = requests.get(url, headers=headers, params=params)
results = response.json()
print(results)
```

### 5. SerpApi
```python
import requests

API_KEY = "YOUR_SERPAPI_KEY"
query = "example"

url = "https://serpapi.com/search"
params = {
    "engine": "google",
    "q": query,
    "api_key": API_KEY
}

response = requests.get(url, params=params)
results = response.json()
print(results)
```


