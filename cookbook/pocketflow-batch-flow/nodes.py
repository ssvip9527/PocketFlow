"""图像处理的节点实现。"""

import os
from PIL import Image, ImageEnhance, ImageFilter
from pocketflow import Node

class LoadImage(Node):
    """加载图像文件的节点。"""
    
    def prep(self, shared):
        """从参数中获取图像路径。"""
        return os.path.join("images", self.params["input"])
    
    def exec(self, image_path):
        """使用 PIL 加载图像。"""
        return Image.open(image_path)
    
    def post(self, shared, prep_res, exec_res):
        """将图像存储在共享存储中。"""
        shared["image"] = exec_res
        return "apply_filter"

class ApplyFilter(Node):
    """对图像应用过滤器的节点。"""
    
    def prep(self, shared):
        """获取图像和过滤器类型。"""
        return shared["image"], self.params["filter"]
    
    def exec(self, inputs):
        """应用指定的过滤器。"""
        image, filter_type = inputs
        
        if filter_type == "grayscale":
            return image.convert("L")
        elif filter_type == "blur":
            return image.filter(ImageFilter.BLUR)
        elif filter_type == "sepia":
            # 棕褐色实现
            enhancer = ImageEnhance.Color(image)
            grayscale = enhancer.enhance(0.3)
            colorize = ImageEnhance.Brightness(grayscale)
            return colorize.enhance(1.2)
        else:
            raise ValueError(f"未知过滤器: {filter_type}")
    
    def post(self, shared, prep_res, exec_res):
        """存储过滤后的图像。"""
        shared["filtered_image"] = exec_res
        return "save"

class SaveImage(Node):
    """保存处理后的图像的节点。"""
    
    def prep(self, shared):
        """获取过滤后的图像并准备输出路径。"""
        # 如果输出目录不存在则创建
        os.makedirs("output", exist_ok=True)
        
        # 生成输出文件名
        input_name = os.path.splitext(self.params["input"])[0]
        filter_name = self.params["filter"]
        output_path = os.path.join("output", f"{input_name}_{filter_name}.jpg")
        
        return shared["filtered_image"], output_path
    
    def exec(self, inputs):
        """将图像保存到文件。"""
        image, output_path = inputs
        image.save(output_path, "JPEG")
        return output_path
    
    def post(self, shared, prep_res, exec_res):
        """打印成功消息。"""
        print(f"已将过滤后的图像保存到: {exec_res}")
        return "default"