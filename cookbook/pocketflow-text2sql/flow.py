from pocketflow import Flow, Node
from nodes import GetSchema, GenerateSQL, ExecuteSQL, DebugSQL

def create_text_to_sql_flow():
    """创建带有调试循环的文本到SQL工作流。"""
    get_schema_node = GetSchema()
    generate_sql_node = GenerateSQL()
    execute_sql_node = ExecuteSQL()
    debug_sql_node = DebugSQL()

    # 使用默认转换操作符定义主流程序列
    get_schema_node >> generate_sql_node >> execute_sql_node

    # --- 使用正确的操作符定义调试循环连接 ---
    # 如果ExecuteSQL返回"error_retry"，转到DebugSQL
    execute_sql_node - "error_retry" >> debug_sql_node

    # 如果DebugSQL返回"default"，回到ExecuteSQL
    # debug_sql_node - "default" >> execute_sql_node # 明确指定"default"
    # 或者使用默认的简写形式：
    debug_sql_node >> execute_sql_node

    # 创建流程
    text_to_sql_flow = Flow(start=get_schema_node)
    return text_to_sql_flow