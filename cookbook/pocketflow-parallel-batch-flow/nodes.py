"""用于图像处理的 AsyncNode 实现。"""
import os
import asyncio
from PIL import Image, ImageFilter
import numpy as np
from pocketflow import AsyncNode

class LoadImage(AsyncNode):
    """从文件加载图像的节点。"""
    async def prep_async(self, shared):
        """从参数中获取图像路径。"""
        image_path = self.params["image_path"]
        print(f"正在加载图像：{image_path}")
        return image_path
    
    async def exec_async(self, image_path):
        """使用 PIL 加载图像。"""
        # 模拟 I/O 延迟
        await asyncio.sleep(0.5)
        return Image.open(image_path)
    
    async def post_async(self, shared, prep_res, exec_res):
        """将图像存储在共享存储中。"""
        shared["image"] = exec_res
        return "apply_filter"

class ApplyFilter(AsyncNode):
    """对图像应用过滤器的节点。"""
    async def prep_async(self, shared):
        """获取图像和过滤器类型。"""
        image = shared["image"]
        filter_type = self.params["filter"]
        print(f"正在应用 {filter_type} 过滤器...")
        return image, filter_type
    
    async def exec_async(self, inputs):
        """应用指定的过滤器。"""
        image, filter_type = inputs
        
        # 模拟处理延迟
        await asyncio.sleep(0.5)
        
        if filter_type == "grayscale":
            return image.convert("L")
        elif filter_type == "blur":
            return image.filter(ImageFilter.BLUR)
        elif filter_type == "sepia":
            # 转换为数组进行棕褐色计算
            img_array = np.array(image)
            sepia_matrix = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])
            sepia_array = img_array.dot(sepia_matrix.T)
            sepia_array = np.clip(sepia_array, 0, 255).astype(np.uint8)
            return Image.fromarray(sepia_array)
        else:
            raise ValueError(f"未知过滤器：{filter_type}")
    
    async def post_async(self, shared, prep_res, exec_res):
        """存储过滤后的图像。"""
        shared["filtered_image"] = exec_res
        return "save"

class SaveImage(AsyncNode):
    """保存处理后的图像的节点。"""
    async def prep_async(self, shared):
        """准备输出路径。"""
        image = shared["filtered_image"]
        base_name = os.path.splitext(os.path.basename(self.params["image_path"]))[0]
        filter_type = self.params["filter"]
        output_path = f"output/{base_name}_{filter_type}.jpg"
        
        # 如果需要，创建输出目录
        os.makedirs("output", exist_ok=True)
        
        return image, output_path
    
    async def exec_async(self, inputs):
        """保存图像。"""
        image, output_path = inputs
        
        # 模拟 I/O 延迟
        await asyncio.sleep(0.5)
        
        image.save(output_path)
        return output_path
    
    async def post_async(self, shared, prep_res, exec_res):
        """打印成功消息。"""
        print(f"已保存：{exec_res}")
        return "default"