from pocketflow import Flow
from nodes import DecideAction, SearchWeb, UnreliableAnswerNode, SupervisorNode

def create_agent_inner_flow():
    """
    创建不带监督的内部研究代理流。
    
    此流程处理研究周期：
    1. DecideAction 节点决定是搜索还是回答
    2. 如果是搜索，则转到 SearchWeb 节点并返回决定
    3. 如果是回答，则转到 UnreliableAnswerNode
    
    Returns:
        Flow: 一个研究代理流
    """
    # 创建每个节点的实例
    decide = DecideAction()
    search = SearchWeb()
    answer = UnreliableAnswerNode()
    
    # 连接节点
    # 如果 DecideAction 返回 "search"，则转到 SearchWeb
    decide - "search" >> search
    
    # 如果 DecideAction 返回 "answer"，则转到 UnreliableAnswerNode
    decide - "answer" >> answer
    
    # SearchWeb 完成并返回 "decide" 后，返回 DecideAction
    search - "decide" >> decide
    
    # 创建并返回内部流，从 DecideAction 节点开始
    return Flow(start=decide)

def create_agent_flow():
    """
    通过将整个代理流视为一个节点并将监督器放置在它之外来创建受监督的代理流。
    
    该流程的工作方式如下：
    1. 内部代理流进行研究并生成答案
    2. SupervisorNode 检查答案是否有效
    3. 如果答案有效，流程完成
    4. 如果答案无效，重新启动内部代理流
    
    Returns:
        Flow: 一个完整的带监督的研究代理流
    """
    # 创建内部流
    agent_flow = create_agent_inner_flow()
    
    # 创建监督节点
    supervisor = SupervisorNode()
    
    # 连接组件
    # agent_flow 完成后，转到监督器
    agent_flow >> supervisor
    
    # 如果监督器拒绝答案，返回 agent_flow
    supervisor - "retry" >> agent_flow
    
    # 创建并返回外部流，从 agent_flow 开始
    return Flow(start=agent_flow)