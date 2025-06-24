import sqlite3
from typing import List, Tuple, Any

def execute_sql(query: str, params: Tuple = None) -> List[Tuple[Any, ...]]:
    """执行 SQL 查询并返回结果
    
    Args:
        query (str): 要执行的 SQL 查询
        params (tuple, optional): 用于防止 SQL 注入的查询参数
        
    Returns:
        list: 查询结果，以元组列表形式返回
    """
    conn = sqlite3.connect("example.db")
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()
        return result
    finally:
        conn.close()

def init_db():
    """使用示例表初始化数据库"""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    execute_sql(create_table_sql)
