from pocketflow import Flow
from nodes import ChainOfThoughtNode

def create_chain_of_thought_flow():
    # 创建一个 ChainOfThoughtNode
    cot_node = ChainOfThoughtNode(max_retries=3, wait=10)
    
    # 将节点连接到自身以实现“继续”操作
    cot_node - "continue" >> cot_node
    
    # 创建流程
    cot_flow = Flow(start=cot_node)
    return cot_flow