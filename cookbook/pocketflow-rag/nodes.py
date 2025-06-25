from pocketflow import Node, Flow, BatchNode
import numpy as np
import faiss
from utils import call_llm, get_embedding, fixed_size_chunk

# 离线流的节点
class ChunkDocumentsNode(BatchNode):
    def prep(self, shared):
        """从共享存储中读取文本"""
        return shared["texts"]
    
    def exec(self, text):
        """将单个文本分块成更小的片段"""
        return fixed_size_chunk(text)
    
    def post(self, shared, prep_res, exec_res_list):
        """将分块的文本存储在共享存储中"""
        # 将列表的列表展平为单个块列表
        all_chunks = []
        for chunks in exec_res_list:
            all_chunks.extend(chunks)
        
        # 用扁平的块列表替换原始文本
        shared["texts"] = all_chunks
        
        print(f"✅ 从 {len(prep_res)} 个文档创建了 {len(all_chunks)} 个块")
        return "default"
    
class EmbedDocumentsNode(BatchNode):
    def prep(self, shared):
        """从共享存储中读取文本并作为可迭代对象返回"""
        return shared["texts"]
    
    def exec(self, text):
        """嵌入单个文本"""
        return get_embedding(text)
    
    def post(self, shared, prep_res, exec_res_list):
        """将嵌入存储在共享存储中"""
        embeddings = np.array(exec_res_list, dtype=np.float32)
        shared["embeddings"] = embeddings
        print(f"✅ 创建了 {len(embeddings)} 个文档嵌入")
        return "default"

class CreateIndexNode(Node):
    def prep(self, shared):
        """从共享存储中获取嵌入"""
        return shared["embeddings"]
    
    def exec(self, embeddings):
        """创建 FAISS 索引并添加嵌入"""
        print("🔍 正在创建搜索索引...")
        dimension = embeddings.shape[1]
        
        # 创建一个平面 L2 索引
        index = faiss.IndexFlatL2(dimension)
        
        # 将嵌入添加到索引中
        index.add(embeddings)
        
        return index
    
    def post(self, shared, prep_res, exec_res):
        """将索引存储在共享存储中"""
        shared["index"] = exec_res
        print(f"✅ 索引已创建，包含 {exec_res.ntotal} 个向量")
        return "default"

# 在线流的节点
class EmbedQueryNode(Node):
    def prep(self, shared):
        """从共享存储中获取查询"""
        return shared["query"]
    
    def exec(self, query):
        """嵌入查询"""
        print(f"🔍 正在嵌入查询: {query}")
        query_embedding = get_embedding(query)
        return np.array([query_embedding], dtype=np.float32)
    
    def post(self, shared, prep_res, exec_res):
        """将查询嵌入存储在共享存储中"""
        shared["query_embedding"] = exec_res
        return "default"

class RetrieveDocumentNode(Node):
    def prep(self, shared):
        """从共享存储中获取查询嵌入、索引和文本"""
        return shared["query_embedding"], shared["index"], shared["texts"]
    
    def exec(self, inputs):
        """在索引中搜索相似文档"""
        print("🔎 正在搜索相关文档...")
        query_embedding, index, texts = inputs
        
        # 搜索最相似的文档
        distances, indices = index.search(query_embedding, k=1)
        
        # 获取最相似文档的索引
        best_idx = indices[0][0]
        distance = distances[0][0]
        
        # 获取相应的文本
        most_relevant_text = texts[best_idx]
        
        return {
            "text": most_relevant_text,
            "index": best_idx,
            "distance": distance
        }
    
    def post(self, shared, prep_res, exec_res):
        """将检索到的文档存储在共享存储中"""
        shared["retrieved_document"] = exec_res
        print(f"📄 已检索文档 (索引: {exec_res['index']}, 距离: {exec_res['distance']:.4f})")
        print(f"📄 最相关文本: \"{exec_res['text']}\"")
        return "default"
    
class GenerateAnswerNode(Node):
    def prep(self, shared):
        """获取查询、检索到的文档和任何其他所需上下文"""
        return shared["query"], shared["retrieved_document"]
    
    def exec(self, inputs):
        """使用 LLM 生成答案"""
        query, retrieved_doc = inputs
        
        prompt = f"""
根据提供的上下文简要回答以下问题:
问题: {query}
上下文: {retrieved_doc['text']}
答案:
"""
        
        answer = call_llm(prompt)
        return answer
    
    def post(self, shared, prep_res, exec_res):
        """将生成的答案存储在共享存储中"""
        shared["generated_answer"] = exec_res
        print("\n🤖 生成的答案:")
        print(exec_res)
        return "default"
