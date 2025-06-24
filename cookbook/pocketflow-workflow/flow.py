from pocketflow import Flow
from nodes import GenerateOutline, WriteSimpleContent, ApplyStyle

def create_article_flow():
    """
    创建并配置文章写作工作流
    """
    # 创建节点实例
    outline_node = GenerateOutline()
    write_node = WriteSimpleContent()
    style_node = ApplyStyle()
    
    # 按顺序连接节点
    outline_node >> write_node >> style_node
    
    # 创建从大纲节点开始的流
    article_flow = Flow(start=outline_node)
    
    return article_flow