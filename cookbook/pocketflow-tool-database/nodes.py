from pocketflow import Node
from tools.database import execute_sql, init_db

class InitDatabaseNode(Node):
    """用于初始化数据库的节点"""
    
    def exec(self, _):
        init_db()
        return "数据库已初始化"
        
    def post(self, shared, prep_res, exec_res):
        shared["db_status"] = exec_res
        return "default"

class CreateTaskNode(Node):
    """用于创建新任务的节点"""
    
    def prep(self, shared):
        return (
            shared.get("task_title", ""),
            shared.get("task_description", "")
        )
        
    def exec(self, inputs):
        title, description = inputs
        query = "INSERT INTO tasks (title, description) VALUES (?, ?)"
        execute_sql(query, (title, description))
        return "任务创建成功"
        
    def post(self, shared, prep_res, exec_res):
        shared["task_status"] = exec_res
        return "default"

class ListTasksNode(Node):
    """用于列出所有任务的节点"""
    
    def exec(self, _):
        query = "SELECT * FROM tasks"
        return execute_sql(query)
        
    def post(self, shared, prep_res, exec_res):
        shared["tasks"] = exec_res
        return "default"
