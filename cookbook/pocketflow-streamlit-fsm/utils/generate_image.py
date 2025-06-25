from openai import OpenAI
import os
import base64

def generate_image(prompt: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    
    image_b64 = response.data[0].b64_json
    print(f"生成的图像 ({len(image_b64)} 字符)")
    return image_b64

if __name__ == "__main__":
    test_prompt = "一只灰色虎斑猫抱着一只戴橙色围巾的水獭"
    print(f"正在为提示生成图像: {test_prompt[:50]}...")
    
    image_base64 = generate_image(test_prompt)
    print(f"成功！生成了 {len(image_base64)} 字符的 base64 数据")
    
    # 将图像写入本地文件进行测试
    image_bytes = base64.b64decode(image_base64)
    with open("test_generated_image.png", "wb") as f:
        f.write(image_bytes)
    print("测试图像已保存为 test_generated_image.png")