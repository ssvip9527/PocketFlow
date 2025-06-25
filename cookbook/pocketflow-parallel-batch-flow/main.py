import os
import asyncio
import time
from flow import create_flows

def get_image_paths():
    """获取 images 目录中现有图像的路径。"""
    images_dir = "images"
    if not os.path.exists(images_dir):
        raise ValueError(f"目录 '{images_dir}' 未找到！")
    
    # 列出 images 目录中的所有 jpg 文件
    image_paths = []
    for filename in os.listdir(images_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_paths.append(os.path.join(images_dir, filename))
    
    if not image_paths:
        raise ValueError(f"在 '{images_dir}' 目录中未找到图像！")
    
    print(f"找到 {len(image_paths)} 张图像：")
    for path in image_paths:
        print(f"- {path}")
    
    return image_paths

async def main():
    """运行并行图像处理示例。"""
    print("并行图像处理器")
    print("-" * 30)
    
    # 获取现有图像路径
    image_paths = get_image_paths()
    
    # 使用图像路径创建共享存储
    shared = {"images": image_paths}
    
    # 创建两个流
    batch_flow, parallel_batch_flow = create_flows()
    
    # 运行并计时批量流
    start_time = time.time()
    print("\n正在运行顺序批量流...")
    await batch_flow.run_async(shared)
    batch_time = time.time() - start_time
    
    # 运行并计时并行批量流
    start_time = time.time()
    print("\n正在运行并行批量流...")
    await parallel_batch_flow.run_async(shared)
    parallel_time = time.time() - start_time
    
    # 打印计时结果
    print("\n计时结果：")
    print(f"顺序批量处理：{batch_time:.2f} 秒")
    print(f"并行批量处理：{parallel_time:.2f} 秒")
    print(f"加速比：{batch_time/parallel_time:.2f} 倍")
    
    print("\n处理完成！请检查 output/ 目录以获取结果。")

if __name__ == "__main__":
    asyncio.run(main())