from pocketflow import Flow, BatchFlow
from nodes import LoadImage, ApplyFilter, SaveImage

def create_base_flow():
    """创建用于处理单个图像的基础流程。"""
    # 创建节点
    load = LoadImage()
    filter_node = ApplyFilter()
    save = SaveImage()
    
    # 连接节点
    load - "apply_filter" >> filter_node
    filter_node - "save" >> save
    
    # 创建并返回流程
    return Flow(start=load)

class ImageBatchFlow(BatchFlow):
    """用于处理具有不同过滤器的多个图像的 BatchFlow。"""
    
    def prep(self, shared):
        """为每个图像-过滤器组合生成参数。"""
        # 要处理的图像列表
        images = ["cat.jpg", "dog.jpg", "bird.jpg"]
        
        # 要应用的过滤器列表
        filters = ["grayscale", "blur", "sepia"]
        
        # 生成所有组合
        params = []
        for img in images:
            for f in filters:
                params.append({
                    "input": img,
                    "filter": f
                })
        
        return params

def create_flow():
    """创建完整的批处理流程。"""
    # 创建用于单个图像处理的基础流程
    base_flow = create_base_flow()
    
    # 包装在 BatchFlow 中以处理多个图像
    batch_flow = ImageBatchFlow(start=base_flow)
    
    return batch_flow 