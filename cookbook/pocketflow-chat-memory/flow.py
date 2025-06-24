from pocketflow import Flow
from nodes import GetUserQuestionNode, RetrieveNode, AnswerNode, EmbedNode

def create_chat_flow():
    # 创建节点
    question_node = GetUserQuestionNode()
    retrieve_node = RetrieveNode()
    answer_node = AnswerNode()
    embed_node = EmbedNode()
    
    # 连接流程：
    # 1. 从获取问题开始
    # 2. 检索相关对话
    # 3. 生成答案
    # 4. 可选地嵌入旧对话
    # 5. 循环回到获取下一个问题

    # 主流程路径
    question_node - "retrieve" >> retrieve_node
    retrieve_node - "answer" >> answer_node
    
    # 当我们需要嵌入旧对话时
    answer_node - "embed" >> embed_node
    
    # 循环回到下一个问题
    answer_node - "question" >> question_node
    embed_node - "question" >> question_node
    
    # 创建从问题节点开始的流程
    return Flow(start=question_node)

# 初始化流程
chat_flow = create_chat_flow()