# main.py

from flow import create_tao_flow

def main():
    
    query = """I need to understand the latest developments in artificial intelligence"""
    
    # 创建共享数据
    shared = {
        "query": query,
        "thoughts": [],
        "observations": [],
        "current_thought_number": 0
    }
    
    # 创建并运行流
    tao_flow = create_tao_flow()
    tao_flow.run(shared)
    
    # 打印最终结果
    if "final_answer" in shared:
        print("\n最终答案:")
        print(shared["final_answer"])
    else:
        print("\n流未产生最终答案")

if __name__ == "__main__":
    main()