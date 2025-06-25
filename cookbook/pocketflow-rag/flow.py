from pocketflow import Flow
from nodes import EmbedDocumentsNode, CreateIndexNode, EmbedQueryNode, RetrieveDocumentNode, ChunkDocumentsNode, GenerateAnswerNode

def get_offline_flow():
    # 创建用于文档索引的离线流
    chunk_docs_node = ChunkDocumentsNode()
    embed_docs_node = EmbedDocumentsNode()
    create_index_node = CreateIndexNode()
    
    # 连接节点
    chunk_docs_node >> embed_docs_node >> create_index_node
    
    offline_flow = Flow(start=chunk_docs_node)
    return offline_flow

def get_online_flow():
    # 创建用于文档检索和答案生成的在线流
    embed_query_node = EmbedQueryNode()
    retrieve_doc_node = RetrieveDocumentNode()
    generate_answer_node = GenerateAnswerNode()
    
    # 连接节点
    embed_query_node >> retrieve_doc_node >> generate_answer_node
    
    online_flow = Flow(start=embed_query_node)
    return online_flow

# 初始化流
offline_flow = get_offline_flow()
online_flow = get_online_flow()