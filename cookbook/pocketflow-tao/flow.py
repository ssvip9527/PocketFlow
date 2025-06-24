# flow.py

from pocketflow import Flow
from nodes import ThinkNode, ActionNode, ObserveNode, EndNode

def create_tao_flow():
    """
    创建一个思维-行动-观察循环流
    
    流的工作原理：
    1. ThinkNode决定下一步行动
    2. ActionNode执行行动
    3. ObserveNode观察行动结果
    4. 返回到ThinkNode继续思考，或结束流
    
    返回：
        Flow: 完整的TAO循环流
    """
    # 创建节点实例
    think = ThinkNode()
    action = ActionNode()
    observe = ObserveNode()
    end = EndNode()
    
    # 连接节点
    # 如果ThinkNode返回"action"，则转到ActionNode
    think - "action" >> action
    
    # 如果ThinkNode返回"end"，则结束流
    think - "end" >> end
    
    # 在ActionNode完成后，转到ObserveNode
    action - "observe" >> observe
    
    # 在ObserveNode完成后，返回到ThinkNode
    observe - "think" >> think
    
    # 创建并返回流，从ThinkNode开始
    return Flow(start=think)