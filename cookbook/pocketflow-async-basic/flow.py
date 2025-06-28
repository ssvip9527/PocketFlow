"""菜谱查找器的异步流程实现。"""

from pocketflow import AsyncFlow, Node
from nodes import FetchRecipes, SuggestRecipe, GetApproval

class NoOp(Node):
    """什么都不做的节点，用于正确结束流程。"""
    pass

def create_flow():
    """创建并连接节点形成流程。"""
    
    # 创建节点
    fetch = FetchRecipes()
    suggest = SuggestRecipe()
    approve = GetApproval()
    end = NoOp()
    
    # 连接节点
    fetch - "suggest" >> suggest
    suggest - "approve" >> approve
    approve - "retry" >> suggest  # 循环回到另一个建议
    approve - "accept" >> end     # 正确结束流程
    
    # 创建以fetch为起点的流程
    flow = AsyncFlow(start=fetch)
    return flow 