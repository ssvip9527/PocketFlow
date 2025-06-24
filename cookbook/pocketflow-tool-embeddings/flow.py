from pocketflow import Flow
from nodes import EmbeddingNode

def create_embedding_flow():
    """创建文本嵌入的流程"""
    # 创建嵌入节点
    embedding = EmbeddingNode()
    
    # 创建并返回流程
    return Flow(start=embedding)