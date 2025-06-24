---
layout: default
title: "RAG"
parent: "设计模式"
nav_order: 3
---

# RAG (检索增强生成)

对于某些 LLM 任务，例如回答问题，提供相关上下文至关重要。一种常见的架构是 **两阶段** RAG 管道：

<div align="center">
  <img src="https://github.com/the-pocket/.github/raw/main/assets/rag.png?raw=true" width="400"/>
</div>

1. **离线阶段**：预处理和索引文档（“构建索引”）。
2. **在线阶段**：给定一个问题，通过检索最相关的上下文来生成答案。

---
## 阶段 1：离线索引

我们创建三个节点：
1. `ChunkDocs` – [分块](../utility_function/chunking.md) 原始文本。
2. `EmbedDocs` – [嵌入](../utility_function/embedding.md) 每个分块。
3. `StoreIndex` – 将嵌入存储到 [向量数据库](../utility_function/vector.md) 中。

```python
class ChunkDocs(BatchNode):
    def prep(self, shared):
        # shared["files"] 中的文件路径列表。我们处理每个文件。
        return shared["files"]

    def exec(self, filepath):
        # 读取文件内容。在实际使用中，进行错误处理。
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        # 每 100 个字符分块
        chunks = []
        size = 100
        for i in range(0, len(text), size):
            chunks.append(text[i : i + size])
        return chunks
    
    def post(self, shared, prep_res, exec_res_list):
        # exec_res_list 是分块列表的列表，每个文件一个。
        # 将它们全部展平为单个分块列表。
        all_chunks = []
        for chunk_list in exec_res_list:
            all_chunks.extend(chunk_list)
        shared["all_chunks"] = all_chunks

class EmbedDocs(BatchNode):
    def prep(self, shared):
        return shared["all_chunks"]

    def exec(self, chunk):
        return get_embedding(chunk)

    def post(self, shared, prep_res, exec_res_list):
        # 存储嵌入列表。
        shared["all_embeds"] = exec_res_list
        print(f"总嵌入数：{len(exec_res_list)}")

class StoreIndex(Node):
    def prep(self, shared):
        # 我们将从 shared 中读取所有嵌入。
        return shared["all_embeds"]

    def exec(self, all_embeds):
        # 创建向量索引（实际使用中可以是 faiss 或其他数据库）。
        index = create_index(all_embeds)
        return index

    def post(self, shared, prep_res, index):
        shared["index"] = index

# 按顺序连接它们
chunk_node = ChunkDocs()
embed_node = EmbedDocs()
store_node = StoreIndex()

chunk_node >> embed_node >> store_node

OfflineFlow = Flow(start=chunk_node)
```

使用示例：

```python
shared = {
    "files": ["doc1.txt", "doc2.txt"],  # 任何文本文件
}
OfflineFlow.run(shared)
```

---
## 阶段 2：在线查询与回答

我们有 3 个节点：
1. `EmbedQuery` – 嵌入用户的查询。
2. `RetrieveDocs` – 从索引中检索最佳分块。
3. `GenerateAnswer` – 使用问题 + 分块调用 LLM 以生成最终答案。

```python
class EmbedQuery(Node):
    def prep(self, shared):
        return shared["question"]

    def exec(self, question):
        return get_embedding(question)

    def post(self, shared, prep_res, q_emb):
        shared["q_emb"] = q_emb

class RetrieveDocs(Node):
    def prep(self, shared):
        # 我们需要查询嵌入，以及离线索引/分块
        return shared["q_emb"], shared["index"], shared["all_chunks"]

    def exec(self, inputs):
        q_emb, index, chunks = inputs
        I, D = search_index(index, q_emb, top_k=1)
        best_id = I[0][0]
        relevant_chunk = chunks[best_id]
        return relevant_chunk

    def post(self, shared, prep_res, relevant_chunk):
        shared["retrieved_chunk"] = relevant_chunk
        print("检索到的分块：", relevant_chunk[:60], "...")

class GenerateAnswer(Node):
    def prep(self, shared):
        return shared["question"], shared["retrieved_chunk"]

    def exec(self, inputs):
        question, chunk = inputs
        prompt = f"问题：{question}\n上下文：{chunk}\n答案："
        return call_llm(prompt)

    def post(self, shared, prep_res, answer):
        shared["answer"] = answer
        print("答案：", answer)

embed_qnode = EmbedQuery()
retrieve_node = RetrieveDocs()
generate_node = GenerateAnswer()

embed_qnode >> retrieve_node >> generate_node
OnlineFlow = Flow(start=embed_qnode)
```

使用示例：

```python
# 假设我们已经运行了 OfflineFlow 并拥有：
# shared["all_chunks"], shared["index"] 等。
shared["question"] = "为什么人们喜欢猫？"

OnlineFlow.run(shared)
# 最终答案在 shared["answer"] 中
```