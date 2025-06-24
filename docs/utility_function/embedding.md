---
layout: default
title: "嵌入"
parent: "实用函数"
nav_order: 5
---

# 嵌入

下面是各种文本嵌入 API 的概述表，以及 Python 代码示例。

> 嵌入与流程设计相比，更多是一种微观优化。
> 
> 建议从最方便的开始，之后再进行优化。
{: .best-practice }


| **API** | **免费额度** | **定价模式** | **文档** |
| --- | --- | --- | --- |
| **OpenAI** | 约 $5 信用额度 | 约 $0.0001/1K tokens | [OpenAI 嵌入](https://platform.openai.com/docs/api-reference/embeddings) |
| **Azure OpenAI** | $200 信用额度 | 与 OpenAI 相同（约 $0.0001/1K tokens） | [Azure OpenAI 嵌入](https://learn.microsoft.com/zh-cn/azure/cognitive-services/openai/how-to/create-resource?tabs=portal) |
| **Google Vertex AI** | $300 信用额度 | 约 $0.025 / 百万字符 | [Vertex AI 嵌入](https://cloud.google.com/vertex-ai/docs/generative-ai/embeddings/get-text-embeddings) |
| **AWS Bedrock** | 无免费额度，但可能适用 AWS 积分 | 约 $0.00002/1K tokens (Titan V2) | [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/) |
| **Cohere** | 有限免费额度 | 约 $0.0001/1K tokens | [Cohere 嵌入](https://docs.cohere.com/docs/cohere-embed) |
| **Hugging Face** | 每月约 $0.10 免费计算 | 按计算秒数付费 | [HF 推理 API](https://huggingface.co/docs/api-inference) |
| **Jina** | 1M tokens 免费 | 之后按 token 付费 | [Jina 嵌入](https://jina.ai/embeddings/) |

## Python 代码示例

### 1. OpenAI
```python
from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")
response = client.embeddings.create(
    model="text-embedding-ada-002",
    input=text
)
    
# 从响应中提取嵌入向量
embedding = response.data[0].embedding
embedding = np.array(embedding, dtype=np.float32)
print(embedding)
```

### 2. Azure OpenAI
```python
import openai

openai.api_type = "azure"
openai.api_base = "https://YOUR_RESOURCE_NAME.openai.azure.com"
openai.api_version = "2023-03-15-preview"
openai.api_key = "YOUR_AZURE_API_KEY"

resp = openai.Embedding.create(engine="ada-embedding", input="Hello world")
vec = resp["data"][0]["embedding"]
print(vec)
```

### 3. Google Vertex AI
```python
from vertexai.preview.language_models import TextEmbeddingModel
import vertexai

vertexai.init(project="YOUR_GCP_PROJECT_ID", location="us-central1")
model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")

emb = model.get_embeddings(["Hello world"])
print(emb[0])
```

### 4. AWS Bedrock
```python
import boto3, json

client = boto3.client("bedrock-runtime", region_name="us-east-1")
body = {"inputText": "Hello world"}
resp = client.invoke_model(modelId="amazon.titan-embed-text-v2:0", contentType="application/json", body=json.dumps(body))
resp_body = json.loads(resp["body"].read())
vec = resp_body["embedding"]
print(vec)
```

### 5. Cohere
```python
import cohere

co = cohere.Client("YOUR_API_KEY")
resp = co.embed(texts=["Hello world"])
vec = resp.embeddings[0]
print(vec)
```

### 6. Hugging Face
```python
import requests

API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
HEADERS = {"Authorization": "Bearer YOUR_HF_TOKEN"}

res = requests.post(API_URL, headers=HEADERS, json={"inputs": "Hello world"})
vec = res.json()[0]
print(vec)
```

### 7. Jina
```python
import requests

url = "https://api.jina.ai/v2/embed"
headers = {"Authorization": "Bearer YOUR_JINA_TOKEN"}
payload = {"data": ["Hello world"], "model": "jina-embeddings-v3"}
res = requests.post(url, headers=headers, json=payload)
vec = res.json()["data"][0]["embedding"]
print(vec)
```

