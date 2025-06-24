import os
from flow import create_flow

def main():
    """运行网页爬虫流程"""
    
    # 从用户获取网站 URL
    url = input("请输入要爬取的网站 URL (例如: https://example.com): ")
    if not url:
        print("错误: URL 是必需的")
        return
        
    # 初始化共享数据
    shared = {
        "base_url": url,
        "max_pages": 1
    }
    
    # 创建并运行流程
    flow = create_flow()
    flow.run(shared)
    
    # 结果在 shared["report"] 中
    
if __name__ == "__main__":
    main()
