from pocketflow import Flow
from nodes import InitDatabaseNode, CreateTaskNode, ListTasksNode

def create_database_flow():
    """创建数据库操作流程"""
    
    # 创建节点
    init_db = InitDatabaseNode()
    create_task = CreateTaskNode()
    list_tasks = ListTasksNode()
    
    # 连接节点
    init_db >> create_task >> list_tasks
    
    # 创建并返回流程
    return Flow(start=init_db)
