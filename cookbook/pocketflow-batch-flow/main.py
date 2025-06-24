import os
from PIL import Image
import numpy as np
from flow import create_flow

def main():
    # 创建并运行流程
    print("正在处理带滤镜的图像...")
    
    flow = create_flow()
    flow.run({}) 
    
    print("\n所有图像处理成功!")
    print("请检查 'output' 目录以查看结果。")

if __name__ == "__main__":
    main() 