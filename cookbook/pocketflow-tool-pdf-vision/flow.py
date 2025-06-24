from pocketflow import Flow
from nodes import ProcessPDFBatchNode

def create_vision_flow():
    """创建用于使用Vision API批量处理PDF的流程"""
    return Flow(start=ProcessPDFBatchNode())
