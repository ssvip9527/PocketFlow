---
layout: default
title: "LLM 封装器"
parent: "实用函数"
nav_order: 1
---

# LLM 封装器

可以查看 [litellm](https://github.com/BerriAI/litellm) 等库。
这里，我们提供了一些最小的示例实现：

1. OpenAI
    ```python
    def call_llm(prompt):
        from openai import OpenAI
        client = OpenAI(api_key="YOUR_API_KEY_HERE")
        r = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        return r.choices[0].message.content

    # 示例用法
    call_llm("你好吗？")
    ```
    > 为了安全起见，请将 API 密钥存储在环境变量中，例如 OPENAI_API_KEY。
    {: .best-practice }

2. Claude (Anthropic)
    ```python
    def call_llm(prompt):
        from anthropic import Anthropic
        client = Anthropic(api_key="YOUR_API_KEY_HERE")
        r = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=3000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return r.content[0].text
    ```

3. Google (Generative AI Studio / PaLM API)
    ```python
    def call_llm(prompt):
    from google import genai
    client = genai.Client(api_key='GEMINI_API_KEY')
        response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=prompt
    )
    return response.text
    ```

4. Azure (Azure OpenAI)
    ```python
    def call_llm(prompt):
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint="https://<YOUR_RESOURCE_NAME>.openai.azure.com/",
            api_key="YOUR_API_KEY_HERE",
            api_version="2023-05-15"
        )
        r = client.chat.completions.create(
            model="<YOUR_DEPLOYMENT_NAME>",
            messages=[{"role": "user", "content": prompt}]
        )
        return r.choices[0].message.content
    ```

5. Ollama (本地 LLM)
    ```python
    def call_llm(prompt):
        from ollama import chat
        response = chat(
            model="llama2",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.message.content
    ```
    
6. DeepSeek
    ```python
    def call_llm(prompt):
        from openai import OpenAI
        client = OpenAI(api_key="YOUR_DEEPSEEK_API_KEY", base_url="https://api.deepseek.com")
        r = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        return r.choices[0].message.content
    ```


## 改进
您可以根据需要随意增强 `call_llm` 函数。以下是一些示例：

- 处理聊天历史记录：

```python
def call_llm(messages):
    from openai import OpenAI
    client = OpenAI(api_key="YOUR_API_KEY_HERE")
    r = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )
    return r.choices[0].message.content
```

- 添加内存缓存

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def call_llm(prompt):
    # 您的实现代码
    pass
```

> ⚠️ 缓存与节点重试冲突，因为重试会产生相同的结果。
>
> 为解决此问题，您可以仅在未重试时使用缓存结果。
{: .warning }


```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_call(prompt):
    pass

def call_llm(prompt, use_cache):
    if use_cache:
        return cached_call(prompt)
    # 直接调用底层函数
    return cached_call.__wrapped__(prompt)

class SummarizeNode(Node):
    def exec(self, text):
        return call_llm(f"Summarize: {text}", self.cur_retry==0)
```

- 启用日志记录：

```python
def call_llm(prompt):
    import logging
    logging.info(f"Prompt: {prompt}")
    response = ... # 您的实现代码
    logging.info(f"Response: {response}")
    return response
```

