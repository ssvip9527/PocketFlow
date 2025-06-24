---
layout: default
title: "向量数据库"
parent: "实用函数"
nav_order: 6
---

# 向量数据库

下面是常用向量搜索解决方案的表格：

| **工具** | **免费额度** | **定价模式** | **文档** |
| --- | --- | --- | --- |
| **FAISS** | 不适用，自托管 | 开源 | [Faiss.ai](https://faiss.ai) |
| **Pinecone** | 2GB 免费 | $25/月起 | [pinecone.io](https://pinecone.io) |
| **Qdrant** | 1GB 免费云 | 按量付费 | [qdrant.tech](https://qdrant.tech) |
| **Weaviate** | 14 天沙盒 | $25/月起 | [weaviate.io](https://weaviate.io) |
| **Milvus** | 5GB 免费云 | 按量付费或 $99/月专用 | [milvus.io](https://milvus.io) |
| **Chroma** | 不适用，自托管 | 免费 (Apache 2.0) | [trychroma.com](https://trychroma.com) |
| **Redis** | 30MB 免费 | $5/月起 | [redis.io](https://redis.io) |

---
## Python 代码示例

以下是每个工具的基本用法片段。

### FAISS
```python
import faiss
import numpy as np

# 嵌入的维度
d = 128

# 创建一个平面 L2 索引
index = faiss.IndexFlatL2(d)

# 随机向量
data = np.random.random((1000, d)).astype('float32')
index.add(data)

# 查询
query = np.random.random((1, d)).astype('float32')
D, I = index.search(query, k=5)

print("距离:", D)
print("邻居:", I)
```

### Pinecone
```python
import pinecone

pinecone.init(api_key="YOUR_API_KEY", environment="YOUR_ENV")

index_name = "my-index"

# 如果索引不存在则创建
if index_name not in pinecone.list_indexes():
    pinecone.create_index(name=index_name, dimension=128)

# 连接
index = pinecone.Index(index_name)

# 插入
vectors = [
    ("id1", [0.1]*128),
    ("id2", [0.2]*128)
]
index.upsert(vectors)

# 查询
response = index.query([[0.15]*128], top_k=3)
print(response)
```

### Qdrant
```python
import qdrant_client
from qdrant_client.models import Distance, VectorParams, PointStruct

client = qdrant_client.QdrantClient(
    url="https://YOUR-QDRANT-CLOUD-ENDPOINT",
    api_key="YOUR_API_KEY"
)

collection = "my_collection"
client.recreate_collection(
    collection_name=collection,
    vectors_config=VectorParams(size=128, distance=Distance.COSINE)
)

points = [
    PointStruct(id=1, vector=[0.1]*128, payload={"type": "doc1"}),
    PointStruct(id=2, vector=[0.2]*128, payload={"type": "doc2"}),
]

client.upsert(collection_name=collection, points=points)

results = client.search(
    collection_name=collection,
    query_vector=[0.15]*128,
    limit=2
)
print(results)
```

### Weaviate
```python
import weaviate

client = weaviate.Client("https://YOUR-WEAVIATE-CLOUD-ENDPOINT")

schema = {
    "classes": [
        {
            "class": "Article",
            "vectorizer": "none"
        }
    ]
}
client.schema.create(schema)

obj = {
    "title": "Hello World",
    "content": "Weaviate vector search"
}
client.data_object.create(obj, "Article", vector=[0.1]*128)

resp = (
    client.query
    .get("Article", ["title", "content"])
    .with_near_vector({"vector": [0.15]*128})
    .with_limit(3)
    .do()
)
print(resp)
```

### Milvus
```python
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection
import numpy as np

connections.connect(alias="default", host="localhost", port="19530")

fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128)
]
schema = CollectionSchema(fields)
collection = Collection("MyCollection", schema)

emb = np.random.rand(10, 128).astype('float32')
ids = list(range(10))
collection.insert([ids, emb])

index_params = {
    "index_type": "IVF_FLAT",
    "params": {"nlist": 128},
    "metric_type": "L2"
}
collection.create_index("embedding", index_params)
collection.load()

query_emb = np.random.rand(1, 128).astype('float32')
results = collection.search(query_emb, "embedding", param={"nprobe": 10}, limit=3)
print(results)
```

### Chroma
```python
import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_data"
))

coll = client.create_collection("my_collection")

vectors = [[0.1, 0.2, 0.3], [0.2, 0.2, 0.2]]
metas = [{"doc": "text1"}, {"doc": "text2"}]
ids = ["id1", "id2"]
coll.add(embeddings=vectors, metadatas=metas, ids=ids)

res = coll.query(query_embeddings=[[0.15, 0.25, 0.3]], n_results=2)
print(res)
```

### Redis
```python
import redis
import struct

r = redis.Redis(host="localhost", port=6379)

# 创建索引
r.execute_command(
    "FT.CREATE", "my_idx", "ON", "HASH",
    "SCHEMA", "embedding", "VECTOR", "FLAT", "6",
    "TYPE", "FLOAT32", "DIM", "128",
    "DISTANCE_METRIC", "L2"
)

# Insert
vec = struct.pack('128f', *[0.1]*128)
r.hset("doc1", mapping={"embedding": vec})

# Search
qvec = struct.pack('128f', *[0.15]*128)
q = "*=>[KNN 3 @embedding $BLOB AS dist]"
res = r.ft("my_idx").search(q, query_params={"BLOB": qvec})
print(res.docs)
```

