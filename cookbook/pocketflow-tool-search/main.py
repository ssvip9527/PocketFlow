import os
from flow import create_flow

def main():
    """运行网络搜索流程"""
    
    # 从用户获取搜索查询
    query = input("Enter search query: ")
    if not query:
        print("错误：需要查询内容")
        return
        
    # 初始化共享数据
    shared = {
        "query": query,
        "num_results": 5
    }
    
    # 创建并运行流程
    flow = create_flow()
    flow.run(shared)
    
    # 结果在 shared["analysis"] 中
    
if __name__ == "__main__":
    main()
