from pocketflow import Flow
from nodes import SearchNode, AnalyzeResultsNode

def create_flow() -> Flow:
    """创建并配置搜索流程
    
    返回:
        Flow: 配置好的可运行流程
    """
    # 创建节点
    search = SearchNode()
    analyze = AnalyzeResultsNode()
    
    # 连接节点
    search >> analyze
    
    # 创建从搜索开始的流程
    return Flow(start=search)
