from pocketflow import Flow
from nodes import DecideAction, SearchWeb, AnswerQuestion

def create_agent_flow():
    """
    创建并连接节点以形成完整的代理流。
    
    流程如下：
    1. DecideAction节点决定是搜索还是回答
    2. 如果是搜索，则转到SearchWeb节点
    3. 如果是回答，则转到AnswerQuestion节点
    4. SearchWeb完成后，返回DecideAction
    
    返回：
        Flow: 一个完整的研究代理流
    """
    # 创建每个节点的实例
    decide = DecideAction()
    search = SearchWeb()
    answer = AnswerQuestion()
    
    # 连接节点
    # 如果DecideAction返回“search”，则转到SearchWeb
    decide - "search" >> search
    
    # 如果DecideAction返回“answer”，则转到AnswerQuestion
    decide - "answer" >> answer
    
    # SearchWeb完成后并返回“decide”，则返回DecideAction
    search - "decide" >> decide
    
    # 创建并返回流程，从DecideAction节点开始
    return Flow(start=decide)