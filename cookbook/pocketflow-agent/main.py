import sys
from flow import create_agent_flow

def main():
    """处理问题的简单函数。"""
    # 默认问题
    default_question = "Who won the Nobel Prize in Physics 2024?"
    
    # 如果命令行提供了 --，则获取问题
    question = default_question
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            question = arg[2:]
            break
    
    # 创建代理流程
    agent_flow = create_agent_flow()
    
    # 处理问题
    shared = {"question": question}
    print(f"🤔 正在处理问题: {question}")
    agent_flow.run(shared)
    print("\n🎯 最终答案:")
    print(shared.get("answer", "No answer found"))

if __name__ == "__main__":
    main()