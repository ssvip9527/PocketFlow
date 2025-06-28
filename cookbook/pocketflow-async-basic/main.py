import asyncio
from flow import create_flow

async def main():
    """运行菜谱查找流程。"""
    # 创建流程
    flow = create_flow()
    
    # 创建共享存储
    shared = {}
    
    # 运行流程
    print("\nWelcome to Recipe Finder!")
    print("------------------------")
    await flow.run_async(shared)
    print("\nThanks for using Recipe Finder!")

if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main()) 