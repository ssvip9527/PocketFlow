from PIL import Image
from utils.call_llm import client
from tools.pdf import image_to_base64

def extract_text_from_image(image: Image.Image, prompt: str = None) -> str:
    """使用OpenAI Vision API从图像中提取文本
    
    Args:
        image (PIL.Image): 要处理的图像
        prompt (str, optional): 用于提取的自定义提示。默认为通用OCR。
        
    Returns:
        str: 从图像中提取的文本
    """
    # 将图像转换为base64
    img_base64 = image_to_base64(image)
    
    # 通用OCR的默认提示
    if prompt is None:
        prompt = "请从该图像中提取所有文本。"
    
    # 调用Vision API
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
            ]
        }]
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    # 测试视觉处理
    test_image = Image.open("example.png")
    result = extract_text_from_image(test_image)
    print("提取的文本:", result)
