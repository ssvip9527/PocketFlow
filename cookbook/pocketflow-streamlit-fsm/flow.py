from pocketflow import Flow
from nodes import GenerateImageNode

def create_generation_flow():
    """创建用于图像生成（初始或重新生成）的流程。"""
    generate_image_node = GenerateImageNode()
    return Flow(start=generate_image_node)


