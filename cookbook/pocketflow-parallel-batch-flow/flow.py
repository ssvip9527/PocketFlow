"""并行图像处理的流定义。"""

from pocketflow import AsyncParallelBatchFlow, AsyncBatchFlow
from nodes import LoadImage, ApplyFilter, SaveImage

def create_base_flow():
    """创建用于处理单个图像和单个过滤器的流。"""
    # 创建节点
    load = LoadImage()
    apply_filter = ApplyFilter()
    save = SaveImage()
    
    # 连接节点
    load - "apply_filter" >> apply_filter
    apply_filter - "save" >> save
    
    # 创建流
    return load

class ImageBatchFlow(AsyncBatchFlow):
    """批量处理多个图像和多个过滤器的流。"""
    
    async def prep_async(self, shared):
        """为每个图像-过滤器组合生成参数。"""
        # 获取图像和过滤器列表
        images = shared.get("images", [])
        filters = ["grayscale", "blur", "sepia"]
        
        # 创建参数组合
        params = []
        for image_path in images:
            for filter_type in filters:
                params.append({
                    "image_path": image_path,
                    "filter": filter_type
                })
        
        print(f"Processing {len(images)} images with {len(filters)} filters...")
        print(f"Total combinations: {len(params)}")
        return params

class ImageParallelBatchFlow(AsyncParallelBatchFlow):
    """并行处理多个图像和多个过滤器的流。"""

    async def prep_async(self, shared):
        """为每个图像-过滤器组合生成参数。"""
        # 获取图像和过滤器列表
        images = shared.get("images", [])
        filters = ["grayscale", "blur", "sepia"]
        
        # 创建参数组合
        params = []
        for image_path in images:
            for filter_type in filters:
                params.append({
                    "image_path": image_path,
                    "filter": filter_type
                })
        
        print(f"Processing {len(images)} images with {len(filters)} filters...")
        print(f"Total combinations: {len(params)}")
        return params

def create_flows():
    """创建完整的并行处理流。"""
    # 创建用于单个图像处理的基础流
    base_flow = create_base_flow()
    
    # 包装在并行批处理流中
    return ImageBatchFlow(start=base_flow), ImageParallelBatchFlow(start=base_flow)