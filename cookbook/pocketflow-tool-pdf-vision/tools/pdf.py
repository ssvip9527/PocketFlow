import fitz  # PyMuPDF
from PIL import Image
import io
import base64
from typing import List, Tuple

def pdf_to_images(pdf_path: str, max_size: int = 2000) -> List[Tuple[Image.Image, int]]:
    """将PDF页面转换为PIL图像并限制大小
    
    Args:
        pdf_path (str): PDF文件路径
        max_size (int): 图像的最大尺寸（宽度/高度）
        
    Returns:
        list: (PIL图像, 页码)元组的列表
    """
    doc = fitz.open(pdf_path)
    images = []
    
    try:
        for page_num in range(len(doc)):
            page = doc[page_num]
            pix = page.get_pixmap()
            
            # 转换为PIL图像
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # 如果需要，在保持宽高比的同时调整大小
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            images.append((img, page_num + 1))
            
    finally:
        doc.close()
        
    return images

def image_to_base64(image: Image.Image) -> str:
    """将PIL图像转换为base64字符串
    
    Args:
        image (PIL.Image): 要转换的图像
        
    Returns:
        str: Base64编码的图像字符串
    """
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')
