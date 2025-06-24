from pocketflow import Node
from tools.embeddings import get_embedding

class EmbeddingNode(Node):
    """用于从OpenAI API获取嵌入的节点"""
    
    def prep(self, shared):
        # 从共享存储中获取文本
        return shared.get("text", "")
        
    def exec(self, text):
        # 使用工具函数获取嵌入
        return get_embedding(text)
        
    def post(self, shared, prep_res, exec_res):
        # 将嵌入存储在共享存储中
        shared["embedding"] = exec_res
        return "default" 