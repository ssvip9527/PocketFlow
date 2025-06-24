"""通信示例的流程配置。"""

from pocketflow import Flow
from nodes import TextInput, WordCounter, ShowStats, EndNode

def create_flow():
    """创建并配置包含所有节点的流程。"""
    # 创建节点
    text_input = TextInput()
    word_counter = WordCounter()
    show_stats = ShowStats()
    end_node = EndNode()
    
    # 配置转换
    text_input - "count" >> word_counter
    word_counter - "show" >> show_stats
    show_stats - "continue" >> text_input
    text_input - "exit" >> end_node
    
    # 创建并返回流程
    return Flow(start=text_input)