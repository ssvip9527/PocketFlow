from pocketflow import Flow
from nodes import DecideAction, SearchWeb, AnswerQuestion

def create_agent_flow():
    """
    创建并连接节点以形成完整的代理流程。
    
    流程如下：
    1. DecideAction 节点决定是搜索还是回答
    2. 如果是搜索，则转到 SearchWeb 节点
    3. 如果是回答，则转到 AnswerQuestion 节点
    4. SearchWeb 完成后，返回 DecideAction
    
    返回：
        Flow: 一个完整的研究代理流程
    """
    # 创建每个节点的实例
    decide = DecideAction()
    search = SearchWeb()
    answer = AnswerQuestion()
    
    # 连接节点
    # 如果 DecideAction 返回 "search"，则转到 SearchWeb
    decide - "search" >> search
    
    # 如果 DecideAction 返回 "answer"，则转到 AnswerQuestion
    decide - "answer" >> answer
    
    # SearchWeb 完成并返回 "decide" 后，返回 DecideAction
    search - "decide" >> decide
    
    # 创建并返回流程，从 DecideAction 节点开始
    return Flow(start=decide)